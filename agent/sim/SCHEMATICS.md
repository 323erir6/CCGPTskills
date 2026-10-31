# GOCODE text-only geometry/NBT simulator

No graphics or game server required. Reads Create structure schematics (`size`, `palette`, `blocks`) and Sable Photomancy blueprint version 1 (`version`, `sub_levels`, each with `block_palette`, `blocks.local_pos`, `palette_id`, `block_entities`, `relative_pose`, `extra_data`). **Sharing the `.nbt` extension does not mean formats are identical.**

Run from repository root:

```sh
python3 agent/sim/schematic_cli.py path/to/structure.nbt --summary
python3 agent/sim/schematic_cli.py path/to/photomancy.nbt --out agent-results/fixture.json
python3 -m unittest discover -s agent/tests -p 'test_*.py' -v
```

- Reads compressed (gzip/zlib) or uncompressed Java big-endian NBT with depth/size/collection bounds.
- Preserves exact block positions, palette names, state properties, block-entity tags, entities and Photomancy sidecars/relative poses as JSON. Records each sublevel separately (rather than merging disconnected physics constructs).
- Physical geometry is represented as **individual oriented block boxes**, not a single bounding sphere. A gap between two blocks remains empty. Rotations use quaternion transforms of each box, and CCD solves time of impact for boxes translating with constant orientation, using SAT axes.
- The compound body solver applies gravitation, force/impulse and a mass-derived inertia **approximation**, with a configurable fixed physics timestep, deterministic JSON snapshots and contact events.
- Known full cubes and slabs have shape-specific collision geometry; all other and **modded block shapes fall back to conservative full cubes**, and their exact IDs are reported in `unresolved_block_shapes`. Air and fluids are omitted from solid collision. A modded block marked `unavailable_palette_ids` is deliberately excluded and reported.
- A schematic's `blocks_origin`, `relative_pose`, `anchor_bounds` and other reference metadata are preserved. They are not silently guessed as a world position/orientation. The caller must supply a validated placement transformation for exact Sable pose reproduction.

**Not yet equivalent to Minecraft:** shape registries for every state/mod, actual Sable physics mass and collision shape generation, Rapier contact constraints, the rotation-dependent full CCD sweep, Create bearing joint mechanics, serialized runtime UUID mapping, block entity behavior and exact tick scheduling. These demand version-specific source/trace validation. Do **not** call the result "100% accurate" for unsupported subsystems.

Source evidence: `Rew1nd-dev/sable-schematic-api` `SableBlueprint.java`, `SubLevelSaveFrame.java`; Create structure binary NBT schema as documented for Java Edition. Tests use synthetic binary NBT fixtures, not real user schematics.

## Versioned VoxelShape registry (accuracy upgrade)

For exact collisions on modded blocks, give a blockstate-qualified registry exported from the **same installed modpack**. The registry maps a state key such as `example:thin_plate[facing=north]` to one or more `[minX,minY,minZ,maxX,maxY,maxZ]` boxes, in block-local coordinates. Use `--strict-shapes` to fail on any unresolved block instead of silently treating it as a full cube:

```sh
python3 agent/sim/schematic_cli.py structure.nbt --shape-registry shapes.json --strict-shapes --summary
```

See `shapes.example.json` for the schema **only**: the example records are invented test fixtures, not verified data. Generate real data by querying Minecraft/NeoForge's `BlockState#getCollisionShape` for the installed block states, ideally including neighbor context for connection-dependent blocks. Some block shapes depend on world state, so the registry is only sufficient for context-independent blocks. This importer does not yet include such a game-side extractor.
