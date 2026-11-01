# GOCODE: functional blocks of the 6.9.3 modpack (headless)

**Target versions verified by inspecting the exact installed JARs:** Minecraft 1.21.1 NeoForge, Create 6.0.10, Create: Aeronautics 1.3.2 (bundled), Create: Simulated 1.3.2 (nested inside Aeronautics), Create Propulsion: Simulated 1.1.5, Synaxis 1.5.0, SynaxisPlus 1.0.5, NeoPeripheral 1.4ve, Aeroworks 1.5.0 and AeroEngineering 1.3.0. Further patches in the pack can modify real runtime behavior. The catalog records the actual filenames, SHA-256 and available block IDs; no JAR binaries are committed. A full RAR inventory contains 218 top-level and embedded JAR layers, with 11,149 distinct block IDs; 51 have registered test models.

## Execution chain

`Create / Photomancy .nbt` → `agent.sim.schematics.load` → versioned block states, palette, block entity NBT → `Compound` with each block's collision boxes → `World(profile='sable-2.0.5')` → `ModRuntime.load_schematic` → mod devices → 40Hz physics callback → `peripheral.call` commands → text-only JSON snapshots.

**Important:** successfully importing a block state is not proof the block's gameplay is supported. `mod_devices_manifest.json.gz` lists exactly what has an adapter versus unsupported blocks. Missing shape, mass, engine ratings, resource consumption or sublevel linkage are surfaced as `unresolved` diagnostics; they are not silently assigned plausible-looking constants.

## Real behavioral adapters

| Mod | Block(s) | What executes | Fidelity |
|---|---|---|---|
| Create Propulsion 1.1.5 | thruster, ion, creative, vector, liquid-vector, creative-vector, solid fuel | CC power and vector methods, priority of peripheral over redstone, FE/fuel bookkeeping, force applied at block location, torque | Verified method names and selected bytecode formulas; throttle dynamics and fuel rates approximated/configurable |
| Create Propulsion 1.1.5 | reaction wheel, tilt adapter, redstone transmission | configured torque, tilt target, transmission settings | Approximate physics / state-only |
| Aeronautics 1.3.2 | wooden/andesite/smart propeller | rpm ramp and thrust: `config_thrust × direction_independent_speed`; source-default thrust coefficient `1.0` | Scalar thrust formula and 0.15 tick smoothing from bundled JAR; force application approximate |
| Aeronautics 1.3.2 | propeller bearing, gyroscopic bearing | `thrust = sail_power^1.5 × speed × 0.2`, source-default coefficient | Formula verified; sail count/assembly and gyroscopic mechanics need explicit state / native port |
| Aeronautics 1.3.2 | adjustable burner, steam vent | configurable buoyancy/force actor | Explicit-input approximation, not combustion model |
| Synaxis 1.5.0 | dynamic joint/revolute motor | `setTarget` radians; `setPID`, gain readouts; angle/speed test state | CC contract verified in NeoPeripheral 1.4ve; joint solver is approximate |
| Synaxis 1.5.0 | jet, compact flap, anchor, resistor, hydraulic actuator, propeller, jet rudder | CC getters/setters where verified; configurable force/state tests | Approximate mechanical or state-only |
| Synaxis 1.5.0 | Cimulink PID controller | deterministic generic PID test state | Generic PID; NOT original Cimulink backend |
| Create: Simulated 1.3.2 | swivel bearing; analog transmission; 16 colored portable engines | verified read-only bearing API; configuration/signal/RPM state | Control state only; no actual Create stress/gear/kinetic graph |
| Aeroworks 1.5.0 | mechanical/stepper servo | deterministic target travel state | Approximation |
| AeroEngineering 1.3.0 | missile thruster, engine propeller, airflow nozzle | configurable force actor | Approximation requiring explicit max force and assembly |
| Create 6.0.10 | rotation speed controller | requested RPM test state | Approximation; no kinetic network stress solver |

### Details validated directly in source/bytecode

- `ThrusterTorqueMath.netTorqueAbout` computes **`sum((point - center) × force)`**. The test World now applies each active propulsion force at its actual schematic-local block position (transformed into world coordinates) and updates angular velocity using the compound's inertia approximation.
- `AtmosphericThrustMath.calculateFactor` and `IonThrusterEnergyMath.poweredFraction` are reimplemented as standalone numeric functions and unit-tested against bytecode paths.
- Aeronautics `BasePropellerBlockEntity.getThrust()` multiplies configured thrust by directional speed, and `PropellerBearingBlockEntity.getThrust()` uses `totalSailPower^1.5`. Aeronautics `KineticBlockEntity.convertToAngular` is `rpm × 360 / 60 / 20 = rpm × 0.3` in the bundled Create 6.0.10 JAR.
- In NeoPeripheral's `DynamicMotorPeripheral`, the **actual case-sensitive method is `GetTarget`**, not `getTarget`. In `JetPeripheral` the actual setter is **`setTrust`** (the mod's spelling), not `setThrust`. The simulator preserves these signatures.
- The **actual** complete behavior of Synaxis motor constraint controllers, propeller aerodynamic drag, Sable contact solver, Create kinetic transmission and fuel inventory transfers has **not** been ported.

## Quick start

From repository root:

```bash
python3 -m unittest discover -s agent/tests -p 'test_*.py'
python3 -m agent.sim.mod_cli agent/scenarios/mod_blocks.json --out agent-results/mod_blocks.json
```

Use a real schematic with a plan that supplies mass/placement/physical input:

```bash
python3 -m agent.sim.mod_cli agent/scenarios/mod_blocks.json --schematic path/to/ship.nbt --out agent-results/ship.json
```

**Note:** `--schematic` replaces the scenario's sample normalized construction. Device command keys are derived from the real file's block IDs and positions; an unrelated schematic requires a corresponding JSON command list.

A JSON scenario can issue `advance` (game ticks), `call` (verified CC peripheral method name), `attach`, `detach`, `redstone` and `rpm`. Returned JSON contains physical body states, each device's instantaneous world-space force and torque, CC command logs, and `unresolved` flags. A test should assert expected numerical invariants and fail if unverified parameters are required.

Runtime API examples:

```python
from agent.sim.rigid import World
from agent.sim.mod_runtime import ModRuntime
from agent.sim.schematics import load

runtime = ModRuntime(World(profile="sable-2.0.5"))
ids = runtime.load_schematic(load("airship.nbt"), masses={"0":500},
    device_config={"createpropulsion:creative_thruster":{"max_thrust_pn":10000}})
for key,device in runtime.devices.items():
    print(key, device.cc_type, device.methods())
print(runtime.advance(20)["devices"])
```

## Engineering limitations

This is an **agent test double**, not a Minecraft server. Correct version-specific method contracts are mixed with **explicitly approximate** force/thermal/aerodynamic/state models. Block entities are retained but their arbitrary NBT schemas are **not** completely decoded. `functional_blocks` and physics world are Python, while the isolated mock CraftOS computer runner is Lua; cross-language in-game scheduling is not yet unified. Do not claim native mod equivalence without matching live-game traces and native collision/constraint code. The JSON manifest includes unsupported blocks so GOCODE can prioritize them from real test cases.

### Full RAR inventory and manifest v2

`agent/scripts/catalog_modpack_rar.py` scans **all** the user-provided RAR's JARs (including nested jarjar dependencies) with system `libarchive` and standard `zipfile`. It hashes each JAR and records every `assets/<modid>/blockstates/*.json` resource. The output is `agent/sim/mod_devices_manifest.json.gz`: the array `blockstates` holds `[block_id, artifact_index,...]`, while `device_models` maps only supported device IDs to implementation classes. The remaining IDs are explicitly **not modeled**. No Minecraft source classes or native physics libs are included.

```bash
python3 -m agent.scripts.catalog_modpack_rar /path/to/modpack.rar --out agent/sim/mod_devices_manifest.json.gz
```

Version-specific contracts are extracted via `javap` from the actual JARs and manually represented in the test adapters. The current simplified dynamics are deliberately not full native equivalents; physical control validity can only be established with captured in-game reference trajectories.
