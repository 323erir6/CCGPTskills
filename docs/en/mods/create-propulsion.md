# Create Propulsion — CC integration

**Exact archive file:** `createpropulsion-1.1.5.jar`.

## Functionality and behavior

The names show separate physical thrust, displayed thrust, air flow and fuel/energy. PN and KN are named force units in the source and are not interchangeable; use unit-consistent calculations. Normalized power methods must not be confused with raw integer power. Vector-thruster output and target vector are separate signals; do not assume instantaneous actuator response. Fluid and inventory methods follow their respective external capability contracts.

## Peripheral/class method index

| Java peripheral or API family | Declared method candidates |
| --- | --- |
| `ThrusterPeripheral` | `getObstruction(), setPower(int), setPowerNormalized(number), getPower(), getCurrentThrustPN(), getCurrentThrustKN(), getDisplayedThrustPN(), getDisplayedThrustKN(), getAirflowMs(), getFuelAmountMb(), getFuelCapacityMb(), tanks(), pushFluid(...), pullFluid(...)` |
| `CreativeThrusterPeripheral` | `getObstruction(), setPower(int), setPowerNormalized(number), getPower(), setThrustConfig(int), getThrustConfig(), getTargetThrustPN(), getTargetThrustKN(), getCurrentThrustPN(), getCurrentThrustKN(), getDisplayedThrustPN(), getDisplayedThrustKN(), getAirflowMs()` |
| `IonThrusterPeripheral` | `getObstruction(), setPower(int), setPowerNormalized(number), getPower(), getCurrentThrustPN(), getCurrentThrustKN(), getDisplayedThrustPN(), getDisplayedThrustKN(), getAirflowMs(), getEnergyAmountFe(), getEnergyCapacityFe()` |
| `SolidFuelThrusterPeripheral` | `getObstruction(), setPower(int), setPowerNormalized(number), getPower(), getCurrentThrustPN(), getCurrentThrustKN(), getDisplayedThrustPN(), getDisplayedThrustKN(), getAirflowMs(), getFuelAmount(), getFuelCapacity(), getBurnTimeRemaining(), isBurning(), list(), pushItems(...), pullItems(...)` |
| `VectorThrusterPeripheral` | `getVectorX(), getVectorY(), getTargetVectorX(), getTargetVectorY(), setVectorX(number), setVectorY(number), setVector(x,y), setThrust(number), setThrustNormalized(number), setPower(int), setPowerNormalized(number), getThrust(), getPower()` |
| `LiquidVectorThrusterPeripheral` | `all VectorThruster methods plus tanks(), pushFluid(...), pullFluid(...)` |
| `CreativeVectorThrusterPeripheral` | `setThrustOutput(number), clearThrustOutput(), getMaxThrustOutputPn(), isCustomThrustOutputActive()` |
| `TiltAdapterPeripheral` | `getLeftSignal(), getRightSignal(), setTargetAngle(number)` |
| `RedstoneTransmissionPeripheral` | `getTransmissionMode(), setTransmissionMode(...), getShiftLevel(), setShiftLevel(...)` |
| `StirlingEnginePeripheral` | `getRpm(), setSpeed(number), setActive(boolean)` |
| `CoralGeneratorPeripheral` | `getCoralAmountMb(), getCoralCapacityMb(), getEnergyAmountFe(), getEnergyCapacityFe()` |

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
