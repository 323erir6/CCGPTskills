# CBC Aeronautics Velocity Fix 1.0.7 — no CC API

**Installed JAR:** `cbc_aero_velocity_fix-1.0.7.jar`; mod ID `cbc_aero_velocity_fix`. No public source repository was supplied in the inspected set.

## CC:Tweaked integration

The JAR's bytecode scan found **no CC:Tweaked peripheral registration, global Lua API or `@LuaFunction` declaration**. It is a physical compatibility patch rather than a scriptable device.

The JAR's NeoForge metadata describes incorporating construction/sub-level velocity into Create Big Cannons projectile launch behavior. That metadata describes a different detail from an informal description of preventing fast physical constructions passing through each other. **The two are not equivalent; implementation-level behavior requires verification from source/decompilation.** Do not attribute any Lua methods, position fields or physics integration constants to this mod.

## Dependencies declared in NeoForge metadata

Requires Minecraft 1.21.1, NeoForge 21.1.219+, CBC 5.11+, Sable 1.2+; optional integration entries include `cbc_at`, `cbc_equally_opposite`, `cbc_going_ballistic`.

## Troubleshooting

When a projectile's initial velocity differs from expectation, isolate the mod in a test instance and compare world velocity before/after firing. When a *whole physical construction* tunnels through another, do not assume this mod owns that collision path without examining its installed Mixin targets.

**Status:** Installed-JAR metadata confirmed; full implementation semantics require further source inspection; **no direct CC API detected**.