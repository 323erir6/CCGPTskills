# Native Sable 2.0.5: generic contact repeatability validation

This is a **non-weapon, text-only physics QA benchmark**, not a guided-flight or
Minecraft parity certification. It uses the original Sable 2.0.5 Rapier JNI
library extracted from the trusted local mod JAR. The original native binaries
and modified Minecraft mod files are not distributed with GOCODE.

## Procedure

- Twelve independent 1x1x1 homogeneous voxel solids (four masses and varying
  heights) are placed over the terrain surface at Y=168.
- Each scene simulates 160 substeps of 1/40 second; original Sable gravity -11
  and damping 0.09 are passed to the native solver.
- Three scenes are run from the same inputs, yielding 36 independent fall/contact
  checks. Note: three repeated scenes is not a statistical accuracy validation.
- Reports vertical rest-position error relative to Y=168.5, horizontal numerical
  drift, final speed and run-to-run position difference for each cube.
- Hard-fail on missing JAR, non-finite native readings, excessive drift,
  missing case IDs or non-deterministic results.

## Run

```sh
python3 -m unittest agent.tests.test_native_conformance -v
python3 -m agent.validation.native_conformance \
  --jar /path/to/sable-neoforge-1.21.1-2.0.5.jar \
  --runs 3 --cases 12 --output agent-results/native-conformance.json
```

**Acceptance windows for this restricted benchmark only**: vertical error
<=0.035 m, horizontal drift <=0.25 m, terminal speed <=0.02 m/s and
repeatability difference <=0.01 m. The native engine's inherent correction
thresholds prevent treating a 0.035-m acceptance window as exact physics parity.

The report **always** contains `game_equivalence: "unverified"` and
`guidance_accuracy: "not tested (out of scope)"`. These are not elevated by a
passing CI status. Modded block shapes, original Java block-entity updates,
chunk loading, device forces and in-game sensor APIs are outside this test.
