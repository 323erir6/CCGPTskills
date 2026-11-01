# Engineering rules for CC:Tweaked reference library

1. Read existing repository documentation and relevant source code before editing.
2. Verify every built-in API using the correct CC:Tweaked version, and every mod API with that mod's source and installed JAR.
3. Never invent methods, numeric units, field names, axis conventions or hardware limits.
4. Separate all documentation prose by language: English only under `docs/en/`, Russian only under `docs/ru/`.
5. Shared executable Lua code may use dual-language comments where necessary, but do not mix English and Russian prose within any language-specific document.
6. Prefer small, verifiable examples. Document exact dependencies and test status.
7. Mark whether methods are source-confirmed, bytecode-confirmed, tested at runtime, or hypotheses.
8. Do not confuse internal Java methods with public Lua API; verify `@LuaFunction` or runtime `peripheral.getMethods`.
9. Use timeouts and bounded operations; validate messages and device capabilities.
10. Preserve backwards compatibility, existing examples and user data.
11. Do not insert personal details, credentials, private conversation excerpts or unpublished assets.
12. For each new API family, supply signatures, units, return schemas, errors, version conditions, examples and tests where feasible.
13. Never claim successful in-game tests unless they were actually executed.
14. Keep index navigation and relative Markdown links valid.
15. Do not copy large upstream documentation or proprietary source files; write independent technical reference material.

English contributor guide: [docs/en/contributing.md](docs/en/contributing.md).
Russian contributor guide: [docs/ru/contributing.md](docs/ru/contributing.md).

## GOCODE agent utilities

For coding-agent tasks, see [agent/AGENTS.md](agent/AGENTS.md) and the independent [English](agent/docs/en/README.md) and [Russian](agent/docs/ru/README.md) implementation guides. These additional instructions do not create an always-on agent or override user permissions.
