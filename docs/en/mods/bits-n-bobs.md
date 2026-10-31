# Bits n Bobs — CC integration

**Exact archive file:** `bits_n_bobs-2.3.5.jar`.

## Functionality and behavior

A CC-integrated Headlamp peripheral exists. The method `setLamp` is visible in its Java implementation; its Lua signature and whether the lamp state applies to a wearable, device, or block depend on registered adapter semantics. A Java `ILuaContext` parameter is injected by CC and must **not** be passed as a Lua argument. Inspect `peripheral.getMethods` and validate with a low-risk visual test.

## Peripheral/class method index

| Java peripheral or API family | Declared method candidates |
| --- | --- |
| `HeadlampPeripheral` | `setLamp(luaContext, brightness:int, ...) — Java declaration includes injected CC context` |

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
