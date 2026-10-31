# Vista — CC integration

**Exact archive file:** `vista-1.21.1-5.5.7-neoforge (1).jar`.

## Functionality and behavior

The ViewFinder provides camera orientation, zoom and lock controls; WaveGate exposes a configured URL string. Angle conventions, allowed zoom range and URL restrictions are not inferable from Java method signatures alone. These are separate peripheral types.

## Peripheral/class method index

| Java peripheral or API family | Declared method candidates |
| --- | --- |
| `ViewFinderPeripheral` | `getYaw(), setYaw(number), getPitch(), setPitch(number), setZoom(int), getZoom(), setLocked(boolean), isLocked()` |
| `WaveGatePeripheral` | `getUrl(), setUrl(string)` |

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
