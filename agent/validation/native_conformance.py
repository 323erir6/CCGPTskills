"""Repeatable, non-weapon Sable 2.0.5 native physics conformance checks.

Tests cube-on-superflat contact, numerical drift, resting velocity, and run-to-run
reproducibility with the original user-provided Sable JNI native library.

This suite intentionally does not test weapons, interception, guidance or any
project-specific target accuracy. Passing it cannot certify Minecraft parity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from math import isfinite
from pathlib import Path

from agent.sim.native_rapier import NativeScene, SABLE_NAME

SURFACE_Y = 168.0
EXPECTED_CENTER_Y = SURFACE_Y + 0.5
DEFAULT_DT = 1.0 / 40.0
DEFAULT_STEPS = 160
VERTICAL_TOLERANCE = 0.035
HORIZONTAL_TOLERANCE = 0.25
REST_SPEED_TOLERANCE = 0.02
REPEAT_TOLERANCE = 0.01


@dataclass(frozen=True)
class DropCase:
    id: int
    start_x: float
    start_y: float
    start_z: float
    mass: float

    @property
    def expected_ground_pos(self):
        return (self.start_x, EXPECTED_CENTER_Y, self.start_z)


def make_cases(count=12):
    if not isinstance(count, int) or not 1 <= count <= 12:
        raise ValueError('case count must be 1..12 (non-overlapping test sites)')
    cases = []
    for i in range(count):
        col, row = i % 4, i // 4
        cases.append(DropCase(
            id=i + 1,
            start_x=float(-12 + 8 * col) + 0.5,
            start_y=float(172 + i % 6 * 2),
            start_z=float(-10 + row * 10) + 0.5,
            mass=(1.0, 2.0, 4.5, 8.0)[i % 4],
        ))
    return cases


def execute_native(jar: Path, cases: list[DropCase], steps=DEFAULT_STEPS):
    if steps < 1 or steps > 1000:
        raise ValueError('steps out of bounds')
    with NativeScene(jar) as scene:
        scene.init(gravity=(0, -11, 0), drag=0.09)
        solid = scene.material('minecraft:stone', mu=1.0)
        # Full local terrain window. Source voxel chunks are created by JNI.
        scene.ground(SURFACE_Y, 0, 0, radius=3, material=solid)
        for c in cases:
            # A full homogeneous cube: I_x = I_y = I_z = m / 6.
            inertia = (c.mass / 6,) * 3
            scene.ship(c.id, (c.start_x, c.start_y, c.start_z),
                       (0, 0, 0, 1), c.mass, (0.5, 0.5, 0.5), inertia,
                       (0, 0, 0, 0, 0, 0), [(0, 0, 0, solid)])
        for _ in range(steps):
            scene.step(DEFAULT_DT)
        return {c.id: scene.state(c.id) for c in cases}


def evaluate(cases, runs, *, vertical_tol=VERTICAL_TOLERANCE,
             horizontal_tol=HORIZONTAL_TOLERANCE, rest_tol=REST_SPEED_TOLERANCE,
             repeat_tol=REPEAT_TOLERANCE):
    """Mechanical contact-only acceptance; no Minecraft or guidance claims."""
    if not runs:
        raise ValueError('native runs are required: never invent a pass')
    expected = {c.id for c in cases}
    rows = []
    accepted = True
    for run_index, states in enumerate(runs):
        if set(states) != expected:
            raise ValueError('native run missing or extra test objects')
        for c in cases:
            state = states[c.id]
            pos, vel = state['position'], state['velocity']
            if len(pos) != 3 or len(vel) != 3 or not all(isfinite(v) for v in (*pos, *vel)):
                raise ValueError('non-finite or malformed native state')
            dx = pos[0] - c.start_x
            dz = pos[2] - c.start_z
            dr = (dx * dx + dz * dz) ** 0.5
            dy = pos[1] - EXPECTED_CENTER_Y
            v = sum(x * x for x in vel) ** 0.5
            baseline = runs[0][c.id]['position']
            repeat_delta = sum((pos[k] - baseline[k]) ** 2 for k in range(3)) ** 0.5
            ok = (abs(dy) <= vertical_tol and dr <= horizontal_tol
                  and v <= rest_tol and repeat_delta <= repeat_tol)
            accepted = accepted and ok
            rows.append({
                'run': run_index + 1, 'case': c.id, 'mass': c.mass,
                'initial_position': [c.start_x, c.start_y, c.start_z],
                'final_position': list(pos), 'vertical_error_m': dy,
                'horizontal_drift_m': dr, 'final_speed_m_s': v,
                'repeat_difference_m': repeat_delta, 'passed': ok,
            })
    return {
        'schema_version': 1,
        'test_scope': 'generic one-block free fall and ground contact ONLY',
        'physics_engine': 'original Sable Rapier 2.0.5 JNI',
        'native_contact_status': 'passed' if accepted else 'failed',
        'game_equivalence': 'unverified',
        'guidance_accuracy': 'not tested (out of scope)',
        'thresholds': {
            'vertical_contact_m': vertical_tol,
            'horizontal_drift_m': horizontal_tol,
            'rest_speed_m_s': rest_tol,
            'repeatability_m': repeat_tol,
        },
        'case_count': len(cases), 'run_count': len(runs),
        'measurements': rows,
        'max_vertical_error_m': max(abs(row['vertical_error_m']) for row in rows),
        'max_horizontal_drift_m': max(row['horizontal_drift_m'] for row in rows),
        'max_repeat_difference_m': max(row['repeat_difference_m'] for row in rows),
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--jar', type=Path, required=True,
                   help=f'Original, trusted {SABLE_NAME} (no mod binary is shipped)')
    p.add_argument('--runs', type=int, default=3)
    p.add_argument('--cases', type=int, default=12)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(argv)
    if not 1 <= a.runs <= 5:
        p.error('--runs must be between 1 and 5')
    if not a.jar.is_file() or a.jar.name != SABLE_NAME:
        p.error('native JAR missing or wrong version')
    cases = make_cases(a.cases)
    result = evaluate(cases, [execute_native(a.jar, cases) for _ in range(a.runs)])
    result['sable_jar_sha256'] = hashlib.sha256(a.jar.read_bytes()).hexdigest()
    result['simulation_seconds_per_case'] = DEFAULT_STEPS * DEFAULT_DT
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f"Sable JNI generic contact: {result['native_contact_status']} "
          f"({len(cases)} cases × {a.runs} runs; "
          f"vertical error <= {result['max_vertical_error_m']:.5f} m; "
          f"horizontal drift <= {result['max_horizontal_drift_m']:.5f} m; "
          f"reproducibility delta <= {result['max_repeat_difference_m']:.7f} m)")
    print('Minecraft in-game equivalence: UNVERIFIED. Guidance: NOT TESTED.')
    return 0 if result['native_contact_status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
