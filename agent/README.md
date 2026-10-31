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
