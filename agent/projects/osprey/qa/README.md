# GOCODE read-only flight instrumentation and native physics QA

This addition is for an **unarmed test object / safe flight-test environment**. It
contains no command transmitter, propulsion sequence, fin actuation, player
tracking, trajectory optimizer, ballistic solver, or mission/target controller.

## On-board data recorder

Copy `lua/flight_recorder.lua` and `lua/recorder_config.example.lua` to a
CC:Tweaked computer connected to a CC:Sable compatible physical sublevel.
Rename the config to `recorder_config.lua`. Run:

```
flight_recorder
```

It writes `sable_flight_log.jsonl`, with sample sequence, monotonic local runtime,
position (world blocks), quaternion (xyzw), linear and angular velocities, and
status of CC:Sable readings. It **never** sets engine power or flap angles and
does not open a modem. Defaults: 10 samples/second, 600 samples.

For each new test, choose a new output filename: the recorder will not append
to or overwrite an existing log.

Transfer JSONL from the computer to a test workstation and check:

```
python -m agent.projects.osprey.qa.flight_log sable_flight_log.jsonl \
    --min-samples 10 --max-gap 1.0 --out log-validation.json
```

Bad sensor frames, missing values, NaN, Infinity, invalid quaternions, out-of-order
samples, time gaps, contradictory vehicle IDs, missing lines and malformed JSON
fail the integrity checks. A passed log only means its **recorded fields were
internally consistent**, not that the physical trajectory was accurate.

## Generic original-Sable JNI integration

Use the **exact** user-owned `sable-neoforge-1.21.1-2.0.5.jar` and JDK 21:

```
python -m agent.projects.osprey.qa.native_recorder_fixture \
    --jar /path/to/sable-neoforge-1.21.1-2.0.5.jar \
    --log /tmp/inert-cube.jsonl --report /tmp/inert-cube-report.json
```

The runner uses the original Rapier physics solver and an inert 1x1x1 cube.
No attempt is made to characterize any weapons, payloads or target accuracy.
This native fixture is **not a substitute for in-game CC:Sable telemetry**.

## Qualification discipline

Until a separately reviewed non-destructive test has logs from the actual game,
the report must retain `actual_game_equivalence=unverified` and
`release_qualified=false`. The test suite cannot certify navigation accuracy,
range, or safe use of modded propulsion mechanisms.

## Test suites

```sh
python -m unittest discover -s agent/projects/osprey/tests -p "test_*.py" -v
(cd agent/projects/osprey/lua && lua5.3 ../tests/test_recorder.lua)
```

The Java/JNI integration test is optional and requires setting `GOCODE_SABLE_JAR` to the original modpack JAR.
