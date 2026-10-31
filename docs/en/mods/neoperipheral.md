# NeoPeripheral 1.4ve — CC:Tweaked peripheral field guide

**Evidence:** scanned `neoperipheral-1.4ve.jar` from the 143-file mod archive. Method names and declared Java argument types were inspected in the actual class files, not inferred from other mod versions. [Enhanced Detector Radar](enhanced-detector-radar.md), [Sable Autonomous Chunk Loader](sable-autonomous-chunk-loader.md), and [Synaxis Patchpack](installed-peripherals.md) may extend or modify these peripherals.

## Discover exact names and methods

```lua
local names=peripheral.getNames()
table.sort(names)
for _,name in ipairs(names) do
  print("DEVICE",name,peripheral.getType(name))
  local list=peripheral.getMethods(name) or {}
  table.sort(list)
  for _,method in ipairs(list) do print(" ",method) end
end
```

A Java method visible in a class is not automatically a public Lua method; `@LuaFunction`, CC generics, and mod configuration determine the callable method set. Use the listing above as the definitive test for your instance. Wired network names depend on actual network topology.

## Sable Engine peripheral

The core NeoPeripheral `SableEnginePeripheral` implements these Lua-oriented operations:

| Method | Arguments in Java declaration | Meaning |
| --- | --- | --- |
| `getUUID()` | none | UUID string |
| `isOnSubLevel()` | none | whether physical body exists |
| `getName()` | none | construction name |
| `getMass()` | none | mass number |
| `getPosition()` | none | position table |
| `getOrientation()` | none | orientation table |
| `getLinearVelocity()` | none | velocity table |
| `getAngularVelocity()` | none | angular velocity table |
| `getCenterOfMass()` | none | center of mass table |
| `applyLinearImpulse(x,y,z)` | three doubles | server-side linear impulse |
| `applyAngularImpulse(x,y,z)` | three doubles | server-side angular impulse |
| `applyImpulseAtPoint(ix,iy,iz,px,py,pz)` | six doubles | impulse applied at point |
| `applyImpulseAtRelativePoint(ix,iy,iz,rx,ry,rz)` | six doubles | impulse at relative point |

Use the actual runtime field keys returned by `getPosition`, `getOrientation` before coding serialization assumptions. World-vs-body coordinates for force-at-point methods must be confirmed for the installed release.

With **Enhanced Detector Radar 1.0.5** installed, the same device additionally receives `getPhysicsState()`, `applyControlImpulse(lx,ly,lz,ax,ay,az)` and `stepControl(lx,ly,lz,ax,ay,az)`. See that book for the exact new table fields `x/y/z,qx/qy/qz/qw,vx/vy/vz,wx/wy/wz,mass`.

```lua
local d = peripheral.find("sable_engine")
assert(d, "Sable engine peripheral missing")
local ok, state = pcall(d.getPhysicsState)
if ok and type(state) == "table" then
  print(textutils.serialize(state))
else
  print("No physics snapshot available")
end
```

The preceding example requires Enhanced Detector Radar and is read-only. For other versions use `getPosition()` and `getLinearVelocity()` when offered by the inspected method list.

## Sub-level radar

`RadarPeripheral` exposes `isCreative()` and `scanForSubLevels([radius[,absolute]])`. `TriangleRadarPeripheral` also exposes `scanForSubLevels()`. These are distinct device types and do not guarantee identical tables. Enhanced Detector Radar adds `velocity_x/y/z` and `size_x/y/z` fields. **Important:** non-creative `x/y/z` may represent radar-relative noisy offsets, not absolute position. Quaternions in this radar use `q_x/q_y/q_z/q_w` — *not* the Sable Engine `qx/qy/qz/qw` spelling.

`EntityRadarPeripheral` supports `scanForEntities(...)` and `scanForPlayers(...)`. The Java interface accepts an argument reader, so allowed filters and limits must be checked against the installed implementation; do not assume compatibility with Advanced Peripherals Player Detector.

```lua
local radarName="radar_name"
local d=assert(peripheral.wrap(radarName))
assert(d.scanForSubLevels, "Device has no sub-level scanner")
local rows=d.scanForSubLevels(128,false) or {}
for _,row in ipairs(rows) do
  print(textutils.serialize(row))
end
```

## CBC mount variants

**Distinct wrappers with related operations**:

| Variant | Methods declared by corresponding Java peripheral |
| --- | --- |
| `CannonMountPeripheral` | `assemble()`, `fire()`, `disassemble()`, `isRunning()`, `getYaw()`, `getPitch()`, `setYaw(angle)`, `setPitch(angle)`, `getX/Y/Z()`, `getDirection()` |
| `FixedCannonMountPeripheral` | same core methods as cannon mount |
| `CompactCannonMountPeripheral` | `assemble()`, `fire()`, `disassemble()`, `isRunning()`, `getPitch()`, `setPitch(angle)`, `getX/Y/Z()`, `getDirection()`; **no yaw methods in this class** |

Check returned status and server mechanical constraints. `fire` is a void Java method; never expect a boolean acknowledgement from it. Methods from other mods may be present on the same mounted peripheral.

## Synaxis integrations

`DynamicMotorPeripheral` methods: `setGainP(number)`, `setGainI(number)`, `setGainD(number)`, `setPID(p,i,d)`, `getGainP/I/D()`, `setTarget(number)`, `GetTarget()` (**capital G as found in Java**), `setMode(boolean)`, `getMode()`, `setGravityCompensation(boolean)`, `getGravityCompensation()`, `collect()`.

`CompactFlapPeripheral`: `setAngle`, `getAngle`, `setTilt`, `getTilt`, `assemble`, `disassemble`.

`CameraPeripheral`: `getPitch`, `getYaw`, `getDistance`, `isRayEnabled`, `setRayEnabled`, `rayRange`, `setRayRange`, `collect`.

`JetPeripheral`: `setTrust`/**`getTrust`** (spelling from bytecode, not `Thrust`), `setHorizontalAngle`, `getHorizontalAngle`, `setVerticalAngle`, `getVerticalAngle`, `collect`.

`AnchorPeripheral`: `setAirResistance`, `getAirResistance`, `setExtraGravity`, `getExtraGravity`, `setRotationalResistance`, `getRotationalResistance`, `collect`.

`KineticResistorPeripheral`: `getRatio`, `setRatio`.

**Angle units:** the source signatures use doubles, but bytecode signatures alone do not prove degrees vs radians. Probe a known position, inspect actual configuration, and confirm semantics before closing a feedback loop. Other Synaxis Patchpack methods may extend these.

## Linked controller hubs

`LinkedControllerHubPeripheral`: `getButton`, `getButtons`, `getKeys` and associated attached-computer support. `TweakedLinkedControllerHubPeripheral` is a different wrapper; the callable interface must be read from its runtime methods.

## Other device families

NeoPeripheral also contains NFC reader/master, Crypto, Socket and modem-related classes. Some implement interface or item APIs without clearly exposed annotated methods in the small inventory; do not invent functions based on class name alone.

## Validation and scheduling

1. Check device type and all method names.
2. Identify underlying body/UUID before using engine operations.
3. Verify return-table keys before assuming layouts.
4. Treat all numeric forces/impulses as physical signals with version-specific units.
5. Use `sableSync.getPhysicsFrequency()` only when that API exists; it is not a general `os.clock()` replacement.
6. Configure `sable_engine.enable` appropriately; high-frequency command availability depends on installed add-ons.
7. Preserve the distinction between absolute and relative coordinates.

**Evidence level:** actual installed JAR class names/signatures and the additional mixin source; in-game peripheral enumeration has not yet been executed.