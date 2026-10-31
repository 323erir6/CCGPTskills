# Geometry and feedback control for Lua programs

Math utilities are useful for navigation, animation, robotics and servo mechanisms.

## Angles

`math.atan(y, x)` behaves like two-argument atan2 on supported CraftOS Lua runtimes; confirm the target runtime. Where available, `math.deg(math.atan(dz, dx))` maps a 2D vector to an angle measured from +X toward +Z.

To wrap degrees into [-180, 180):

```lua
local function wrapDegrees(a)
  return (a + 180) % 360 - 180
end
```

For a heading controller, use `wrapDegrees(target - current)` to choose the shortest angular error.

**Coordinate frames matter.** World X/Y/Z, local forward/right/up and yaw conventions differ between modded entities. Never infer a transformation-matrix field index without confirming the producer's convention.

## Velocity

If positions are measured at timestamps `t0` and `t1`, velocity is `(p1 - p0) / (t1 - t0)`. Protect against zero or tiny `dt`. Minecraft blocks/s can be displayed as km/h by multiplying by 3.6; this is a presentation conversion, not a simulation guarantee.

For local forward speed, compute the dot product of world velocity and the entity's normalized world-forward vector.

## P, PD and PID

- P: `u = Kp * e`
- PD: `u = Kp * e - Kd * measurementRate` when the setpoint is fixed or a suitable derivative convention is selected.
- PID: `u = Kp * e + Ki * integral(e dt) + Kd * derivative(e)`

Always clamp output to hardware limits. Apply anti-windup to avoid accumulating integral error while saturated. Derivative filtering and output rate limiting may reduce noise and oscillation.

## Cautions

Controller update periods, deadbands, actuator direction, latency and saturation require measured tuning. An example controller cannot guarantee stabilization on every assembly.

See [Reusable math module](../../lib/math3d.lua) and [PID controller](../../lib/pid.lua).
