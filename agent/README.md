# GOCODE Agent infrastructure

- **English:** [Full implementation and usage](docs/en/README.md)
- **Русский:** [Полная реализация и использование](docs/ru/README.md)
- **AI agent instructions:** [AGENTS.md](AGENTS.md)
- **Structured API manifests:** [api/](api/)
- **ComputerCraft mocks:** [mocks/](mocks/)
- **Deterministic regression cases:** [benchmarks/cases.json](benchmarks/cases.json)
- **Templates for project memory:** [context/](context/)
- **CI workflow:** [gocode-agent-ci.yml](../.github/workflows/gocode-agent-ci.yml)
- **Manual safe autofix:** [gocode-autofix.yml](../.github/workflows/gocode-autofix.yml)

The infrastructure is currently hosted in this repository to keep the reusable CC:Tweaked reference separate from the execution tools within the `agent/` directory. It can be moved to its own repository without changing Python/Lua algorithms, provided the relative `lib/` and `tests/` dependencies are also copied or made available.

## Request-scoped execution / Выполнение задач одного запроса

Use `[goloop]` as a standalone line followed by a checklist of tasks to request continuous build/test/review iterations within a single response. Use `[gostop]` for future-turn deactivation or the UI's Stop generating control to interrupt the ongoing response. This is bounded by available time, tools and permissions; it is not unlimited or asynchronous execution.

Для циклического выполнения задач одного сообщения укажите `[goloop]` отдельной строкой перед списком задач. `[gostop]` отменяет режим для последующих сообщений; текущую генерацию можно прервать штатной кнопкой остановки. Системные ограничения времени и инструментов сохраняются.

## Text-only physics and CC:Tweaked simulator / Физика и CC без графики

- [English: mechanics, models, limitations, commands](docs/en/simulator.md)
- [Русский: механики, точность, ограничения, команды](docs/ru/simulator.md)
- Executable modules: [sim/](sim/); example: [falling_block.lua](scenarios/falling_block.lua).
- Coverage and unimplemented features: [coverage.json](sim/coverage.json).
- Regression tests: [test_world.lua](tests/test_world.lua).

Run: `lua5.3 agent/sim/run.lua agent/scenarios/falling_block.lua`.

## Accurate saved block geometry

- [Create / Photomancy NBT geometry import and collision rules](sim/SCHEMATICS.md)
- [Binary NBT parser](sim/nbt.py) · [source-format adapters](sim/schematics.py) · [voxel SAT collisions](sim/geometry.py) · [compound rigid bodies](sim/rigid.py)
- [Binary NBT regression tests](tests/test_schematics.py) · [rigid-body regression tests](tests/test_rigid.py)

- **Sable 2.0.5 source-matched physics formulas / Формулы физики Sable 2.0.5:** [English](docs/en/sable-2.0.5-physics.md) / [Русский](docs/ru/sable-2.0.5-physics.md).

## Functional mod blocks / Функциональные блоки модов

- [EN: source-grounded functional block models](docs/en/mod-functional-blocks.md)
- [RU: модели функциональных блоков](docs/ru/mod-functional-blocks.md)
- [Complete machine-readable block registry](sim/mod_devices_manifest.json.gz) (gzip-compressed JSON; actual installed modpack, 11,149 IDs, 51 modeled)
- CLI example: `python3 -m agent.sim.mod_cli agent/scenarios/mod_blocks.json --out agent-results/mod_blocks.json`.
- The registry includes unknown/decorative blocks; **51 behavioral models does not imply full mod compatibility**.
