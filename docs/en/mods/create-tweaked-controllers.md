# Create Tweaked Controllers — CC integration

**Exact archive file:** `create_tweaked_controllers-1.21.1-1.2.7.jar`.

## Functionality and behavior

Button and axis IDs correspond to the connected controller mapping, not a universal keyboard layout. getButton returns a state for an indexed button; getAxis returns a numeric axis state. Boundaries and mappings depend on configured input device. Full-precision mode changes reporting granularity, not the physical accuracy of a controller. This peripheral is unrelated to the vanilla CC keyboard events.

## Peripheral/class method index

| Java peripheral or API family | Declared method candidates |
| --- | --- |
| `TweakedLecternPeripheral` | `hasUser(), getUserUUID(), getButton(int), getAxis(int), setFullPrecision(boolean), isFullPrecision()` |

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
