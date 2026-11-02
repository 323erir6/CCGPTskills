# Autonomous execution loop

Use this loop for one technical specification. Persist state in `autonomy-state.json` so a new chat can continue from evidence instead of restarting.

## 1. Contract

- Convert every normative requirement into one acceptance criterion with a stable ID.
- Give each criterion a `measurement`, numerical or observable `pass_condition`, `minimum_trials`, and required evidence kinds. The manifest validator rejects vague criteria.
- Require `live_server` evidence for physical motion, mod peripherals, networking, tick timing, ammunition, projectiles, fuzes, collisions, or damage.
- Require `client` only for rendering, touch input, sound, camera, or another client-only behavior.
- Record assumptions. Resolve them from source, installed JARs, runtime inspection, or experiments rather than asking the user when the choice does not change the requested product.

## 2. Preflight

- Validate every schematic and its device connection contract.
- Verify exact block IDs, construction membership, computer/peripheral adjacency, wired topology, orientation, clearance, and required moving parts.
- Audit source or installed JAR bytecode for every mod API not already source-confirmed.
- If the schematic is defective, run `schematic-issue`, provide the file, construction, coordinates, actual and expected condition, consequence, and smallest human correction. Pause only affected live tests.

## 3. Implement

- Work on a topic branch and preserve existing interfaces unless the specification changes them.
- Keep hardware mapping, control algorithms, networking, UI, and test instrumentation separable.
- Add deterministic tests for pure logic and each reproduced defect.
- Make processes bounded and restartable. Persist calibration and measurements as data, not undocumented constants.

## 4. Verify from cheap to exact

1. Syntax and static checks.
2. Pure unit tests and CC:Tweaked mocks.
3. Synthetic schematic/physics checks for fast regressions.
4. Native Rapier checks where they answer a narrower collision question.
5. Real isolated NeoForge 6.9.3 headless tests for actual server behavior.
6. Client tests only for behavior a dedicated server cannot execute.

Record evidence using `autonomous_project.py record`. A failed test changes the implementation or hypothesis and starts another iteration. Do not repeat an unchanged failing action.

## 5. Qualification

- Reset or copy a clean isolated world between trials when state affects outcomes.
- Automate target setup, program deployment, startup, operation, telemetry, hit classification, cleanup, and summary generation.
- Use fixed seeds for regression tests and varied documented seeds for statistical qualification.
- Record misses and failures, not only successes. Calculate the metric exactly as specified.
- Inspect TPS and server errors so a nominal result does not hide runtime corruption.

## 6. Completion

The project is complete only when the evidence gate passes every criterion. A final report must distinguish verified, failed, partial, and client-only/not-run results. If the platform terminates before completion, preserve the manifest, state, logs, and next executable command; do not redefine partial work as completion.

Evidence is bound to the current technical specification, schematics, connection contract, runtime profile, and criteria. A changed input invalidates older records. For each criterion and evidence kind, the newest result supersedes earlier results, so a new failure reopens the gate.
