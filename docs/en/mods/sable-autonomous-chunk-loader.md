# Sable Autonomous Chunk Loader 1.8.1 — indirect CC integration

**Installed:** `sable-autonomous-chunk-loader-1.8.1.jar`; older 1.7.9 and 1.8.0 entries are **disabled**. [Repository](https://github.com/323erir6/Sable-Autonomous-Chunk-loader) has older source history.

## CC/Tweaked impact

A bytecode scan identifies CC references in Mixin/integration code, but no separately declared `ILuaAPI` or direct `@LuaFunction` peripheral. The project includes a NeoPeripheral radar compatibility path and server-side stable Sable pose/chunk-tracking logic. Its radar Mixin can override/extend the existing `scanForSubLevels` implementation, and the Enhanced Detector Radar code explicitly defers to it when present.

**API ownership:** existing `neoperipheral` radar. Inspect the actual returned table at runtime for fields such as `velocity_x/y/z`, `size_x/y/z`, stable position and quaternion components. Do not call `chunkLoader.getPosition()` or other imagined functions.

## Consistency requirements

- Never mix relative radar `x,y,z` with absolute CC:Sable `pose.position`.
- If player/ship radar filters depend on loaded chunks, test under a high-speed/high-altitude test scenario.
- This mod may change data consistency and chunk residency without changing the actual Lua method name.
- Disabled JARs do not create active APIs.
- Record exact active version **1.8.1** rather than relying on old GitHub `gradle.properties`.

See [Enhanced Detector Radar](enhanced-detector-radar.md) and [NeoPeripheral API](neoperipheral.md).