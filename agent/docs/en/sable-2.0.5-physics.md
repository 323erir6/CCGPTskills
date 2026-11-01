# Source-pinned physics: Sable 2.0.5 / NeoForge / Minecraft 1.21.1

This reference is tied to **the user's modpack JAR** `sable-neoforge-1.21.1-2.0.5.jar`, SHA-256 `c8710f85bc780bbf523e6726ceaaf76dd0b8c61479db497b382c6bb34317e7ab`. The nested `sable_rapier` Java JAR contains the original native Rapier libraries for supported platforms; the simulator **does not redistribute or execute** these binaries.

Exact source versions:
- [Sable tag `mc1.21.1-2.0.5-neoforge`](https://github.com/ryanhcode/sable/tree/mc1.21.1-2.0.5-neoforge), release commit `6966d29`.
- Sable native [Rust `lib.rs`](https://github.com/ryanhcode/sable/blob/mc1.21.1-2.0.5-neoforge/sable_rapier/src/main/rust/rapier/src/lib.rs) and [contact hooks](https://github.com/ryanhcode/sable/blob/mc1.21.1-2.0.5-neoforge/sable_rapier/src/main/rust/rapier/src/hooks.rs).
- Rapier is a **fork**, pinned by Sable's `Cargo.toml` to [`38e92f117590862481a53df6fc69a5d893e29186`](https://github.com/ryanhcode/rapier/tree/38e92f117590862481a53df6fc69a5d893e29186), not an arbitrary current release.

## Source-confirmed constants

| Physical property | Default | Source |
|---|---:|---|
| Gravity, Overworld | `(0,-11,0)` blocks/s² | Sable `DimensionPhysics.DEFAULT_GRAVITY` |
| Universal linear and angular drag | `0.09` | Sable `DimensionPhysics.DEFAULT_UNIVERSAL_DRAG`, Rust `set_linear_damping` |
| Physics substeps per game tick | `2`, hence **40 Hz** at 20 TPS | Sable `SableServerConfig` |
| Dynamic sublevel collider friction | `0.525` | Sable Rust `createSubLevel` |
| Main-world collider friction | `1.0` (Rapier default) | Sable Rust main-level collider + Rapier `ColliderMaterial::default` |
| Per-block friction multiplier | `1.0` (unless configured) | Sable `PhysicsBlockPropertyTypes.FRICTION` |
| Restitution | `0` (unless configured) | Sable block-property default |
| CCD maximum substeps | `3` | Sable native `integration_parameters` |
| Contact spring frequency / damping ratio | `30` / `5` | Sable native parameters |

The Java `PhysicsConfigData` describes solver iterations and internal PGS/stabilization defaults; runtime settings can override these. The original native physics pipeline uses more than these scalar constants.

## Original formulas adopted in Python

The fork's `RigidBodyVelocity::apply_damping` **does not use exponential decay**. For each component:

```text
v_after = v_before / (1 + damping * dt)
```

For an unconstrained body, the fork integrates position using the new physical velocity **before the post-step damping writeback**. See fork `velocity_solver.rs` and `rigid_body_components.rs`:

```text
v_pre = v_old + gravity * dt
x_next = x_old + v_pre * dt
v_next = v_pre / (1 + damping * dt)
```

For the fork's **default Average** friction combine rule and the two Sable colliders:

```text
mu_contact = ((0.525 + 1.0) / 2) * block_multiplier_A * block_multiplier_B
           = 0.7625     (with default block multipliers 1.0)
```

Coulomb friction bounds contact tangential impulse by `abs(J_t) <= mu_contact * J_normal`. The actual Rapier solver computes tangential and normal impulses per contact point, with angular effective mass, stabilization, warmstarting and iterative constraints. Our `World` terrain implementation **only approximates** that solver using a plane and `mu * gravity * dt`. Do not equate those two algorithms.

## Simulator interface and validation

Use `World(profile="sable-2.0.5", ground_y=168)` from `agent/sim/rigid.py`. The profile sets **40 Hz**, gravity `-11`, damping `0.09` and source-derived basic material coefficient `0.7625`. Override frequency, gravity or body damping explicitly to test a custom server config.

```sh
python3 -m unittest agent.tests.test_sable205 -v
python3 -m unittest discover -s agent/tests -p 'test_*.py'
```

Test `test_no_contact_two_substeps` compares the integrated World with standalone formulas. A separate illustrative superflat model (230 dirt + bedrock + grass, surface Y=168) starts at `(0,300,0)` with `(0,0,5)` m/s and stops at approximately `(0,168.5,21.556)` after `5.65 s` **in the simplified contact model**. This is **not** a measured result from the bundled Rapier binary or Minecraft.

For actual contact-equivalent results, a native JNI/Rapier integration harness or a trace captured in-game with the same modpack is required. The already-bundled native engine cannot be called as a drop-in Python extension: it exposes JNI entry points tied to Sable's Java-side world, collider and physics pipeline. Likewise, copying only the motion formulas does not recreate its full physics solver. Preserve upstream license notices and do not redistribute the proprietary/native payload with this repository.
