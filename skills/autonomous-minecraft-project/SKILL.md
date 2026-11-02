---
name: autonomous-minecraft-project
description: Develop and verify a modded Minecraft 1.21.1 project from a technical specification, using user-authored schematics, CC:Tweaked code, exact mod APIs, and the real isolated 6.9.3 headless runtime. Use when an agent is expected to continue from requirements through implementation and live qualification with minimal human involvement.
---

# Autonomous Minecraft Project

Own the complete bounded development cycle: turn the technical specification into measurable criteria, inspect the supplied schematics, implement code, run the cheapest useful checks, run the real isolated server, analyse evidence, correct failures, and repeat until every criterion is verified.

Do not stop at a prototype, successful compilation, mock pass, prepared test, or list of instructions for the user. Do not ask the user to perform routine installation, firing, calibration, log collection, or parameter tuning when the available tools can do it. Never call synthetic or native-only evidence an in-game pass.

## Start

1. Read repository instructions, the technical specification, current implementation, exact mod versions, API manifests, and `agent/sim/coverage.json`.
2. Read [the execution loop](references/execution-loop.md).
3. For every supplied `.nbt`, read [the schematic contract](references/schematic-contract.md), create an explicit connection contract, and run `agent.sim.schematic_preflight`.
4. Create a version 1 autonomous project manifest from `agent/autonomy/project.template.json`; validate and track it with `agent/scripts/autonomous_project.py`.
5. Read [the live-runtime rules](references/live-runtime.md) before claiming integration success.

The schematic is a human-owned input. Inspect it, preserve it, and build code around it. If its geometry, block choice, orientation, physical-construction grouping, or device wiring prevents the specification from working, record a schematic issue and tell the human exactly what must change. Do not silently edit, replace, regenerate, or approximate the schematic.

## Non-negotiable CC:Tweaked topology

A computer may use a peripheral only when either:

- the two blocks share one full block face; diagonal contact does not count; or
- both are connected to the same wired-modem network.

The computer, peripheral, modems, and cables involved in that link must all belong to the same Sable physical construction. World-space proximity between separate constructions is not a connection. Confirm wired links again in the live runtime with `peripheral.getNames` and `peripheral.getMethods`.

## Finish gate

Run `python agent/scripts/autonomous_project.py gate <project.json>`. Finish only when it reports `complete`. A genuine open schematic defect is a human blocker. Ordinary code defects, calibration errors, failed tests, missing adapters that can be implemented, and unexpected logs are work for the agent, not reasons to hand the project back.

Report exact artifacts, commands, hashes, test counts, measured results, and remaining client-only checks. Never promise continued execution after the current agent turn or conceal an unavailable execution environment.
