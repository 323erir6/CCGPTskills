# Create Diesel Generators — CC integration

**Exact archive file:** `createdieselgenerators-1.21.1-1.3.15.jar`.

## Functionality and behavior

ChemicalTurretPeripheral exposes rotation and spray operations. Java signatures specify integer inputs for rotation setters; exact angle units, allowed values and spray prerequisites require in-game validation. Do not treat this as equivalent to CBC's cannon mounts.

## Peripheral/class method index

| Java peripheral or API family | Declared method candidates |
| --- | --- |
| `ChemicalTurretPeripheral` | `getHorizontalRotation(), getVerticalRotation(), setHorizontalRotation(int), setVerticalRotation(int), spray()` |

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
