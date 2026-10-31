"""Verified scalar formulas and defaults for Minecraft 1.21.1 Sable NeoForge 2.0.5.

Reference: https://github.com/ryanhcode/sable/tree/mc1.21.1-2.0.5-neoforge
Bundled Rapier fork revision: 38e92f117590862481a53df6fc69a5d893e29186.

Only these scalar formulas/constants are sourced directly. This module does NOT
port the Rapier contact solver, VoxelCollider or sleeping/island algorithms.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite

SABLE_TAG = "mc1.21.1-2.0.5-neoforge"
RAPIER_REVISION = "38e92f117590862481a53df6fc69a5d893e29186"
EXTRACTED_JAR_SHA256 = "c8710f85bc780bbf523e6726ceaaf76dd0b8c61479db497b382c6bb34317e7ab"


@dataclass(frozen=True)
class Sable205:
    gravity: tuple[float, float, float] = (0.0, -11.0, 0.0)
    universal_drag: float = 0.09
    game_tps: int = 20
    physics_substeps: int = 2
    moving_construction_friction: float = 0.525
    static_world_friction: float = 1.0  # Rapier ColliderMaterial default
    block_friction_multiplier: float = 1.0  # Sable block-property default
    block_restitution: float = 0.0
    solver_iterations: int = 18  # Java PhysicsConfigData nominal default, runtime dependent
    pgs_iterations: int = 2
    stabilization_iterations: int = 2
    contact_natural_frequency: float = 30.0  # Native 2.0.5 scene
    contact_damping_ratio: float = 5.0
    max_ccd_substeps: int = 3

    @property
    def physics_hz(self) -> int:
        return self.game_tps * self.physics_substeps

    @property
    def contact_friction(self) -> float:
        """Rapier fork's default AVERAGE rule, then Sable block multiplier."""
        return combine_friction(self.moving_construction_friction,
                                self.static_world_friction,
                                self.block_friction_multiplier)


def combine_friction(a: float, b: float, multiplier_a: float = 1.0,
                     multiplier_b: float = 1.0) -> float:
    """Fork's default Average combine rule, then Sable per-block multipliers."""
    for value in (a, b, multiplier_a, multiplier_b):
        if not isfinite(value) or value < 0:
            raise ValueError("finite nonnegative material coefficients required")
    return (a + b) * 0.5 * multiplier_a * multiplier_b


def damp(velocity: float, damping: float, dt: float) -> float:
    """Exact Rapier 38e92f1 velocity component damping: v / (1 + dt*k)."""
    if not all(isfinite(x) for x in (velocity, damping, dt)) or damping < 0 or dt < 0:
        raise ValueError("invalid damping parameters")
    return velocity / (1.0 + dt * damping)


def coulomb_impulse_limit(normal_impulse: float, mu: float) -> float:
    """Magnitude upper bound |J_t| <= mu * J_n (not a contact solver)."""
    if not all(isfinite(x) and x >= 0 for x in (normal_impulse, mu)):
        raise ValueError("normal impulse and mu must be nonnegative")
    return normal_impulse * mu


def free_step(position: tuple[float, float, float],
              velocity: tuple[float, float, float], dt: float,
              gravity=(0.0, -11.0, 0.0), drag=0.09):
    """No-contact symplectic Euler plus END-of-substep damping.

    Solver integrates position using updated velocity; writeback applies
    1/(1+k*dt) to velocity after position. Exact for this isolated model,
    not a reproduction of Rapier constrained/CCD stepping.
    """
    if not isfinite(dt) or dt < 0:
        raise ValueError("invalid dt")
    pre = tuple(v + g * dt for v, g in zip(velocity, gravity, strict=True))
    out_pos = tuple(p + v * dt for p, v in zip(position, pre, strict=True))
    return out_pos, tuple(damp(v, drag, dt) for v in pre)
