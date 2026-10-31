# Tom's Peripherals — CC integration

**Exact archive file:** `toms-peripherals-1.21-1.3.1.jar`.

## Functionality and behavior

Tom's GPU is not a vanilla terminal and not CC:AR. Its methods are dispatched dynamically by ITMPeripheral; simple javap of the outer class cannot enumerate all Lua methods in nested GPU peripheral classes. **Never synthesize setSize, sync, draw or mouse-event signatures from memory.** Run the generic peripheral inspector on the exact device and capture a minimal command/return example for each method. Scheduling may stay on CC's Minecraft-tick queue even when Sable CC Tick Sync accelerates Lua.

## Peripheral/class method index

| Java peripheral or API family | Declared method candidates |
| --- | --- |
| `GPU peripheral / monitor` | `GPUBlockEntity.GPUPeripheral, dynamic ITMPeripheral and ITMLuaObject dispatch; discover method names through peripheral.getMethods()` |
| `Keyboard` | `KeyboardBlockEntity emits event callbacks; input is not the same as vanilla terminal key events` |
| `Redstone port` | `RedstonePortBlockEntity provides per-side and bundled signals through its wrapped peripheral` |
| `Watchdog timer` | `WatchDogTimerBlockEntity exposes watchdog state and time limits through its peripheral` |
| `Other devices` | `Modem and monitor providers use the mod's own peripheral adapter` |

## On-device verification

```lua
for _,name in ipairs(peripheral.getNames()) do
  local methods=peripheral.getMethods(name) or {}
  table.sort(methods)
  print(name,peripheral.getType(name))
  print(table.concat(methods,", "))
end
```

This program is read-only and requires no additional API besides CC:Tweaked.

## Evidence and limits

Method names are extracted from Java classes of the **exact installed JAR** with `javap`. A class method is not proof of Lua visibility: annotations, generic adapters, wrapped block entities, runtime flags and other mods determine exposed interfaces. The table includes **method candidates** and deliberately omits Java internals such as constructors, `getType`, `equals`, `getTarget` and `attach`. Method return shapes must be inspected on-device. All nontrivial actuator behavior needs testing on the target build.
