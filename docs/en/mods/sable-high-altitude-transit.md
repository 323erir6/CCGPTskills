# Sable High Altitude Transit 1.3.5

**Mod:** [Sable-High-Altitude-Transit](https://github.com/323erir6/Sable-High-Altitude-Transit), `gradle.properties: mod_version=1.3.5`, source commit `f3330cbca139f6e62154c04cb05df22e225810bf`.

## CC:Tweaked API status

**No new Lua API, ILuaAPI or IPeripheral interface was found in the reviewed source tree.** The mod changes Sable's server-side physics/chunk residency and therefore affects the *environment* in which CC programs run, without adding a new peripheral type.

## Behavior relevant to CC programs

- For physical constructions traveling high above terrain, physics integration continues without vanilla ground-chunk loading under the object.
- The default transit threshold uses world Y=400 for the *lowest point* of the body. Dimensions with lower build ceilings use a corresponding threshold above the ceiling; check the installed implementation and server configuration.
- While in high transit, Sable physics, control inputs, player transport and construction tracking continue.
- Terrain simulation resumes when a construction descends.
- The mod changes chunk ticket decisions and optimizes empty-sky reads; it is not a generic patch that treats **every** unloaded chunk as air.
- Telemetry from `CC:Sable`, `NeoPeripheral sable_engine`, and radar peripherals should still be treated as the relevant source of position, speed and orientation.

## Diagnostic procedure

1. Record `sublevel.getLogicalPose()` and `sublevel.getVelocity()` from a CC:Sable-enabled computer.
2. Verify that the body remains moving while its lowest bound is above the threshold.
3. Compare server logs with the `[Transit perf]` instrumentation described in the upstream README.
4. Test descending into actual generated terrain; do not infer collision behavior from unloaded regions.
5. Do not assume high altitude implies coordinate precision, constant tick frequency or zero lag.

**API owner:** CC:Sable/NeoPeripheral provides the Lua interface; High Altitude Transit provides the environment modification. **Do not invent** `highAltitudeTransit.*` functions.