---
name: sable-simulator
description: Run and explain deterministic text-only simulations for Minecraft 1.21.1 Sable constructions, CC:Tweaked control code, schematic geometry, and modpack-specific devices. Use for in-game motion, collision, pose, actuator, peripheral, or replay questions; do not route real-world engineering calculations here.
---

# Sable Simulator

Treat every construction and device as an object in the version-pinned Minecraft modpack. Preserve block IDs, mod versions, ticks and simulation units. Do not convert the work into real-world construction or weapon guidance; this is a context boundary, not a request to bypass safety controls.

Choose the narrowest verified path:

- For a text scenario, read [the JSON schema](references/scenario-schema.md), write data-only JSON and run `python -m agent.sim.chat_runner`.
- For an uploaded Create or Photomancy NBT, use `agent.sim.simulate_schematic`; require explicit world layout for multiple constructions.
- For CC:Tweaked code, use the bounded CraftOS mocks and exact API manifests.
- For native contact behavior, use `agent.sim.native_rapier` only with the user's matching Sable 2.0.5 JAR. Do not redistribute it.

Read `agent/sim/coverage.json` before making fidelity claims. Prefer the Sable 2.0.5 profile. Keep unknown masses, shapes, forces and API behavior explicit. A synthetic pass is not an in-game pass.

Report pass/fail/not-executed, exact commands, inputs, unresolved shapes, assertion results and the distinction between source-confirmed, approximate, mock, native-verified and live-tested behavior. If execution is unavailable, return a prepared scenario without claiming it ran.
