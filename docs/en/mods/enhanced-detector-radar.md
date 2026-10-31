# Enhanced Detector Radar 1.0.5 — API changes

**Source:** [repository](https://github.com/323erir6/Enhanced-Detector-Radar), source commit `e14b41b64a0d28871d69ec0bb51a2ee2a2ba1043`. Reviewed the three Mixin classes in `src/main/java/dev/radarcompat/enhanceddetector/mixin/`. This add-on **modifies existing peripheral APIs** rather than registering a separate radar peripheral.

## Advanced Peripherals Player Detector

`getPlayerPos(username[,precision])` and its alias `getPlayer(username[,precision])` retain the underlying API. Omitting the optional precision defaults to **3 decimal digits**, replacing the original default. Explicit precision retains the original behavior and restrictions. The code patches the `IArguments.optInt(0, default)` call; it does **not** turn all source data into physically precise positions.

For Minecraft 1.21.1, Advanced Peripherals uses the type `player_detector` (older versions: `playerDetector`). A response can be `nil` when the player is offline, out of range, or in a disallowed dimension.

```lua
local detector = peripheral.find("player_detector") or peripheral.find("playerDetector")
assert(detector, "Player Detector missing")
for _, name in ipairs(detector.getOnlinePlayers()) do
  local pos = detector.getPlayerPos(name)
  if pos and pos.x and pos.y and pos.z then
    print(("%s: %.3f %.3f %.3f"):format(name,pos.x,pos.y,pos.z))
  end
end
```

## NeoPeripheral Radar: `scanForSubLevels(radius[,absolute])`

The add-on injects into `RadarPeripheral.scanForSubLevels`. It retains the original radius rules and creative/normal behavior. Default radius: 16 in creative, otherwise NeoPeripheral `Config._RADAR_DEFAULT_RANGE`; a normal radar radius is clamped between 16 and `Config._RADAR_RANGE_LIMIT`. Absolute coordinates are accepted only when the radar is creative and `absolute=true`.

**Result:** 1-based array of rows. Original properties: `id` (UUID table), optional `name`, `x`, `y`, `z`, `distance`, `q_x`, `q_y`, `q_z`, `q_w`. Added by this mod:

| Key | Type | Coordinate system | Details |
| --- | --- | --- | --- |
| `velocity_x` | number | world X | `subLevel.latestLinearVelocity.x` |
| `velocity_y` | number | world Y | `subLevel.latestLinearVelocity.y` |
| `velocity_z` | number | world Z | `subLevel.latestLinearVelocity.z` |
| `size_x` | number | local body | plot bounding-box width |
| `size_y` | number | local body | plot bounding-box height |
| `size_z` | number | local body | plot bounding-box length |

Non-finite velocity components become 0. **Important:** for normal radar the reported `x,y,z` are approximate **radar-relative deltas with error**, not guaranteed absolute world positions. The error magnitude scales with distance / π³. Unlike position output, velocity is a world-axis vector.

**Compatibility precedence:** when `sable_autonomous_chunk_loader` is installed, this mixin leaves `scanForSubLevels` to the chunk-loader mod's implementation instead of overriding it; verify the final field set with `textutils.serialize`.

```lua
local radarName = "your_radar_name"
local radar = assert(peripheral.wrap(radarName), "Radar missing")
assert(type(radar.scanForSubLevels) == "function", "Wrong peripheral")
for _, body in ipairs(radar.scanForSubLevels(256,false) or {}) do
  local vx,vy,vz = body.velocity_x,body.velocity_y,body.velocity_z
  if type(vx)=="number" and type(vy)=="number" and type(vz)=="number" then
    local speed = math.sqrt(vx*vx+vy*vy+vz*vz)
    print(body.name or "unnamed",("speed %.2f b/s"):format(speed))
  end
end
```

## NeoPeripheral Sable Engine

The add-on replaces NeoPeripheral's shared call limiter with `EmptyCallLimiter` on engine-peripheral initialization. The original `sable_engine.enable` still controls whether the device is available. Config options `sable_engine.max_rate` and `rate_window` no longer limit these calls.

Three `@LuaFunction` methods are added to the existing `sable_engine` peripheral:

- `getPhysicsState() -> table | nil`: reads one coherent physics-state snapshot.
- `applyControlImpulse(linearX,linearY,linearZ,angularX,angularY,angularZ) -> boolean`: applies world-axis linear and angular impulses together.
- `stepControl(linearX,linearY,linearZ,angularX,angularY,angularZ) -> table | nil`: applies impulses and returns a coherent state in one call. May return `nil` when no valid body exists.

**State fields:** `x,y,z` position, `qx,qy,qz,qw` quaternion, `vx,vy,vz` linear velocity, `wx,wy,wz` angular velocity, `mass`. The calls reject non-finite impulse components. In Lua, remember **underscored radar quaternion keys `q_w`** are different from **engine state `qw`**. These are *impulses*, not force-per-second commands; check physical units and operating range before controlling real contraptions.

```lua
local engine = assert(peripheral.find("sable_engine"), "Sable engine missing")
local state = engine.getPhysicsState()
if state then
  print(("pos=%.2f,%.2f,%.2f mass=%.2f"):format(
    state.x, state.y, state.z, state.mass))
end
```

This read-only example avoids changing physical state.

## Failure modes and validation

- Absent methods: wrong mod version or another Mixin overrides the same method.
- `scanForSubLevels` only returns visible bodies intersecting the requested search region; unloaded/unknown state is not guaranteed.
- High frequency requires compatible tick scheduling; removing a limiter does not guarantee constant TPS.
- Verify radar coordinate system before map overlays.
- If a motor/engine is missing a sublevel, `getPhysicsState` returns `nil`.
- Use `peripheral.getMethods(name)` to confirm all methods in the loaded pack.

**Evidence:** [PlayerDetectorPrecisionMixin.java](https://github.com/323erir6/Enhanced-Detector-Radar/blob/main/src/main/java/dev/radarcompat/enhanceddetector/mixin/PlayerDetectorPrecisionMixin.java), [RadarPeripheralMixin.java](https://github.com/323erir6/Enhanced-Detector-Radar/blob/main/src/main/java/dev/radarcompat/enhanceddetector/mixin/RadarPeripheralMixin.java), [SableEnginePeripheralMixin.java](https://github.com/323erir6/Enhanced-Detector-Radar/blob/main/src/main/java/dev/radarcompat/enhanceddetector/mixin/SableEnginePeripheralMixin.java).