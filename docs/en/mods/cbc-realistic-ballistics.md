# CBC Realistic Ballistics 1.9.22 — integration and API boundaries

**Source:** [CBC-Realistic-Ballistics](https://github.com/323erir6/CBC-Realistic-Ballistics), commit `a09920888421b15de1fe7d92cc01e0731ba6c725`; current `gradle.properties: mod_version=1.9.22`, Minecraft 1.21.1, Create 6.0.10, CBC 5.11.7. The installed JAR metadata identifies mod ID `cbc_realistic_ballistics`.

## API status

**The current JAR bytecode scan found no direct CC:Tweaked API references and no new Lua peripheral methods.** The add-on modifies physical projectile flight, collision handling, persistence and optimization internally through Java/NeoForge. It must not be confused with **CBC Going Ballistic** (a different public mod, *not* part of the audited mod archive).

CC-facing information comes from other mods, notably:
- `CBC Programmable Fuzes` inspection methods: `getLoadedProjectileInfo()`, `getLoadedPropellantInfo()`, `getCannonInfo()`.
- NeoPeripheral/CBC or CBC-specific mount peripherals: yaw, pitch, assembly, firing and inspection methods.
- Radar/physics peripherals: world coordinate and velocity snapshots.

## Effective behavior described in source

- Projectile motion follows a custom SI-derived model using mass, drag, air density and gravity.
- The model supports named ammunition profiles and nominal calibre overrides.
- Projectile flight/transit can be retained across unloaded terrain and server restarts in later releases.
- Swept collision checks reduce tunneling by sampling the actual projectile trajectory along bounded segments; unknown terrain near ground is not globally treated as empty air.
- The add-on preserves CBC explosion/penetration behavior in its own integration layer.
- Modern releases contain optimizations and life-cycle handling for projectiles, including those from other CBC add-ons.

**Do not substitute physical diameter from `getLoadedProjectileInfo()` for the model's nominal calibre.** The former is generally the entity hitbox. Also do not assume a linear velocity-to-range formula: drag, projectile mass, atmosphere, elevation, and add-on profiles matter.

## Offline documentation expectations

A future independently implemented solver must document:
1. Exact projectile registry ID / ballistic profile mapping.
2. Configuration keys, numeric defaults, units and permitted ranges.
3. Gravity and atmosphere/drag equations from the installed Java source.
4. Integration step and tick/substep relationship.
5. Projectile cross-section, effective mass, wind seed and any range correction.
6. Special overrides for CBC AT, Military Supplement, and other shell types.
7. Comparison tests for identical in-game and offline initial conditions.

**No ballistic calculator is included here**, because reliable calculations require copying all relevant constants and rules from the exact installed release. Do not infer them from another CBC mod.

## Compatibility

- `cbc-programmable-fuzes-1.4.1.jar` interacts with projectiles through other exposed APIs; source work is version-specific.
- `cbc_aero_velocity_fix-1.0.7.jar` is a separate server-side physical patch with no direct CC interface.
- `Sable High Altitude Transit` changes physics/chunk residency, not the Lua method list.
- High-frequency CC updates depend on `Sable CC Tick Sync`, not on this ballistic mod.

## Verification

Use a dedicated offline regression suite plus real in-game trajectory tests in the current modpack. The `gradlew build` tests described in the project are not proof that CC device methods exist.

**Source:** [README](https://github.com/323erir6/CBC-Realistic-Ballistics/blob/main/README.md), [RealisticFlightModel.java](https://github.com/323erir6/CBC-Realistic-Ballistics/blob/main/src/main/java/dev/cbcrealisticballistics/RealisticFlightModel.java), [BallisticsConfig.java](https://github.com/323erir6/CBC-Realistic-Ballistics/blob/main/src/main/java/dev/cbcrealisticballistics/BallisticsConfig.java).