# JSON scenario schema

Use `schema_version: 1`. The runner accepts data only and rejects unknown action or assertion types.

Required top-level fields:

- `schema_version`: integer `1`.
- `bodies`: one to 128 body objects.

Useful optional fields:

- `name`: report label.
- `profile`: `sable-2.0.5` (default) or `generic`.
- `ticks`: 0 to 100000 game ticks.
- `trace_every`: 0 disables trace; otherwise sample every N ticks, bounded to 2000 samples.
- `strict_shapes`: reject unresolved Minecraft collision shapes when true.
- `world`: `physics_hz`, `gravity`, `ground_y`, `ground_friction`.
- `actions`: bounded `impulse`, `force` or `torque` entries.
- `assertions`: `position_range`, `velocity_range`, `speed_range`, `event` or `max_unresolved_shapes`.

Each body needs a unique string `id` and exactly one geometry form:

- `blocks`: `{pos:[x,y,z], name:"namespace:block", properties:{...}}` records; or
- `boxes`: explicit local `[minX,minY,minZ,maxX,maxY,maxZ]` bounds.

Body state may include `mass`, `position`, `velocity`, quaternion `orientation`, `angular_velocity`, `damping`, `restitution` and `static`.

Run from the repository root:

```sh
python -m agent.sim.chat_runner scenario.json --pretty --out report.json
```

Exit code 0 means assertions passed, 2 means the simulation ran but assertions failed, and 1 means invalid input or an execution error.
