# Original Sable 2.0.5 native Rapier, text-only JNI harness

**Status:** original native solver connected and tested; **full-game rocket fidelity remains unverified**.

This harness uses the *unmodified* precompiled native library from the user's **Sable NeoForge 1.21.1 v2.0.5 JAR**. It extracts the Linux x86_64, Windows x86_64, or macOS x86_64 library from the version-pinned nested JAR using LZ4, compiles a small Java JNI client, and talks to it through stdin/stdout. No renderer or Minecraft graphical client is involved. **Do not commit the original native binaries or mod JAR to this repository.**

Native library provenance:
- Sable tag: <https://github.com/ryanhcode/sable/tree/mc1.21.1-2.0.5-neoforge>
- Rust source for the exact native library: `sable_rapier/src/main/rust/rapier/src/`
- Pinned fork of Rapier: <https://github.com/ryanhcode/rapier/tree/38e92f117590862481a53df6fc69a5d893e29186>
- Runtime library path inside installed mod JAR: `META-INF/jarjar/dev.ryanhcode.sable.sable-sable_rapier-1.21.1-2.0.5.jar`, then `natives/sable_rapier/sable_rapier_binaries.zip.l4z`.

## Covered by actual native code

`agent/native/src/NativeHarness.java`, with JNI class `Rapier3D.java`, invokes the original functions `initialize`, `newVoxelCollider`, `addVoxelColliderBox`, `createSubLevel`, `setLocalBounds`, `setCenterOfMass`, `setMassProperties`, `addChunk`, `applyForceAndTorque`, `step`, `getPose`, `getLinearVelocity`, `getAngularVelocity`, `clearCollisions`, and `dispose`.

The bridge creates **real Sable sublevels** with **individual voxel shapes**, populates sections of the main level and moving sublevels, processes native rigid-body rotations and angular impulses, and reads native collision events and their contact coordinates. For the smoke test, the source-format section positions and contact states are set to yield a functioning, source-verified native collision between a falling grass voxel and the grass terrain layer at Y=167. The original native solver settles the center near Y=168.497. This is **not** the previous Python plane-collision approximation.

**Important:** `NativeHarness` currently marks imported voxels as physics-state `Edge` (index 2 in `ALL_VOXEL_PHYSICS_STATES`). Real Sable classifies block physics states based on their neighbors. Accurate per-block `Face`/`Edge`/`Corner`/`Interior` classification and registry-provided modded `VoxelShape` inputs are still needed for full in-game collision parity. In isolated native tests setting a custom body or a ground block to `Face` instead of `Edge` caused missing contacts; the harness must not silently claim full compliance.

## Run

Prerequisites: Java JDK 21, Python 3.11+, `lz4`, `numpy` and `scipy`, plus your own Sable JAR.

```sh
python -m pip install lz4 numpy scipy
python -m agent.sim.native_rapier --jar /path/to/sable-neoforge-1.21.1-2.0.5.jar --smoke --output agent-results/native-smoke.json
python -m agent.sim.native_rocket rszo_rocket_v0.nbt --jar /path/to/sable-neoforge-1.21.1-2.0.5.jar --max-seconds 60 --out agent-results/native-rocket.json
```

Windows PowerShell:

```powershell
py -m pip install lz4 numpy scipy
py -m agent.sim.native_rapier --jar .\mods\sable-neoforge-1.21.1-2.0.5.jar --smoke
```

The bridge compiles automatically to `agent/native/build/`. The library and build contents are ignored by Git and should not be committed.

### Confirmed local tests on user's supplied archive

- The extracted **original Sable native library** initializes a scene, creates a sublevel and a world terrain, runs 40 steps per second and provides pose/velocity and contact reports.
- Native grass voxel drop onto Y=168 world surface: **final body center Y≈168.497, zero velocity**.
- **Native-backed rocket probe**, using the uploaded Photomancy blueprint (`rszo_rocket_v0.nbt`), six occupied blocks (each currently approximated by a full cube), source-derived gravity/drag and an external engine/sail force adapter: first native ground contact **t=14.825 s**, one native contact point reported near `(0,168,3374)`. Center of mass at contact approximately `(-0.709,168.713,3373.365)`.
- Repeated probe produced matching results on the same test host.

### What is still approximate, and why

The **native Sable Rapier solver is now real**, but the *complete simulator is not the actual Minecraft server*.

1. The six blocks and their relative positions come from the blueprint, but some **modded collision shapes**, VoxelPhysicsState classification, Sable's per-block masses and inertia tensors are not yet extracted from real running registries. The current native rocket case uses six full cubes, mass 4.5 and a uniform-cuboid inertia tensor.
2. Create Propulsion's thruster is modeled with a 230-unit body-frame impulse source, 0.5 s startup ramp and 800 s burn. Actual control flags, redstone, damage and fuel logic are not executed inside Minecraft.
3. The two symmetric sails use source-derived pressure and drag coefficients, but their exact event scheduling, lift provider group behavior and network-side block updates are not reproduced.
4. The synthetic superflat ground is a dynamically populated 1-layer plane; the loaded Java Minecraft world's full chunk/collision state and HE fuze/detonation are absent.
5. JDK/Rust native floating-point and thread scheduling can produce small platform differences. A native contact event is **not proof** that its world coordinate matches a particular player-run server configuration.

**Remaining work for exact in-game behavior:** generate actual modded collision shape and mass/physics-state data from Minecraft registries, faithfully execute mod-side block tick/force-provider logic and validate against captured in-game traces. A fully exact alternative is a text-only NeoForge dedicated-server test mod using the same installed modpack and physics pipeline. Do not label the coordinates from this interim adapter as certified Minecraft outcomes.

### Tests

```sh
python -m unittest agent.tests.test_native_rapier_bridge -v
GOCODE_SABLE_JAR=/path/to/sable-neoforge-1.21.1-2.0.5.jar python -m unittest agent.tests.test_native_rapier_bridge -v
```
