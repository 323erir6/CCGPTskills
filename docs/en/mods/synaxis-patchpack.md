# Synaxis Patchpack — CC integration

**Exact archive file:** `synaxis_patchpack-1.0.0.jar`.

## Functionality and behavior

The code uses CC generic peripherals and Mixins to extend NeoPeripheral camera/motor objects. Return maps may hold runtime state vs stored configuration separately; do not conflate getMotorRuntime with getMotorSettings. getCurrentAngleDegrees explicitly declares degrees, whereas getCurrentAngle must be checked for its own unit. The installed version is 1.0.0, and public source repository has not been verified for this particular patchpack.

## Peripheral/class method index

| Java peripheral or API family | Declared method candidates |
| --- | --- |
| `SynaxisCameraScopePeripheral` | `getScopeSettings(), setScopeSettings(table), getScopeOffset(), setScopeOffset(x,y,z), getScopeYawLimits(), setScopeYawLimits(min,max), getScopePitchLimits(), setScopePitchLimits(min,max), getScopeMaxYawSpeed(), setScopeMaxYawSpeed(number), getScopeMaxPitchSpeed(), setScopeMaxPitchSpeed(number), setScopeMaxSpeed(yaw,pitch), getScopeZoomSpeed(), setScopeZoomSpeed(number), isScopeSlidingEnabled(), setScopeSlidingEnabled(boolean)` |
| `SynaxisDynamicMotorPeripheral` | `getMotorSettings(), getMotorConfig(), getMotorRuntime(), getMotorOffsets(), getCurrentAngle(), getCurrentAngleDegrees(), getCurrentSpeed(), getAppliedTorque(), isMotorConnected(), isMotorLockActive(), isMotorAutoLockActive()` |

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
