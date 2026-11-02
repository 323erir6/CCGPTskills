# Real Sable headless server

The headless path runs an actual NeoForge 21.1.248 dedicated server with Minecraft 1.21.1, the original Sable 2.0.5 JAR and either the complete enabled mod directory or a minimal Sable-only runtime. It does not reimplement Sable equations.

`agent/headless` contains a server-only telemetry mod. A bounded JSON scenario schedules normal server commands, then records every loaded Sable sublevel after completed server ticks: pose, scale, linear and angular velocity, Sable mass, center of mass and world bounds. The report also records the mod IDs and versions loaded by NeoForge. The Python launcher creates an isolated server directory, copies configuration inputs, hashes every enabled JAR and stops the server when the scenario ends.

## Run on Windows

```powershell
python agent/scripts/run_headless_sable.py agent/headless/scenarios/stone_drop.json `
  --instance "C:\path\to\ElyPrismLauncher\instances\6.9.3" `
  --java-home "C:\path\to\jdk-21" `
  --mode full
```

The repository-owned Gradle 8.14.2 wrapper is selected automatically. `--gradlew` remains available only as an explicit override.

## Autonomous blueprint and computer staging

Stage a human-authored Photomancy v1 blueprint in the isolated world's `sable_blueprints` directory with `--blueprint name=path`. A scenario can then place it through the real installed Sable command, for example `execute positioned 0 100 0 run sablebp load vehicle`. The launcher validates the NBT format and records its hash in `agent-results/staged-inputs.json`.

When computer IDs are known from the schematic or an initial discovery run, `--computer-programs computers.json` copies bounded Lua directory trees into the isolated world's CC:Tweaked filesystems before startup:

```json
{
  "schema_version": 1,
  "computers": [
    {"id": 42, "source": "lua/controller"}
  ]
}
```

Paths are relative to the computer manifest. Each source directory is limited to 256 files and 4 MiB. This replaces files only inside the isolated test world.

A scenario may declare bounded `block_probes`. They verify a block after a selected tick and, for a CC:Tweaked computer, record its runtime computer ID, label, power state and directly attached peripheral types:

```json
{
  "id": "controller",
  "dimension": "minecraft:overworld",
  "pos": [0, 100, 0],
  "expected_block": "computercraft:computer_advanced",
  "from_tick": 20,
  "required": true,
  "activate_computer": true,
  "turn_on": true,
  "expected_peripheral_types": ["speaker"]
}
```

`activate_computer` creates the server-side CC computer when an unstarted block still has ID `-1`, allowing the discovery run to assign and persist an ID. `turn_on` boots it in the isolated world. `expected_peripheral_types` makes missing face-adjacent peripherals fail the scenario instead of merely appearing in telemetry.

Use a first discovery run when placement assigns a new computer ID, stage its Lua tree, then run the qualification scenario against the same isolated world with `--reuse-run`. Lua itself must confirm remote wired peripherals through `peripheral.getNames` and `peripheral.getMethods`.

The launcher deliberately accepts the `6.9.3` instance as its version-pinned base. Use `--mode minimal` to diagnose Sable itself. `--mode full` places every enabled server-compatible `.jar` from that instance on the NeoForge runtime classpath. Pure client rendering/UI files listed in `server-excluded-mods.txt` and files ending in `.disabled` are never loaded; neither category participates in dedicated-server physics. Generated worlds, logs, copied configurations, JAR hashes and JSON telemetry stay under `agent-results/` and are not committed.

Pass `--world "C:\path\to\saves\world"` with `record_existing_world.json` to copy an existing world into the isolated server and record its already saved Sable constructions. Stop the client before copying so `level.dat`, region files and Sable storage are from one consistent save. The original world is never modified.

The supplied stone-drop scenario executes the real commands `fill` and `sable assemble area`. This means construction assembly, mass tracking, block collision shapes, server ticks, mod block actors and Sable's Java pipeline are executed by the production runtime. In `minimal` mode Sable loads its packaged native Rapier solver. In the full 6.9.3 stack, `taov_core` deliberately replaces that native library with its bundled Sable-compatible build; retaining that replacement is necessary to reproduce the actual modpack rather than clean Sable in isolation.

## Fidelity boundary

A successful run is live-server evidence for the exact JAR hashes, copied configuration, generated world and commands listed in that run. It is not a timeless 100% guarantee for another client world, a different server configuration, missing datapacks, unloaded chunks or different mod versions. To reproduce a client-world result exactly, copy that world's save, server config and datapacks into the isolated run and keep its mod manifest unchanged.

`run-summary.json` includes `runtime_error_count` and the corresponding server log lines. A passed motion assertion does not hide mod-loading or datapack errors; inspect these diagnostics before calling a specific block behavior verified.

The implementation was live-tested with the full 6.9.3 instance: 112 server JARs produced 168 registered mod IDs, the two-block Sable body had mass 4.0, fell from Y about 200.49 to Y about 42.50 and finished with zero reported linear velocity after 240 ticks. The same run also exposed existing modpack data errors, chiefly unresolved optional loot-table entries and stale physics-property block IDs; those diagnostics remain in the report and are not converted into a false all-mods verification claim.
