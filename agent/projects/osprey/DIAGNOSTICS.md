# OSPREY — passive diagnostics subsystem (inert test platform)

The diagnostics modules observe CC:Sable physical-object motion and make that
observation visible on a CC:Tweaked pocket computer and, when available, CC:AR.
This is an **instrumentation-only subsystem**. It contains no waypoint, target,
player/entity tracking, motor controller, ordnance logic or actuation commands.

## Install

On the on-board inert laboratory object:
1. Copy `lua/diagnostics_protocol.lua` and `lua/diagnostics_sender.lua`.
2. Copy `lua/diagnostics_config.example.lua` to `diagnostics_config.lua`.
3. Attach a wireless modem and ensure the CC:Sable `sublevel` API exists.
4. Run `diagnostics_sender` from the directory containing the files.

On a pocket computer:
1. Copy `lua/diagnostics_protocol.lua` and `lua/diagnostics_receiver.lua`.
2. Copy `lua/diagnostics_receiver_config.example.lua` to `diagnostics_receiver_config.lua`.
3. Attach a wireless modem, optionally a CC:AR controller.
4. Run `diagnostics_receiver`.

## QA

From the repository root:

```sh
(cd agent/projects/osprey/lua && lua5.3 ../tests/test_diagnostics.lua)
(cd agent/projects/osprey/lua && lua5.3 ../tests/test_diagnostics_sender.lua)
(cd agent/projects/osprey/lua && lua5.3 ../tests/test_diagnostics_receiver.lua)
```

The receiver is deliberately passive: it never calls `rednet.send`, broadcasts
commands, or touches peripherals controlling movement. Invalid, stale or
out-of-sequence frames are rejected. The transport is **not authenticated**;
this is a laboratory observability feature, not a security boundary.

Passing Lua tests proves packet validation and mocked CC behavior only. The
CC:AR rendering call still requires testing against the installed hardware.
