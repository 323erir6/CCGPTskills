# Installed peripheral API inventory

**Pack:** Minecraft 1.21.1, CC:Tweaked 1.120.0, NeoForge; derived from the exact audited JAR archive and selected up-to-date source repositories. This index links to **independent English documentation files**.

## Coverage table

| Mod/add-on | Reference | CC impact |
| --- | --- | --- |
| CBC Programmable Fuzes | [Read](./cbc-programmable-fuzes.md) | 22 Java-source-confirmed methods; fuze telemetry and cannon inspection |
| Enhanced Detector Radar | [Read](./enhanced-detector-radar.md) | Adds radar fields, precision and engine snapshot calls |
| Sable CC Tick Sync | [Read](./sable-cc-tick-sync.md) | Global sableSync API and scheduling |
| CC:Sable | [Read](./cc-sable.md) | Global pose and aerodynamics APIs |
| NeoPeripheral | [Read](./neoperipheral.md) | Radars, Sable Engine, CBC mounts, Synaxis control |
| Advanced Peripherals | [Read](./advanced-peripherals.md) | Player Detector and related peripherals |
| Create | [Read](./create.md) | Native Create computer integrations |
| Create Addition | [Read](./create-addition.md) | Motor, servo, accumulator and digital adapter |
| Create Propulsion | [Read](./create-propulsion.md) | Thrusters, vectored propulsion and power systems |
| Create Radar | [Read](./create-radar.md) | Radar, controller and tracking peripherals |
| Create Tweaked Controllers | [Read](./create-tweaked-controllers.md) | User-controller axes and buttons |
| Create Diesel Generators | [Read](./create-diesel-generators.md) | Chemical turret peripheral |
| CC:AR | [Read](./cc-ar.md) | Augmented reality 2D/3D controller |
| Tom's Peripherals | [Read](./toms-peripherals.md) | GPU/monitor/keyboard and dynamic peripheral API |
| Vista | [Read](./vista.md) | ViewFinder and WaveGate |
| Synaxis Patchpack | [Read](./synaxis-patchpack.md) | Camera scope and dynamic motor extras |
| Bits n Bobs | [Read](./bits-n-bobs.md) | Headlamp peripheral |
| Mianbao Sable Explosion Compat | [Read](./mianbao-sable-explosion-compat.md) | Explosive peripheral |
| CBC Realistic Ballistics | [Read](./cbc-realistic-ballistics.md) | Indirect ballistics, no direct Lua API |
| Sable High Altitude Transit | [Read](./sable-high-altitude-transit.md) | No Lua methods, affects physical environment |
| CBC Aero Velocity Fix | [Read](./cbc-aero-velocity-fix.md) | No Lua methods |
| Sable Autonomous Chunk Loader | [Read](./sable-autonomous-chunk-loader.md) | Indirect radar behavior |
## Verification statuses

- **Java-source-confirmed:** concrete methods and parameter types extracted from the relevant source.
- **JAR bytecode-confirmed:** method names/classes detected in the installed release; not all necessarily exported into Lua.
- **Indirect integration:** the mod changes physical or scheduler behavior without registering a new Lua function.
- **Runtime-confirmed:** only when a test on an actual CC:Tweaked computer validates the method; this document does not claim such testing.

See [all 143 archive entries](../modpack-audit.md) for exact filenames, disabled files and bytecode-reference status. Use [`inspect_peripherals.lua`](../../../examples/inspect_peripherals.lua) to obtain a definitive runtime method list.