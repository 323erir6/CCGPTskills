# OSPREY — Minecraft 1.21.1 NeoForge flight-test prototype

**Project status: GOCODE prototype v0.1 / NO FLIGHT QUALIFICATION.** This is an **unarmed, in-game** experimental vehicle and test environment. It does not implement payload actuation, explosives, real geodesy, real-life navigation or remote services. In-game destination markers and observed Minecraft objects are used for *non-destructive tracking and flight tests*. No claim of operational 20–600 km range is made.

## Verified mod versions (actual OneOne 6.9.3 JARs)

- Create Propulsion: Simulated **1.1.5**: `createpropulsion:solid_fuel_thruster`; CC methods `setPowerNormalized`, `getBurnTimeRemaining`, `getCurrentThrustPN`. Source: `createpropulsion-1.1.5.jar`, `SolidFuelThrusterPeripheral`.
- Synaxis **1.5.0** with NeoPeripheral **1.4ve**: `synaxis:compact_flap`; `setAngle(double)` and `setTilt(double)` from `CompactFlapPeripheral`. **Angles are in degrees**: the implementation passes the input to Minecraft `Mth.wrapDegrees`.
- CC:Sable **1.3.4**: global `sublevel.getLogicalPose()`, `sublevel.getLinearVelocity()`, `sublevel.getAngularVelocity()`. `getLogicalPose` returns `{position={x,y,z}, orientation={x,y,z,w}, scale=..., rotationPoint=...}`.
- CC:AR **0.2.1**: `drawRect2D`, `drawText2D`, `update`, confirmed from `ARControllerPeripheral`. AR requires a separate station attached to a controller, with compatible goggles. **CC:AR is not the pocket computer itself**.
- Sable **2.0.5**, Photomancy **1.0.1**, Create **6.0.10**: world and schematic pipeline.

## Construction

The program generates a compact **5 × 5 × 16-block Create schematic**, forward local axis **+Z**. It has 4 symmetric fuel-burning `solid_fuel_thruster`s (rear, at Z=0), 4 `compact_flap` blocks around the tail (Z=2), Create casing spine, 1 advanced ComputerCraft computer and 1 Sable chunk loader.

```
Looking towards +Z (schematic X/Y cross-section)

       y+
       F
    E     E
  F    C    F       E = fuel engine, F = compact flap
    E     E         C = body spine (at other Z levels)
       F            no explosive payload
           x+
```

Generate the schematic from the project root:

```sh
python3 agent/projects/osprey/tools/build_schematic.py
```

This writes `schematics/OSPREY_Create.nbt` and `schematics/layout.json`. Both are included in the release artifact.

**Important assembly constraints:** Create `.nbt` is a **block template**, not an assembled Sable physical sublevel. Place it using Create, connect modem and peripheral network manually, put valid fuel into all four engines, and form the physical Sable construct. A Synaxis compact flap may require assembly of an attached movable surface and its orientation must be calibrated on a tethered stand. The schematic does not automatically place a preconfigured wireless modem, load fuel, pair CC:AR goggles, or assign Lua programs to the computer. It cannot guarantee a real flying vehicle immediately after pasting.

## Installation on CC computers

Copy the 5 `lua/*.lua` programs and `config.example.lua` to a computer's working directory. Copy `config.example.lua` to `config.lua` and configure the actual peripheral names (check `peripheral.getNames()` and `peripheral.getMethods(name)` on your physical build). On the rocket run `onboard.lua`; on a wireless pocket computer run `operator.lua`; optionally run `sensors.lua` on a radar-linked station and `ar_bridge.lua` on a computer connected to CC:AR controller. Each unit must have a usable wireless modem and matching pairing token.

The operator can set in-game XYZ markers, select observed in-game players/entities/sublevels when supported sensors report them, view telemetry, and request a **non-destructive test launch**. The controller will not start fuel engines unless `config.allow_control=true`; check signs and units, hardware wiring and direction first. A `SAFE` command is allowed only before ignition: **solid-fuel motors are not guaranteed extinguishable after ignition**. Lack of telemetry or loss of moving-object observations does not substitute for a safe physical launch mechanism.

**The current steering rule is an unqualified line-of-sight game demonstration.** It is not a predictive ballistic guidance system. Moving-object radar scan signatures and radio range remain to be verified in a live server. Tests do not establish that the vehicle can reach a requested marker or a 20–600 km gameplay distance, especially under native Sable drag, chunk loading, height limits and limited fuel.

## QA and known limits

Run from GOCODE repository root:

```sh
python3 -m unittest agent.projects.osprey.tests.test_build agent.projects.osprey.tests.test_runtime -v
lua5.3 agent/projects/osprey/tests/test_common.lua
(cd agent/projects/osprey/lua && lua5.3 ../tests/test_onboard.lua)
```

The first suite tests NBT roundtrip, installed mod block IDs, fin/motor symmetry and a smoke run with GOCODE's **synthetic** functional-block simulator. Lua mock tests verify protocol validation, quaternion direction conversion and the default **no-actuation** guard. These tests DO NOT constitute a real Minecraft launch or 600-km-range validation.

### Open tasks before any accurate range claim

1. Confirm solid-fuel thruster **blockstate facing** and in-world output axis after Create paste; do not assume all 4 engines point outward in the intended direction.
2. Confirm Sable sublevel assembly and actual total mass, center of mass, moment of inertia and engine inventory after build.
3. Assemble/configure Synaxis flaps, verify each sign and `setAngle` response empirically.
4. Replace synthetic fin dynamics with calibrated or native mod interaction; verify trajectory at several distances in Minecraft.
5. Verify radar scan argument lists, reported entity positions, chunk-loading behavior and wireless modem range in the specific server.
6. Repeat native physics tests against actual assembled construct; run regression checks with in-game logged motion.

**Status by task:** layout `.nbt` generated + parsed, Lua modules implemented and syntax-checked, mock and synthetic scenarios pass; complete Sable assembly, motor thrust under fuel, physical steering, player/entity observation and 20–600 km reachability are **not validated in game**.
