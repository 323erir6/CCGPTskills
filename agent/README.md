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
