# GOCODE Agent — implementation and operating reference

This reference implements a zero-additional-fee, GitHub-based engineering workflow for CC:Tweaked / NeoForge projects. It does not contain an autonomous paid model runtime. The language-specific companion is located at [Russian reference](../ru/README.md); documents are kept in independent language directories.

## 1. Code → CI → diagnosis → correction → review

**Completed infrastructure:** `.github/workflows/gocode-agent-ci.yml` runs on relevant pushes and pull requests. The job syntax-checks Lua files, executes Python unit tests, runs deterministic Lua benchmarks and publishes a JSON report artifact. The existing `lua-ci.yml` remains unchanged.

**Human/assistant reasoning cycle:** inspect the CI run; read the failing job and logs; record a concrete hypothesis; modify a dedicated branch; rerun checks; review the diff; repeat until the actual tests pass or blockers are documented. There is no unattended model reasoning when the chat is closed. Failure-log categorization is available through `python3 agent/scripts/diagnose.py path/to/log.txt`.

**Deterministic autofix:** `.github/workflows/gocode-autofix.yml` is manually dispatched. It formats Python under `agent/`, creates a new branch and opens an unmerged PR if formatting changes exist. It never changes Lua algorithms or guesses how to repair an exception. GitHub may require enabling `Settings → Actions → General → Allow GitHub Actions to create and approve pull requests` and write permissions. Do not enable arbitrary third-party PR code with write tokens. See GitHub's official Actions permissions documentation.

## 2. Machine-readable API reference

`agent/api/*.json` stores exact Minecraft/mod versions, upstream repository, source commit, exposed peripheral/global API, each method's Lua-visible arguments and results, verification status and the implementation file. Version-qualified manifests are deliberately distinct from the human documentation.

**Verification levels:**

- `source-confirmed`: traced to Java `@LuaFunction` or the implementation that exposes the method.
- `documentation-confirmed`: supported by a version-matched upstream reference, but no source inspection recorded.
- `runtime-confirmed`: explicitly checked against an installed CraftOS device in Minecraft.
- `unverified`: hypothesis; must never be treated as a stable API.

Run `python3 agent/scripts/validate_api.py` before publishing changed manifests. It checks structure and obvious inconsistencies, not whether the Java implementation actually matches; upstream source inspection is still required. Current manifests were created from available source snapshots of Programmable Fuzes 1.4.1, Enhanced Detector Radar 1.0.5, Sable CC Tick Sync 1.6.4, and Mianbao Sable Explosion Compat 1.2.9.

## 3. Offline mock simulation — exact implementation

The mock runtime is **not Minecraft**, not an implementation of all CraftOS, and not a real Sable physics simulator. It supplies deterministic stand-ins for a small subset of APIs, allowing unchanged pure Lua logic to be exercised.

| Mock | Implemented behavior | Deliberately missing |
| --- | --- | --- |
| `agent/mocks/peripheral.lua` | Attach/detach, enumerate types/methods, wrap/find/call | Java-side invocation scheduling and capabilities |
| `agent/mocks/clock.lua` | Controlled time, timer IDs and queued events | Real wait/parallel scheduling, full event filters |
| `agent/mocks/rednet.lua` | Two or more simulated computers, message filtering, optional dropped packet | Wireless topology, delays, encryption |
| `agent/mocks/redstone.lua` | Boolean/analog outputs, bounds and history | World block changes and powering behavior |
| `agent/mocks/sublevel.lua` | Synthetic pose and velocity snapshots | Physics integration, collisions, constraints |

Example:

```lua
local Mock = require('agent.mocks.sublevel')
local transform = require('lib.sublevel_pose')
local ship = Mock.new()
ship:setVelocity({x=0,y=0,z=20})
local state = ship:api()
local p = transform.localToWorld({x=2,y=3,z=4}, state.getLogicalPose())
assert(p.x == 2 and p.y == 3 and p.z == 4)
```

The mocks can be extended with motion models, delay queues and fault injection **only after defining expected behavior**. Physical time steps, quaternions, field conventions and external peripheral signatures must be validated with the installed versions. Execute Lua tests with `lua5.3 agent/tests/test_mocks.lua` and `lua5.3 agent/tests/test_integration.lua` from repository root. CraftOS-PC can supplement this but does not automatically implement modded peripherals.

## 4. Source/JAR analysis on the assistant's side

Use connected GitHub repository reads and a temporary analysis environment to inspect source snapshots and JAR internals **without needing local installation or additional software on the user's computer**. Inspect `@LuaFunction`, `ILuaAPI`, `IPeripheral`, `GenericPeripheral`, method registrations, capabilities, bytecode and variant-specific return fields. Reconcile source and installed JAR version and document mismatches. If the binary cannot be read or is too large, explicitly report the limitation. Do not dump proprietary Java source or uploaded binaries into this repository without permission. No GitHub Action automatically uploads or analyzes modpack archives.

## 5. Independent review

After implementation, review the complete diff independently of the initial implementation plan: correctness, edge cases, false assumptions about APIs, thread safety, untrusted input, authorization, resource leaks, compatibility, performance and scope. `agent/scripts/review.py` provides only a small high-signal Lua heuristic scanner; it is not CodeQL or a full security audit. For NeoForge/Java projects, use the build/test template and optionally add CodeQL as a separate workflow in the **Java source repository**.

## 6. Persistent engineering context

`agent/context/*.template.*` supplies templates for architecture, interface assumptions, development state and known issues. Create project-local copies and update them with **confirmed** information; each claim should link to source, test or commit. Never treat outdated notes as newer than the current branch. This survives new conversations because it lives in GitHub.

## 7. Topic branches and pull requests

Use a topic branch for substantial changes; use `.github/pull_request_template.md` as a review checklist. CI gates are visible in each PR. Do not modify default branch directly or merge automatically without the required authorization; branch protection must be configured separately by a repository administrator if desired.

## 8. Measurable evaluation

`agent/benchmarks/cases.json` enumerates deterministic tasks. `agent/scripts/benchmark.py --output agent-results/benchmark.json` executes them, records pass/fail, duration and output. Results are attached to CI as artifacts; passing checks establishes a measurable regression baseline for the tested behaviors, **not** general GPT intelligence. Add a reproducing case for every important fixed bug.

## 9. Automatically selected work modes

`agent/AGENTS.md` defines research, architect, implement, debug, test, review, refactor and release modes. The assistant selects and switches modes according to the nature of the task, while explicit manual selection overrides the automatic routing. Activating the overall GOCODE workflow is separate from selecting a mode. No background watcher or local always-on agent is installed.

## 10. Reproducible artifact building

`agent/templates/java-neoforge-ci.yml` is a reusable GitHub workflow for building Java 21 NeoForge projects with Gradle and uploading `.jar` files. `agent/templates/python-ci.yml` demonstrates Python tests. These templates are **not** automatically installed in every repository; copy/adapt them to the project being built. No deployment, release or auto-merge is performed without authorization.

## Free-cost boundary

GitHub standard hosted runners are generally free for public repositories, subject to service limits. Private repositories receive included allowances, and paid runner/storage scenarios may apply. The code and mocks use Python stdlib and system Lua 5.3; optional formatters and emulators are freely available. Hosted ChatGPT/API model inference is *not* included in free GitHub Actions compute.

## 11. [goloop] — continuous execution for a checklist

Start a user-authored request with the exact standalone marker `[goloop]` and place all tasks after it, one per line or as a numbered list:

```text
[goloop]
1. Implement the change in a topic branch.
2. Reproduce the reported failure with an automated test.
3. Fix failing checks, inspect the CI logs and review the diff.
4. Open a pull request with evidence of passing tests.
```

The marker is **request-scoped**: it automatically selects the GOCODE engineering workflow for the listed tasks without requiring the persistent `gocode` trigger. For each item establish observable acceptance criteria, keep a checklist and iterate through analysis, code, tests and correction while tools and response execution are available. Shift engineering modes automatically; an explicitly requested mode takes precedence.

Treat `verified`, `partial`, `blocked` and `not tested` as different outcomes. Do not stop merely because the first build succeeded if a listed task remains actionable. Conversely, do not enter an unbounded retry loop or claim a task is 100% complete without adequate evidence. External Minecraft integration tests that were not run must be reported as not tested. Report blockers and exact next actions if resources, permissions or tools prevent further progress.

**Stop control:** use the interface's Stop generating control to interrupt an active response. A later `[gostop]` or `gostop` message disables future execution-loop instructions (and `gostop` also disables GOCODE). These text commands do not provide a communication channel into a still-running generation. The platform can terminate or limit any request; the marker cannot override those limits or schedule background work.

## 12. Versioned text-only simulation world

The incremental voxel, rigid-body and CC:Tweaked simulator has an independent [English specification](simulator.md) and a machine-readable [coverage manifest](../../sim/coverage.json). Its physics are explicitly approximate. It is used for reproducible regression tests, not as proof of live Minecraft compatibility.

## 13. Original native Sable Rapier integration

See [Sable 2.0.5 native JNI bridge](native-sable-rapier.md) for actual voxel contact and rigid-body physics execution. Native physics is tested separately from approximate mod behavior; an in-game equality claim requires an end-to-end server trace.
