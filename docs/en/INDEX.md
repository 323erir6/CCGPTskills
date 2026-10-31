# CC:Tweaked development — English offline reference

This independent English documentation tree targets the **audited Minecraft 1.21.1 / NeoForge modpack**. All source-backed declarations come from Java repositories, installed JAR bytecode, or official CC:Tweaked documentation. The exact build versions and evidence level are recorded; uncertain information is explicitly labeled.

## Core CraftOS

[Getting started](getting-started.md) · [Core APIs](core-apis.md) · [Events](events.md) · [Networking](networking.md) · [Peripheral discovery](peripherals.md) · [Mathematics and control](maths-and-control.md) · [UI and input](ui-and-input.md) · [Turtles and inventories](turtles-and-inventories.md) · [Reliability](reliability.md) · [Testing and deployment](testing-and-deployment.md)

## Mod-specific API books

[Advanced Peripherals 0.7.61b](mods/advanced-peripherals.md) · [Create Addition](mods/create-addition.md) · [Create Propulsion](mods/create-propulsion.md) · [Create Radar](mods/create-radar.md)

| Book | API scope |
| --- | --- |
| [CBC Programmable Fuzes](mods/cbc-programmable-fuzes.md) | 22 source-confirmed Lua functions and return tables |
| [Enhanced Detector Radar](mods/enhanced-detector-radar.md) | Precision, radar fields, engine physics snapshots |
| [Sable CC Tick Sync](mods/sable-cc-tick-sync.md) | `sableSync`, tick domains and limitations |
| [CC:Sable](mods/cc-sable.md) | Pose, local/world transforms, velocity, Euler orientation |
| [NeoPeripheral](mods/neoperipheral.md) | Sable engine, radars, CBC, Synaxis peripherals |
| [Installed peripheral inventory](mods/installed-peripherals.md) | Other available CC add-on APIs |
| [Mianbao Sable Explosion Compat](mods/mianbao-sable-explosion-compat.md) | `explosive` peripheral |
| [CBC Realistic Ballistics](mods/cbc-realistic-ballistics.md) | Compatibility and explicit lack of direct CC APIs |
| [Sable High Altitude Transit](mods/sable-high-altitude-transit.md) | Physics/chunk changes without new Lua APIs |
| [CBC Aero Velocity Fix](mods/cbc-aero-velocity-fix.md) | Physics patch without new Lua APIs |
| [Sable Autonomous Chunk Loader](mods/sable-autonomous-chunk-loader.md) | Indirect radar behavior |
| [Complete audited pack manifest](modpack-audit.md) | Every installed/disabled JAR and CC reference scan |

## Coding-agent engineering tools

[Automated checks, offline peripheral mocks, API manifests and benchmark framework](gocode-agent.md).

## Source and test status

Documentation based on [CCGPTskills](https://github.com/323erir6/CCGPTskills), the referenced source repositories and archived mod binaries. Java bytecode presence can prove an integration reference, but **cannot prove all public methods are callable from Lua**. Only `@LuaFunction` / explicit dispatch and runtime `peripheral.getMethods` do that.

Shared Lua modules under `lib/` are language-neutral executables. Their numeric regression tests are **not** evidence that peripherals have been physically tested. No proprietary third-party library is silently bundled.

## Examples

- [CC:Sable world position](../../examples/sublevel_world_position.lua), [orientation](../../examples/sublevel_attitude.lua), [speedometer](../../examples/sublevel_speedometer.lua)
- [Generic peripheral inspector](../../examples/inspect_peripherals.lua)
- [Generic networking examples](../../examples/README.md)

For Russian documentation, use [the fully separate Russian index](../ru/INDEX.md).