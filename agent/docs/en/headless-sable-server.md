# Real Sable headless server

The headless path runs an actual NeoForge 21.1.248 dedicated server with Minecraft 1.21.1, the original Sable 2.0.5 JAR and either the complete enabled mod directory or a minimal Sable-only runtime. It does not reimplement Sable equations.

`agent/headless` contains a server-only telemetry mod. A bounded JSON scenario schedules normal server commands, then records every loaded Sable sublevel after completed server ticks: pose, scale, linear and angular velocity, Sable mass, center of mass and world bounds. The report also records the mod IDs and versions loaded by NeoForge. The Python launcher creates an isolated server directory, copies configuration inputs, hashes every enabled JAR and stops the server when the scenario ends.

## Run on Windows

```powershell
python agent/scripts/run_headless_sable.py agent/headless/scenarios/stone_drop.json `
  --instance "C:\path\to\ElyPrismLauncher\instances\6.9.3" `
  --gradlew "C:\path\to\another-neoforge-project\gradlew.bat" `
  --java-home "C:\path\to\jdk-21" `
  --mode full
```

The launcher deliberately accepts the `6.9.3` instance as its version-pinned base. Use `--mode minimal` to diagnose Sable itself. `--mode full` places every enabled server-compatible `.jar` from that instance on the NeoForge runtime classpath. Pure client rendering/UI files listed in `server-excluded-mods.txt` and files ending in `.disabled` are never loaded; neither category participates in dedicated-server physics. Generated worlds, logs, copied configurations, JAR hashes and JSON telemetry stay under `agent-results/` and are not committed.

Pass `--world "C:\path\to\saves\world"` with `record_existing_world.json` to copy an existing world into the isolated server and record its already saved Sable constructions. Stop the client before copying so `level.dat`, region files and Sable storage are from one consistent save. The original world is never modified.

The supplied stone-drop scenario executes the real commands `fill` and `sable assemble area`. This means construction assembly, mass tracking, block collision shapes, server ticks, mod block actors and Sable's Java pipeline are executed by the production runtime. In `minimal` mode Sable loads its packaged native Rapier solver. In the full 6.9.3 stack, `taov_core` deliberately replaces that native library with its bundled Sable-compatible build; retaining that replacement is necessary to reproduce the actual modpack rather than clean Sable in isolation.

## Fidelity boundary

A successful run is live-server evidence for the exact JAR hashes, copied configuration, generated world and commands listed in that run. It is not a timeless 100% guarantee for another client world, a different server configuration, missing datapacks, unloaded chunks or different mod versions. To reproduce a client-world result exactly, copy that world's save, server config and datapacks into the isolated run and keep its mod manifest unchanged.

`run-summary.json` includes `runtime_error_count` and the corresponding server log lines. A passed motion assertion does not hide mod-loading or datapack errors; inspect these diagnostics before calling a specific block behavior verified.

The implementation was live-tested with the full 6.9.3 instance: 112 server JARs produced 168 registered mod IDs, the two-block Sable body had mass 4.0, fell from Y about 200.49 to Y about 42.50 and finished with zero reported linear velocity after 240 ticks. The same run also exposed existing modpack data errors, chiefly unresolved optional loot-table entries and stale physics-property block IDs; those diagnostics remain in the report and are not converted into a false all-mods verification claim.
