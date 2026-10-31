# Create Radar — CC integration

**Exact archive file:** `create_radar-0.4.4-1.21.1.jar`.

## Functionality and behavior

These are CC generic peripheral methods with Java block-entity arguments automatically supplied by the adapter. Thus Lua calls do not pass the Java BlockEntity as an argument. Radar tracking tables may contain mod-defined fields; dump a real return value before relying on keys. Numeric angles must be tested against actual motor orientation and mechanical limits. A fire controller and radar bearing are different peripheral types.

## Peripheral/class method index

| Java peripheral or API family | Declared method candidates |
| --- | --- |
| `PlaneRadarPeripheral` | `getTracks(), getPosition(), getRange()` |
| `RadarBearingPeripheral` | `getTracks(), getPosition(), getRotation(), getRotationSpeed(), getRange(), getDishCount()` |
| `MonitorPeripheral` | `getSelectedTrackId(), getTracks(), getSelectedTrack()` |
| `FireControllerPeripheral` | `isPowered(), fireOn(), fireOff(), setPowered(boolean), keepFiring()` |
| `YawControllerPeripheral` | `setAngle(number), getAngle(), stopAuto()` |
| `PitchControllerPeripheral` | `setAngle(number), getAngle(), stopAuto()` |

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
