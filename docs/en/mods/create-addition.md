# Create Addition — CC integration

**Exact archive file:** `createaddition-1.7.0.jar`.

## Functionality and behavior

Direct CC implementations were found for motors, servos, digital adapters, accumulators and energy interfaces. Servo target angles are distinct from speed, and connection/motor state may constrain writes. The Digital Adapter is an adapter for nearby Create blocks rather than a universal controller. Read output values and input bounds before changing mechanisms. Exact angle units are implementation-dependent; verify using a known zero position.

## Peripheral/class method index

| Java peripheral or API family | Declared method candidates |
| --- | --- |
| `ElectricMotorPeripheral` | `setSpeed(number), stop(), getSpeed(), getStressCapacity(), getEnergyConsumption(), getMaxInsert(), getMaxExtract()` |
| `ServoMotorPeripheral` | `getSpeed(), setSpeed(number), getAngle(), getTargetAngle(), setTargetAngle(number), getMinAngle(), setMinAngle(number), getMaxAngle(), setMaxAngle(number), isAssembled(), assemble(), disassemble(), getEnergyConsumption()` |
| `DigitalAdapterPeripheral` | `clearLine(), clear(), print(string), getLine(), setLine(number), getMaxLines(), setTargetSpeed(name,number), getTargetSpeed(), getKineticStress(), getKineticCapacity(), getKineticSpeed(), getKineticTopSpeed(), getPulleyDistance(), getPistonDistance(), getBearingAngle(), getElevatorContraption(), getElevatorFloor(), hasElevatorArrived(), getElevatorFloors(), getElevatorFloorName(), gotoElevatorFloor(), getDurationAngle(), getDurationDistance()` |
| `ModularAccumulatorPeripheral` | `getEnergy(), getCapacity(), getPercent(), getMaxInsert(), getMaxExtract(), getHeight(), getWidth()` |
| `PortableEnergyInterfacePeripheral` | `getEnergy(), getCapacity(), isConnected(), getMaxInsert(), getMaxExtract()` |
| `RedstoneRelayPeripheral` | `getMaxInsert(), getMaxExtract(), getThroughput(), isPowered()` |

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
