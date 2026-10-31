# Create (base mod) — CC integration

**Exact archive file:** `create-1.21.1-6.0.10.jar`.

## Functionality and behavior

The base Create 6.0.10 JAR contains ComputerCraft-compatible class references. Many integrations are generic-peripheral providers or Lua-exposed block capabilities rather than a one-to-one peripheral class with the same name as a block. The exact exposed method set depends on each placed block's compatible adapter. This reference identifies integration families; use the runtime peripheral inspector to get the definitive interface.

## Peripheral/class method index

| Java peripheral or API family | Declared method candidates |
| --- | --- |
| `Kinetic gauges and motors` | `SpeedGaugeBlockEntity, StressGaugeBlockEntity, CreativeMotorBlockEntity, SpeedControllerBlockEntity, SequencedGearshiftBlockEntity` |
| `Display and logistics` | `DisplayLinkBlockEntity, NixieTubeBlockEntity, PackagerBlockEntity, RepackagerBlockEntity, StockTickerBlockEntity, RedstoneRequesterBlockEntity` |
| `Railway and machinery` | `TrackObserverBlockEntity, StationBlockEntity, SignalBlockEntity, StickerBlockEntity, Portable interfaces` |
| `ComputerCraft bridge` | `AbstractComputerBehaviour and Lua objects for package/order data` |

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
