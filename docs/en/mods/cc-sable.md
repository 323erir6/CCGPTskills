# CC:Sable: sublevel and aero APIs (offline field reference)

**Status:** Functions verified against the CC:Sable public Lua API reference (2026-05-13). Some field shapes below are from a known working CC:Sable pose program and must still be checked on the installed version.

**Runtime:** CC:Tweaked + CC:Sable + Sable, Minecraft 1.21.1. Global `sublevel` is available on computers with the add-on; most sublevel methods require a computer currently aboard a Sub-Level.

## 1. API inventory

| Method | Input | Output | Semantics |
| --- | --- | --- | --- |
| `sublevel.isInPlotGrid()` | none | boolean | Whether current computer occupies a sub-level |
| `sublevel.getUniqueId()` | none | string UUID | Persistent sub-level identifier |
| `sublevel.getName()` | none | string | Human-readable name |
| `sublevel.setName(newName)` | string | no documented return | Change sub-level name |
| `sublevel.getLogicalPose()` | none | pose table | Current logical transform |
| `sublevel.getLastPose()` | none | pose table | Previous logical transform |
| `sublevel.getVelocity()` | none | vector | Global velocity |
| `sublevel.getLinearVelocity()` | none | vector | Latest linear velocity |
| `sublevel.getAngularVelocity()` | none | vector | Latest angular velocity |
| `sublevel.getCenterOfMass()` | none | vector | Center of mass |
| `sublevel.getMass()` | none | number | Mass |
| `sublevel.getInverseMass()` | none | number | Inverse mass |
| `sublevel.getInertiaTensor()` | none | matrix | Inertia tensor |
| `sublevel.getInverseInertiaTensor()` | none | matrix | Inverse inertia tensor |

Except `isInPlotGrid`, sublevel calls typically raise an error if no sub-level is associated with the computer. Do **not** use `ship` (CC:VS) API methods on `sublevel`: those are distinct integrations.

### 1.1 Pose structure

A known working CC:Sable Lua representation is:

```lua
{
  position = {x = 100, y = 80, z = -20},
  rotationPoint = {x = 5, y = 6, z = 7},
  scale = {x = 1, y = 1, z = 1},
  orientation = {
    a = 1, -- scalar w
    v = {x = 0, y = 0, z = 0} -- vector x,y,z
  }
}
```

All numeric fields above are **illustrative**, not fixed API defaults. Orientation is a quaternion: `w = orientation.a`, `x = orientation.v.x`, `y = orientation.v.y`, `z = orientation.v.z`. Do not assume global pose.position equals a chosen block's world position: the *rotation point* must be included.

## 2. Local coordinate -> world coordinate

Convention:

```text
local      = (sx,sy,sz)  coordinate inside the sub-level
r          = pose.rotationPoint
s          = pose.scale
t          = pose.position
q          = normalized pose.orientation
offset     = (local - r) component-wise multiplied by s
world      = t + R(q) * offset
```

Quaternion rotation matrix for `q=(w,x,y,z)`:

```text
R00 = 1 - 2(y*y+z*z)
R01 = 2(x*y-z*w)
R02 = 2(x*z+y*w)
R10 = 2(x*y+z*w)
R11 = 1 - 2(x*x+z*z)
R12 = 2(y*z-x*w)
R20 = 2(x*z-y*w)
R21 = 2(y*z+x*w)
R22 = 1 - 2(x*x+y*y)
```

**Production implementation:** [`lib/sublevel_pose.lua`](../../../lib/sublevel_pose.lua), function `localToWorld({x,y,z}, pose)`. It validates the pose, normalizes q and applies translation/pivot/scale/rotation. Matching executable program: [`examples/sublevel_world_position.lua`](../../../examples/sublevel_world_position.lua).

Common errors: forgetting `rotationPoint`; rotating an already-world-space position; using degrees instead of quaternion components; multiplying scale after rotation; treating a zero or non-unit quaternion as valid; mixing Sable `sublevel` and CC:VS `ship` representations.

### 2.1 Inverse transform

```text
offset = inverse(R(q)) * (world - t)
local  = rotationPoint + offset component-wise divided by scale
```

For a unit quaternion, inverse rotation is its conjugate `(w,-x,-y,-z)`. Inverse transform fails when any scale component is zero.

### 2.2 Point vs direction

A **point** includes scale and translation; a **direction** rotates but does not translate. Use `localDirectionToWorld({x=0,y=0,z=1}, pose)` to obtain the ship's forward unit axis under the defined +Z convention, not `localToWorld`.

## 3. Yaw, pitch, roll from quaternion

Chosen convention: world +Y up; body +Z forward and body +X right. This is not a universal convention across modded vehicles. Denote a normalized quaternion as `(w,x,y,z)`.

```text
forwardY = 2(y*z - x*w)
forwardX = 2(x*z + y*w)
forwardZ = 1 - 2(x*x + y*y)
rightY   = 2(x*y + z*w)
upY      = 1 - 2(x*x + z*z)

pitch = degrees(asin(clamp(forwardY,-1,1)))
yaw   = degrees(atan2(forwardX,forwardZ))
roll  = degrees(atan2(rightY,upY))
```

In modern CC:Tweaked prefer **`math.atan(y, x)`** for two-argument atan2. A script that assumes `math.atan2` can fail depending on Lua compatibility/version. The complete tested-in-CI math implementation is `yawPitchRoll(pose)` in [`lib/sublevel_pose.lua`](../../../lib/sublevel_pose.lua).

At pitch near ±90° the yaw/roll decomposition is singular (gimbal lock); use quaternions or direction vectors for control rather than relying on Euler differences.

### 3.1 Axis sign tests

| Synthetic body rotation | Expected yaw | Expected pitch | Expected roll |
| --- | ---: | ---: | ---: |
| Identity | 0° | 0° | 0° |
| +90° about world +Y | +90° | 0° | 0° |
| +90° about body/world +X from identity | 0° | -90° | 0° (singular) |
| +90° about +Z | 0° | 0° | +90° |

Test the actual contraption by orienting it toward cardinal directions before enabling automated correction.

## 4. Speed

`sublevel.getVelocity()` is documented as global velocity, while `getLinearVelocity()` refers to latest linear velocity; do not assume identical timing without inspecting the installed source.

Magnitude: `sqrt(vx^2+vy^2+vz^2)`. For display, blocks/s × 3.6 = km/h. Local signed forward speed: `dot(worldVelocity, normalize(R(q)*(0,0,1)))`. Negative speed indicates movement opposite to local forward.

For velocity at an *offset point* on a rotating body, theoretical rigid-body kinematics is `v_point = v_origin + omega × r`, with consistent units and a confirmed velocity reference point. CC:Sable documentation does not guarantee the velocity reference point and angular units for every release, so verify these before using the expression.

See [`examples/sublevel_speedometer.lua`](../../../examples/sublevel_speedometer.lua).

## 5. aero API

The global `aero` module supplies dimension-specific physics:

| Function | Input | Return |
| --- | --- | --- |
| `aero.getAirPressure(position)` | vector | number |
| `aero.getGravity()` | none | vector |
| `aero.getMagneticNorth()` | none | vector |
| `aero.getUniversalDrag()` | none | number |
| `aero.getRaw()` | none | config table |
| `aero.getDefault()` | none | default config table |

A vector is normally a CraftOS `vector.new(x,y,z)` (verify installed API). Do not assume air pressure, gravity or drag equals vanilla Minecraft constants in custom dimensions.

## 6. Diagnostic probe

```lua
assert(type(sublevel) == "table", "CC:Sable sublevel API missing")
print("On sublevel:", sublevel.isInPlotGrid())
if sublevel.isInPlotGrid() then
  local pose = sublevel.getLogicalPose()
  print(textutils.serialize(pose))
  print("UUID:", sublevel.getUniqueId())
  print("Velocity:", tostring(sublevel.getVelocity()))
end
if type(aero) == "table" then
  print("Gravity:", tostring(aero.getGravity()))
end
```

Do not enable a controller before confirming pose direction, sign and units.

## Verification and references

- Official CC:Sable sublevel API: https://techtastic.github.io/CC-Sable/modules/sublevel.html
- Official aero API: https://techtastic.github.io/CC-Sable/modules/aero.html
- CC:Tweaked feature compatibility: https://www.tweaked.cc/mc-1.21.x/reference/feature_compat.html
- CC:Sable GitHub: https://github.com/techtastic/CC-Sable
- Pure math tests: [`tests/sublevel_pose_test.lua`](../../../tests/sublevel_pose_test.lua)

**Confidence:** module function signatures from official docs; pose field names and formulas from working integration patterns plus independent deterministic tests. A successful pure-Lua test does not validate installed physics-mod behavior.
