# Documentation contribution standards

Maintain a self-contained, source-traceable CC:Tweaked library intended to function even when external documentation sites are unavailable.

## Required evidence and content

Every mod-specific API page should include:
1. Exact installed JAR name, mod ID and version where known.
2. Source repository and commit or immutable class-based version evidence.
3. Whether the interface is a global Lua API, generic peripheral, ordinary IPeripheral, Mixin extension or unrelated physics patch.
4. Exact Lua method names, argument types and order, injected vs actual Lua arguments, return values and error conditions.
5. Table schemas with field names, type, units, optionality and coordinate-frame conventions.
6. Server options, ranges, permissions and hardware prerequisites.
7. Small self-contained examples using available APIs; avoid placeholders disguised as implementations.
8. Version changes and interactions with other installed mods.
9. Tests, expected results and honest verification status.

## Language isolation

English prose and English examples are placed under `docs/en/`. Equivalent Russian prose is maintained separately under `docs/ru/`. The same method names, signatures, numeric limits and return fields must appear in both language editions. Code modules under `lib/` are shared functional source, not language editions.

## Reliability

Use `peripheral.getMethods` to establish actual on-device capabilities. Java bytecode method names do not automatically establish Lua export. Any direct device-state change should be guarded by validation and appropriate server authorization. Cite upstream sources without copying lengthy external manuals.

## Regression checks

A CI pass covers static Lua syntax and deterministic pure-math tests only; physical device methods require in-game tests. Do not claim those occurred unless there is test evidence.