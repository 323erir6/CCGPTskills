# Sable CC Tick Sync 1.6.4

**Source:** [Sable-CC-Tick-Sync](https://github.com/323erir6/Sable-CC-Tick-Sync), commit `32ed09ce8e8944ee20b3787b547971617003fafb`. API from `SableSyncApi.java`, scheduling from `HighFrequencyController.java`, `PhysicsPeripheralDispatch.java` and Mixins.

## Exact Lua API

A global `sableSync` API is registered with two read-only functions:

| Method | Arguments | Returns |
| --- | --- | --- |
| `sableSync.isHighFrequency()` | none | boolean: computer is registered as accelerated |
| `sableSync.getPhysicsFrequency()` | none | number: physics substeps per second (0 before a valid recorded timestep) |

The historical `sableSync.setHighFrequency()` **was removed**. There is no per-program switch. The add-on accelerates all CC computers automatically when its runtime integration is active.

```lua
assert(type(sableSync)=="table","Tick Sync API not installed")
print("Accelerated:",sableSync.isHighFrequency())
print("Physics frequency:",sableSync.getPhysicsFrequency(),"Hz")
```

## Scheduling model

- Lua worker/executor work follows real Sable physics substeps.
- CC timers, Redstone polling and tick-bound state keep their 20 TPS game-time semantics.
- Original Minecraft tick processing still handles attachment, external events and other CC work reliably; a matched substep is skipped to avoid counting it twice.
- Main-thread peripheral actions can be processed on a bounded physics-step queue when eligible.
- Built-in peripherals and Tom's GPU/monitor operations stay in the 20 TPS main-thread queue when required by their backing state.
- Peripherals with unsafe direct native Rapier calls are rerouted through the optimized bounded queue, rather than called from arbitrary Lua worker threads.

## Current source queue limits

From `HighFrequencyController.java`:

| Constant | Value | Meaning |
| --- | ---: | --- |
| `MAX_PENDING_FAST_TASKS` | 4096 | Pending tasks per registered computer state |
| `MAX_TASKS_PER_SUBSTEP` | 1024 | Global maximum tasks served per substep |
| `MAX_TASK_TIME_PER_SUBSTEP_NANOS` | 2,000,000 | Global time budget: 2 ms/substep |

The queue is cooperatively serviced; **this is not a guarantee** that arbitrary peripheral calls execute synchronously at each substep. Overflow can reject acceleration, and unrelated work still has an independent schedule.

## Controller design notes

A program that calls `sleep(0)` in an unlimited loop is not guaranteed to run every physics substep. Do not assume `sleep(0.001)` means 1000 Hz. Sample actual state timing, obtain the effective frequency from `sableSync`, and derive control-loop `dt` from real observation where possible. Do not multiply impulses by an assumed rate without checking their units and actuator semantics.

## Diagnostics

Run `print(sableSync.getPhysicsFrequency())` after simulation starts, inspect server tick timings and follow the repo's `gradlew regressionTest` for thread dispatch/backpressure tests. These tests do not replace multiplayer load profiling.

**Compatibility:** Minecraft 1.21.1 / NeoForge, Sable 2.0.5, CC:Tweaked 1.120.0 (source README). Verify loaded versions before applying scheduling assumptions.

**No additional peripheral methods** beyond the global `sableSync` API are declared by the add-on; it also changes scheduling of other peripherals internally.