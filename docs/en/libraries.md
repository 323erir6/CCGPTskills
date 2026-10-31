# Reusable Lua modules

## Installation

Copy `lib/` onto a CraftOS computer. When the computer's module search path includes the working directory, import for example `local math3d = require("lib.math3d")`. The Lua modules do not fetch network dependencies.

| Module | Scope |
| --- | --- |
| [math3d.lua](../../lib/math3d.lua) | Angles: wrapDegrees, shortestError; vectors: vec/add/subtract/scale/dot/length/normalize/distance; heading, velocity from time samples, forward speed, km/h conversion |
| [round.lua](../../lib/round.lua) | Decimal rounding with midpoint away from zero, for both positive and negative inputs |
| [sublevel_pose.lua](../../lib/sublevel_pose.lua) | Sable pose math: quaternion extraction and normalization, world/local conversion, orientation decomposition, direction and velocity projection |
| [pid.lua](../../lib/pid.lua) | Discrete PID with integral/output clamps and basic saturation anti-windup |
| [peripherals.lua](../../lib/peripherals.lua) | Peripheral inventory, method capability validation, guarded calls |
| [protocol.lua](../../lib/protocol.lua) | Basic versioned message envelopes, input checks; NOT encryption or authentication |
| [config.lua](../../lib/config.lua) | Namespaced CraftOS settings load/get/save with basic type checks |

## Important conventions

- All time deltas used by velocity/PID calculations are in seconds.
- Angles are degrees in `wrapDegrees`, `shortestError` and the documented sublevel Euler output.
- Sable pose quaternion convention uses scalar `a`, vector components `v.x/v.y/v.z`.
- `localToWorld` includes pivot, scale, quaternion rotation and world translation; use direction-only rotation for vectors.
- The PID controller is a numerical example and must be tuned to the actual machine.
- `protocol` validates an envelope; it provides no cryptographic confidentiality or source authentication.
- Missing modded devices are handled by capability checks, not by inventing methods.

## Verification

Pure mathematics: `tests/math3d_test.lua`, `tests/round_test.lua`, `tests/sublevel_pose_test.lua`, `tests/pid_test.lua`. CI runs these under Lua 5.3. Physically attached peripherals remain untested without Minecraft.