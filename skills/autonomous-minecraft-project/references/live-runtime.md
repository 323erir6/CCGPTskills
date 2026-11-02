# Real runtime and evidence

Use `agent/scripts/run_headless_sable.py` with the exact 6.9.3 instance for server-side qualification. It runs Minecraft 1.21.1, NeoForge 21.1.248, Sable 2.0.5, and the enabled server-compatible mod JARs in an isolated directory. No paid remote server is required.

## Runtime rules

- Never modify the user's source world. Copy it or generate a dedicated test world.
- Hash enabled JARs and preserve configs, datapacks, scenario, server log, run summary, and telemetry report.
- Use `full` mode for modpack qualification. Use `minimal` only to isolate clean Sable behavior.
- Treat data-pack errors, unknown block IDs, mixin conflicts, TPS stalls, and missing mods as test findings.
- A passed assertion does not erase server errors.
- Reuse an isolated run only when the scenario deliberately needs persistent state; otherwise start clean.
- Stage supplied Photomancy blueprints with `--blueprint name=path` and place them with the real `sablebp load` command.
- Use bounded `block_probes` to discover CC computer IDs and verify expected blocks after placement. Stage Lua with `--computer-programs`, then run qualification against the same isolated copy.
- Record verified `live_server` evidence as a JSON qualification report with `status: passed`, the actual `trials` count, measured results, and `runtime_summary` pointing to the full-mode `run-summary.json`. The gate checks the linked headless report and exact Sable/CC runtime versions.

## Agent environment

The chat agent needs filesystem access, Python, Java 21, enough memory, process execution, the CCGPTskills repository, and a complete user-owned 6.9.3 instance or equivalent portable instance layout. If these are present, absence of a graphical client is not a blocker for server physics.

If process execution is genuinely unavailable, prepare reproducible inputs and report `not_executed`; never manufacture results. This is an execution-environment limitation, not a simulator-accuracy conclusion.

## Evidence classes

- `static`: source, bytecode, schemas, syntax, topology.
- `unit`: deterministic program logic.
- `synthetic`: approximate CCGPTskills world/device model.
- `native`: original Rapier component executed with verified inputs.
- `live_server`: actual NeoForge/mod code executed and logged.
- `client`: graphical/input/audio behavior executed in a client.

Physical acceptance criteria normally require `live_server`, even when earlier layers pass.
