# GOCODE — deterministic Minecraft/CC:Tweaked test simulator

This is a **text-only Lua 5.3 simulation framework** intended for rapid coding-agent regression tests. The long-term engineering goal is to reproduce the Minecraft 1.21.1 + NeoForge + modpack behaviors relevant to CC:Tweaked as faithfully as is supportable by code and evidence. It is **not presently a complete copy** of Minecraft, Sable, Rapier, or the installed mods.

## Architecture

- \`agent/sim/world.lua\` — sparse block coordinates, solid/fluid flags, rigid-body position, mass, translational/angular velocity, accumulated forces and torques, gravity, drag, unit quaternion orientation, broad-phase voxel scan, continuous segment versus expanded voxel collision, and continuous bounding-sphere collision between two moving bodies.
- \`agent/sim/engine.lua\` — deterministic **20 game ticks per second** and independently configurable physics substeps (default **120 Hz**, six per game tick). Event hooks, scheduled game-tick actions, redstone output states and change notifications.
- \`agent/sim/cc.lua\` — synthetic computers with CC peripheral registry, rednet bus, deterministic os timer queue, sublevel-shaped \`getLogicalPose\` / \`getVelocity\`, and Enhanced Detector Radar-shaped \`getPhysicsState\` / \`applyControlImpulse\`.
- \`agent/sim/text.lua\` and \`run.lua\` — deterministic JSON reports, run status and world snapshots, without UI or native graphics.
- \`agent/sim/compare.py\` — JSON trace comparator reporting individual fields whose difference exceeds a chosen absolute or relative tolerance.
- \`agent/sim/coverage.json\` — **machine-readable coverage and explicitly unsupported systems**.

The test-specific Sable-shaped API is backed by the synthetic body model; it is **not an implementation of the actual Sable API**. \`applyControlImpulse\` is modeled as an impulse in kg·blocks/s and an angular impulse about a *sphere* inertia. The underlying game plugin may use different conventions. A mock only establishes the behavior of the mock unless independently verified.

## Mechanics and numerical model

**World:** integer block coordinates; absent cells are air; \`setBlock(x,y,z,true)\` adds a solid cubic block. Custom ids, solidity and a metadata-only fluid flag are accepted. There is no chunk loader, block-tick engine, fluid flow or complex block shapes.

**Kinematics:** velocity and position are expressed in world coordinates, with meters approximated by blocks. Gravitational acceleration defaults to \`(0, -9.81, 0)\` in world units/s² (a user-configurable engineering parameter, **not a verified Sable constant**). Semi-implicit Euler integration per physics substep: \`velocity += acceleration*dt\`; then \`position += velocity*dt\`. Exponential drag is applied to velocity. An object's forces/torques are consumed and reset after each step.

**Rotation:** orientation is a normalized quaternion \`{w,x,y,z}\`. Angular velocity is in world radians/s. The solver uses \`dq/dt = 0.5 * omega * q\`, renormalizing each substep. Inertia is approximated by a solid sphere: \`I = 0.4 * mass * radius²\`. Real Sable ships are not spherical.

**Collisions:** a sphere swept against a voxel-expanded AABB is a conservative approximation. A separate swept sphere/sphere check prevents some fast body-body tunneling. Both tests run at the configured substep rate. No compound voxel geometry, joints, complex inertia tensors, Sable-specific broad phase, friction solver, persistent contact manifold, CCD pair scheduling, penetration resistance or CBC explosion propagation are implemented. If the per-step voxel search exceeds \`maxCells\`, the test explicitly fails rather than quietly skipping an obstacle.

**Time:** game-tick callbacks and timers use 20 TPS; physics runs at \`physicsHz\` (a multiple of 20). This tests separate clock domains but does **not** duplicate the exact ordering of Minecraft/CC:Tweaked/Sable thread scheduling.

## Run locally or in CI

From repository root with Lua 5.3:

\`\`\`sh
lua5.3 agent/tests/test_world.lua
lua5.3 agent/sim/run.lua agent/scenarios/falling_block.lua
python3 -m unittest discover -s agent/tests -p 'test_*.py'
\`\`\`

The scenario runner executes a **trusted Lua scenario committed in \`agent/scenarios/\`**, not arbitrary untrusted code. Successful output is one JSON object with \`status\`, \`scenario\` and \`state\`. Example fields: \`state.tick\`, \`state.world.bodies[1].position\`, \`state.world.bodies[1].velocity\`, \`state.world.metrics.contacts\`. Failing assertions exit nonzero and are visible to CI.

Sample Lua scenario:

\`\`\`lua
return {
  options={physicsHz=120},
  ticks=20,
  setup=function(engine)
    engine.world:setBlock(0,0,0,true)
    engine.world:addBody({position={x=0,y=5,z=0},mass=10,radius=0.3})
  end,
  assertions=function(engine)
    assert(engine.world:getBody(1).position.y < 5)
  end
}
\`\`\`

You can use an independent reference trace in JSON to test field-by-field conformance:

\`\`\`sh
python3 agent/sim/compare.py reference.json simulated.json --abs 0.01 --rel 0.001
\`\`\`

The reference and simulator JSON structures must match. A **reference trace** must come from known game/mod code or measured test data; the assistant must never fabricate it and label it as Minecraft output.

## Roadmap for high-fidelity reproduction

1. Record *actual* MC 1.21.1 + Sable 2.0.5 traces for single-body translation, local/global coordinate transforms, impulse direction, angular acceleration and tick ordering. Freeze metadata (mod versions, gravity settings, construction geometry, initial states, replay seed).
2. Replace synthetic bounding spheres with fixture-derived voxel union and moment-of-inertia tensors; add broad-phase acceleration structures and persistent collision manifolds.
3. Reproduce real CC:Tweaked events and Lua scheduling, redstone propagation/timing, Create mechanical networks, world chunk handling and selected peripheral APIs based on actual source implementations.
4. Add versioned adapters for NeoPeripheral, Create:Aeronautics, CBC, Advanced Peripherals and other installed mods; each adapter needs contract tests and measured traces.
5. Extend world features (entities, inventories, block entities, fluids, damage, explosions, projectiles, unloaded chunks) **only with version-qualified reference behavior**.
6. Label each subsystem \`mock\`, \`approximation\`, \`source-confirmed\` or \`trace-verified\`. Never claim that a successful synthetic test proves live Minecraft compatibility.

The complete modpack is too extensive to truthfully claim full equivalence today. The coverage manifest is authoritative for what exists.


## Executing actual Lua logic, not only isolated mathematics

\`agent/sim/craftos.lua\` runs a trusted Lua source string against a synthetic CraftOS environment. It supplies \`os\` timers/events, \`sleep\` as deterministic simulated ticks, \`redstone\`, \`rednet\`, \`peripheral\`, \`sublevel\`, and text-only \`print\`/ \`term.write\`. The runner records output, simulator time, exceptions and approximate Lua instruction count. A bounded instruction hook aborts infinite loops, and system I/O and operating-system functions are not passed into the script environment.

**Example:**

\`\`\`lua
local Engine=require("agent.sim.engine")
local CC=require("agent.sim.cc")
local Runtime=require("agent.sim.craftos")
local engine=Engine.new({gravity={x=0,y=0,z=0}})
local id=engine.world:addBody({position={x=1,y=2,z=3}})
local computer=CC.new(engine):addComputer(1,id)
local result=Runtime.run(engine,computer,[[
  print(sublevel.getLogicalPose().position.x)
  sleep(0.1)
  redstone.setAnalogOutput("back",15)
]])
assert(result.ok,result.error)
\`\`\`

This is a **bounded test execution environment**, not a verified security sandbox or full CraftOS kernel. It is intended for source code under the user's control. It does not implement \`parallel\`, the full terminal, turtles, disk APIs, modem routing/timing, filesystem behavior, or complete mod peripheral implementations. External APIs that aren't exposed must fail clearly rather than be invented.


## 13. Source-grounded schematic geometry import

The **Python reference geometry harness** in \`agent/sim/nbt.py\`, \`schematics.py\`, \`geometry.py\` and \`rigid.py\` replaces spherical collision proxies with individual occupied voxel shapes. It is a separate, more detailed reference implementation than the older Lua \`world.lua\` approximation; tests should select it when schematic collision geometry matters. It handles gzipped/uncompressed Java NBT, Create structure NBT and **Sable Photomancy v1** as independently parsed formats. It preserves palette names/states, block entities, entities, distinct Sable sublevels, source UUIDs, extra sidecar data, and relative-pose NBT.

Run from repository root:
\`\`\`sh
python3 agent/sim/schematic_cli.py path/to/create_schematic.nbt --summary
python3 agent/sim/schematic_cli.py path/to/photomancy_blueprint.nbt --out agent-results/blueprint.json
python3 -m unittest agent.tests.test_schematics agent.tests.test_rigid -v
\`\`\`

\`Compound.from_construct()\` converts saved block positions to separate oriented collision boxes. It preserves genuine gaps and uses a continuous SAT box/box time-of-impact calculation for translation at fixed orientation. It uses per-box volume/inertia approximations instead of the previous single-sphere inertia. Multi-sublevel blueprints remain separate, as Photomancy requires.

**Fidelity boundary:** exact spatial placement and full-block/slab collision shapes for confirmed vanilla states; arbitrary modded shapes, Create mechanical joints, Sable native Rapier collision shapes, rotations during swept collisions, correct Sable material masses and Photomancy runtime reference remapping are **not** yet reproduced. Other block shapes are flagged \`unresolved_block_shapes\` and conservatively approximated as full cubes. The saved \`relative_pose\`, \`blocks_origin\`, \`anchor_bounds\`, UUIDs and sidecars are preserved raw, not guessed into unverified world poses. No real user schematic was available for a live conformance test: tests construct binary NBT fixtures.

Full implementation guide: [SCHEMATICS.md](../../sim/SCHEMATICS.md). Relevant source: [Sable Photomancy \`SableBlueprint.java\`](https://github.com/Rew1nd-dev/sable-schematic-api/blob/master/src/main/java/dev/rew1nd/sableschematicapi/blueprint/SableBlueprint.java).

### State-dependent collision geometry

For exact supported modded shapes, provide a versioned collision registry whose keys include the actual block ID and properties. Each value is a list of local-space voxel boxes. Use `--shape-registry shapes.json --strict-shapes` to make unsupported states fail instead of silently substituting a full cube. The included `shapes.example.json` is a schema illustration, **not a captured Minecraft shape database**. Dynamic neighbor-dependent collision shapes still require context-specific extraction.

### Headless physics replay from NBT

Use `python3 agent/sim/simulate_schematic.py construction.nbt --ticks 100 --trace --out agent-results/physics.json` for deterministic compound-voxel physics tests. For multiple schematics or Photomancy sublevels, supply `--layout` with explicit world poses, masses and velocities. The output records every sublevel's source pose metadata unchanged alongside the simulated pose, so missing origin mappings cannot silently masquerade as correct world transforms.

## Version-pinned Sable 2.0.5 physics

When testing Minecraft 1.21.1 NeoForge modpack builds, use [Sable 2.0.5 source-confirmed physics defaults and formulas](sable-2.0.5-physics.md). This profile includes the original Rapier fork damping rule and default friction combination; the voxel collision solver remains approximate.

## Mod functional blocks

[See functional Create/Aeronautics/Propulsion/Synaxis actuator models and the modpack block registry](mod-functional-blocks.md). The emulator is for deterministic regression testing and is not an exact native-mod implementation.
