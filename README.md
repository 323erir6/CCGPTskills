# CC:Tweaked Offline Development Reference

Choose one **independent language tree**. Documentation and method books do not mix English and Russian in the same file.

- **[English documentation / EN](docs/en/INDEX.md)**
- **[Русская документация / RU](docs/ru/INDEX.md)**

Source-backed ComputerCraft/CC:Tweaked Lua reference for Minecraft 1.21.1 NeoForge, core CraftOS APIs, CC:Sable, NeoPeripheral, CBC peripheral integrations and other mod-pack add-ons. Includes reusable Lua modules, examples, test cases and a complete pack-archive audit.

Executable Lua helpers are shared under [lib/](lib/). Documentation prose is separate in `docs/en/` and `docs/ru/`. API support is version-specific and must be verified against installed devices.

## Ordinary ChatGPT Chat

The simulator includes a bounded, data-only Python runner that works without Lua:

```sh
python -m agent.sim.chat_runner chatgpt/examples/drop_test.json --pretty --out report.json
```

- [ChatGPT project instructions](chatgpt/en/PROJECT_INSTRUCTIONS.md)
- [Короткий запуск українською](chatgpt/uk/QUICKSTART.md)
- [Reusable Sable simulator skill](skills/sable-simulator/SKILL.md)
- [Minecraft-only scope in English](docs/en/game-scope.md) / [по-русски](docs/ru/game-scope.md)

Build the single-file upload bundle with `python agent/scripts/build_chatgpt_bundle.py`. GitHub Actions publishes the same ZIP as an artifact. ChatGPT must have Python/data-analysis execution to run the simulator inside a chat; otherwise it can prepare a scenario but must label it as not executed.

For the highest local fidelity, [the headless NeoForge runner](agent/docs/en/headless-sable-server.md) starts the real version-pinned 6.9.3 Minecraft 1.21.1 dedicated-server stack with the user's original Sable 2.0.5 and server-compatible mod JARs. It records Sable telemetry and exact JAR hashes instead of reimplementing mod forces.

## GOCODE engineering tools

- **[Coding-agent infrastructure / EN](agent/docs/en/README.md)**
- **[Инструменты программного агента / RU](agent/docs/ru/README.md)**

Includes source-verified JSON API manifests, deterministic CC:Tweaked mocks, regression testing, GitHub Actions, branch/PR workflow templates and engineering context files. No autonomous model service is bundled.
