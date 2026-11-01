# Passive Sable / Minecraft physics parity gate

**Scope:** non-powered, non-weapon, one-block free fall and ground contact only. It does not evaluate guided flight, a strike point, engine control, or tracking of people/entities.

This gate fixes a serious validity gap: successful source-matched Rapier JNI tests do **not** establish equality with the installed Minecraft server. The gate is deliberately **fail closed** when actual Minecraft measurements are absent.

## 1. Run actual native tests

```bash
python3 -m agent.validation.native_conformance \
  --jar /path/to/sable-neoforge-1.21.1-2.0.5.jar \
  --cases 12 --runs 5 --output agent-results/native-passive.json
```

The JSON now records the full 3D final velocity of every body, in addition to final position and scalar speed. This is a regression-sensitive schema addition.

## 2. Capture real in-game measurements

For the *same* 12 inert test blocks and five independent runs, record the initial XYZ, block mass, final XYZ and full XYZ velocity after 4 seconds. Use the actual CC:Sable or another verifiable source, and ensure each sample is aligned by server **physics ticks**, not `os.clock()` or assumed timing. Do not generate or backfill the live results by copying or simulating the native states.

Supply a separate JSON file containing:

```json
{
  "schema_version": 1,
  "source": "minecraft_live",
  "capture_method": "cc_sable_passive_contact",
  "time_basis": "verified_server_ticks",
  "test_scope": "generic one-block free fall and ground contact ONLY",
  "world_surface_y": 168,
  "gravity_y": -11,
  "modpack_fingerprint": "RECORD_FROM_INSTALLED_MODPACK",
  "world_config_fingerprint": "RECORD_FROM_SERVER_CONFIG",
  "sable_jar_sha256": "SAME_HEX_SHA256_AS_NATIVE_REPORT",
  "measurements": []
}
```

Every `measurements` element requires `run` (positive integer), `case` (positive integer), `mass`, `initial_position: [x,y,z]`, `final_position: [x,y,z]`, and `final_velocity: [vx,vy,vz]`. The empty array above is *only a schema illustration*, not a sample that can qualify. Live evidence must be collected independently; matching labels alone cannot cryptographically authenticate measurements.

## 3. Run the comparison

```bash
python3 -m agent.validation.live_parity \
  --native agent-results/native-passive.json \
  --live agent-results/minecraft-passive.json \
  --out agent-results/passive-parity.json
```

Without `--live`, the module writes `status: not_qualified`, adds a missing-evidence issue and returns exit code 1. It also rejects mismatched initial conditions, inconsistent JAR fingerprints, missing game timing evidence, incomplete repeats, non-finite values and discrepancies above explicit tolerances. `passive_parity_consistent` means only that **supplied, self-reported observations** agree within thresholds for the tested passive scenario; it does not establish that the data are authentic or that other flight modes match.

**No rocket, moving-target, weapon accuracy or full Minecraft-mod equivalence claim can be derived from these checks.**
