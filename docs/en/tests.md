# Test documentation

CI uses Lua 5.3 to parse all `lib/`, `examples/` and `tests/` files. Deterministic regression suites execute: `math3d_test.lua`, `pid_test.lua`, `round_test.lua`, `sublevel_pose_test.lua`. The latter uses synthetic quaternion poses for identity, translation/scale/pivot, and 90-degree rotations.

## Manual test

Copy `lib/` and `tests/` into a CC computer, execute `tests/math3d_test`, `tests/pid_test`, `tests/round_test`, `tests/sublevel_pose_test`. For peripheral-specific behavior, use a separate real-device test. A passing math test is not proof that a particular mod's peripheral is present or its data shape matches.

## Test result terminology

- Executed and passed: actual run completed with all assertions true.
- Executed and failed: capture full failure and environment.
- Reviewed only: inspected code without executing.
- Not tested: no reliable verification.
