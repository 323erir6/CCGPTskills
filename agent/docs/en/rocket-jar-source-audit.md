# Sable/Propulsion six-block rocket — version-pinned source audit

The **original Sable 2.0.5 native Rapier** is already called through JNI by `native_rapier.py`. This upgrade extracts **modded voxel shapes and engine constants from the exact installed mod JARs** and pipes them into the native `LevelCollider`, instead of using six full cubes. The input `.nbt` is read as Photomancy v1. No rendered Minecraft client is needed.

## Provenance and procedure

- `createpropulsion-1.1.5.jar`: `ThrusterShapes.<clinit>`, `SolidFuelThrusterBlockEntity.updateThrust`, `AbstractThrusterBlockEntity`, `ThrusterForceProvider.createSample`, and `data/createpropulsion/solid_thruster_fuels/minecraft/coal_block.json`.
- `simulated-nested.jar`, extracted from `create-aeronautics-bundled-1.21.1-1.3.2.jar`: `SimBlockShapes.<clinit>` and `SymmetricSailBlock`. The lift-provider implementation comes from the **exact `sable-neoforge-1.21.1-2.0.5.jar`**, plus [Sable's versioned source](https://github.com/ryanhcode/sable/tree/mc1.21.1-2.0.5-neoforge).
- `createbigcannons-5.11.7+mc.1.21.1.jar`: `ProjectileBlock.makeShapes`, inherited by the HE shell.
- `rszo_rocket_v0.nbt`: original six saved block coordinates, rotation, block entity states, fuel and `IntactReferenceMass=4.5`.

`rocket_source_profile.py` uses **JDK javap bytecode inspection** and compares numerical shape operands with the pinned schema; it refuses changed/unexpected classes rather than silently using stale values. This is bytecode disassembly of the installed JAR, not invented source code. See installed JAR SHA-256 values in the machine-generated audit JSON.

## Geometry corrected

All shape coordinates use Minecraft's 0–16 sub-block unit and are normalized to 0–1 before passing to JNI.

| Schematic block | Confirmed static geometric source | Unresolved |
|---|---|---|
| `createpropulsion:solid_fuel_thruster[facing=south]` | 5 union boxes, source baseline NORTH and direction rotation | Runtime shape overrides |
| `simulated:white_symmetric_sail[axis=y]` | `(0,6,0,16,10,16)` | Dynamic world effects |
| `simulated:white_symmetric_sail[axis=x]` | Same 4/16-thickness plate rotated onto X | Dynamic world effects |
| `createbigcannons:he_shell[facing=south]` | `(3,0,3,13,16,13)` baseline UP, rotated to SOUTH | Entity spawning and detonation behavior |
| `computercraft:computer_advanced` | No dedicated shapes in current audit; falls back to full cube **with warning** | Runtime `BlockState.getCollisionShape` |
| `sable_autonomous_chunk_loader` | No dedicated shapes in current audit; falls back to full cube **with warning** | Chunk residency and runtime shape |

The entire rocket **is not six cubes**. With `--strict-shapes`, a missing state shape fails the run rather than approximating. This is essential before claiming exact game parity.

## Original equations verified for the modpack

For coal block: fuel datapack `thrust_multiplier=1.15`, `burn_ticks=16000`; configured base thrust `200`. Thus, at full input, clear nozzle, and default non-atmospheric mode, the calculated raw thrust is `200 * 1.15 * 1000` pN (using `thrustUnitsPerKn=1000`), and the native impulse is scaled by `/1000` to `230 * dt` in Sable physics units. This normalization is verified by `ThrusterForceProvider` and `AbstractThrusterBlockEntity.sable$physicsTick`. This **only applies while powered and burning**.

`StartupTicks` ramps from 0 to 10 (0.5 s at 20 TPS); the fuel drain accumulator adds the effective thrust percentage once per tick and decrements whole ticks on its integer crossings. `getEffectiveThrustPercentage` uses the startup envelope and obstruction clearance. `USE_ATMOSPHERIC_PRESSURE` defaults to **false**, but the sails still use dimension-dependent air pressure.

Symmetric sails override `sable$getParallelDragScalar` with `1.75`, `sable$getLiftScalar` with `0`. The inherited directionless drag constant is `0.068882026`. Normals point in the **positive block axis** (`x` or `y` in this schematic). The Sable `BlockSubLevelLiftProvider` computes local point velocity, direction-dependent and isotropic drag, and applies both linear and angular impulses at each substep.

Sable `MassTracker` code computes center of mass from **mass-weighted `BlockState.getCollisionShape` bounds**, then full tensor inertia: for an unconfigured 1 m cube, intrinsic diagonal contribution is `m/6`; parallel-axis contribution is `m * ((r·r)I - rrᵀ)`. `rocket_mass_tracker.py` ports this tensor equation. The NBT value `IntactReferenceMass=4.5` is a saved reference **not a guarantee** of present mass for arbitrary configs.

## Run

From repository root, with JDK 21, `lz4`, `numpy`, `scipy`:

```bash
python3 -m agent.scripts.audit_rocket_jars rszo_rocket_v0.nbt --propulsion-jar createpropulsion-1.1.5.jar --sail-jar simulated-nested.jar --cbc-jar 'createbigcannons-5.11.7+mc.1.21.1.jar' --out agent-results/rocket-jar-audit.json

python3 -m agent.sim.native_rocket rszo_rocket_v0.nbt --jar sable-neoforge-1.21.1-2.0.5.jar --propulsion-jar createpropulsion-1.1.5.jar --sail-jar simulated-nested.jar --cbc-jar 'createbigcannons-5.11.7+mc.1.21.1.jar' --ignite-at 0 --max-seconds 60 --out agent-results/rocket-native.json
```

### Fidelity caveat — NOT a verified in-game result

The collision solver is the **actual** Sable 2.0.5 native binary; this is verified by JNI execution and contact events. The applied engine/sail force schedule is **a separate Python reimplementation**, not the execution of NeoForge block-entity tick classes. The mass and per-block collision registry depend on active tags, modifiers and runtime blockstates. The input NBT has an **OFF** computer and **zero** redstone input, so `--ignite-at 0` injects a test-only launch event. It is not contained in the original save.

Additionally, the autonomous chunk loader, fuze, entity explosions, exact all-block `getCollisionShape` results and loaded-chunk behavior are not run in the original Minecraft runtime. Therefore do not label any resulting impact coordinate as fully game-exact.
