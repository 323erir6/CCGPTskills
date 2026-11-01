"""Fail-closed comparison of passive Sable contact tests with recorded Minecraft runs.

This is a generic physics parity auditor, NOT a weapons targeting/guidance validator.
It never invents an in-game run. A machine-produced comparison only verifies
consistency of *reported* observations, not the authenticity of the capture.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from math import hypot, isfinite, sqrt
from pathlib import Path

SCENARIO = "generic one-block free fall and ground contact ONLY"
LIVE_SCHEMA = 1
MIN_REPEATS = 3
MIN_CASES = 8


def _number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{label}: finite number required")
    return float(value)


def _vec(value, label):
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError(f"{label}: three components required")
    return tuple(_number(x, f"{label}[{i}]") for i, x in enumerate(value))


def _index(rows, *, source):
    if not isinstance(rows, list):
        raise ValueError(f"{source}: observations must be a list")
    output = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(f"{source}: invalid observation")
        run, case = row.get('run'), row.get('case')
        if (type(run) is not int or type(case) is not int or run < 1 or case < 1):
            raise ValueError(f"{source}: positive integer run and case required")
        key = (run, case)
        if key in output:
            raise ValueError(f"{source}: duplicate observation {key}")
        _vec(row.get('final_position'), f"{source} {key} position")
        # Verify actual three-axis velocity; speed magnitudes cannot substitute.
        _vec(row.get('final_velocity'), f"{source} {key} velocity")
        _vec(row.get('initial_position'), f"{source} {key} initial position")
        _number(row.get('mass'), f"{source} {key} mass")
        output[key] = row
    return output


def audit(native: dict, live: dict | None, *, max_position_error=0.25,
          max_speed_error=0.1, min_cases=MIN_CASES, min_repeats=MIN_REPEATS) -> dict:
    """Compare *observed* resting states; absence of game data fails closed.

    Native source: JSON from native_conformance (with velocities supplied by
    native runner). Live source: independent CC:Sable measurements in matching
    local coordinates, captured after the same 4-second passive drop scenario.
    """
    if not isinstance(native, dict) or native.get('test_scope') != SCENARIO:
        raise ValueError('wrong native physics scenario')
    if native.get('physics_engine') != 'original Sable Rapier 2.0.5 JNI':
        raise ValueError('native engine provenance missing')
    if native.get('native_contact_status') != 'passed':
        raise ValueError('native contact tests have not passed')
    for name, value in (("max_position_error", max_position_error),
                        ("max_speed_error", max_speed_error)):
        if _number(value, name) <= 0:
            raise ValueError(f'{name} must be positive')
    if type(min_cases) is not int or min_cases < 1 or type(min_repeats) is not int or min_repeats < 1:
        raise ValueError('invalid minimum coverage')
    report = {
        'schema_version': 1,
        'scope': 'passive block drop and ground-contact parity only',
        'status': 'not_qualified',
        'weapons_accuracy': 'not tested; this report cannot be used as a targeting claim',
        'live_game_equivalence': 'unverified',
        'criteria': {'minimum_distinct_cases': min_cases, 'minimum_repeats_per_case': min_repeats,
                     'position_delta_m': max_position_error, 'velocity_delta_m_s': max_speed_error},
        'observations': [], 'issues': [],
    }
    if live is None:
        report['issues'].append('No independently recorded Minecraft observations supplied')
        return report
    if not isinstance(live, dict) or live.get('schema_version') != LIVE_SCHEMA:
        raise ValueError('invalid live observation schema')
    if live.get('source') != 'minecraft_live' or live.get('capture_method') != 'cc_sable_passive_contact':
        raise ValueError('live observations must identify their source and capture method')
    if live.get('test_scope') != SCENARIO:
        raise ValueError('live and native tests have different scenarios')
    if live.get('time_basis') != 'verified_server_ticks':
        report['issues'].append('Minecraft timebase is not verified server ticks')
    if live.get('world_surface_y') != 168 or live.get('gravity_y') != -11:
        report['issues'].append('Minecraft test world gravity/ground configuration mismatch')
    if not live.get('modpack_fingerprint') or not live.get('world_config_fingerprint'):
        report['issues'].append('Missing modpack or physics/world configuration fingerprints')
    expected_sha = native.get('sable_jar_sha256')
    if not expected_sha or live.get('sable_jar_sha256') != expected_sha:
        report['issues'].append('Sable JAR fingerprint is missing or differs')
    nr = native.get('measurements')
    # Older native_conformance report includes final speed only. We reject it
    # explicitly instead of fabricating an axis-resolved velocity.
    if isinstance(nr, list) and any('final_velocity' not in row for row in nr):
        report['issues'].append('Native report lacks axis-resolved velocity; rerun an updated probe')
        return report
    nidx = _index(nr, source='native')
    lidx = _index(live.get('measurements'), source='live')
    if set(nidx) != set(lidx):
        report['issues'].append('Mismatched case/run coverage between native and live captures')
        return report
    counts = Counter(key[1] for key in nidx)
    if len(counts) < min_cases or any(n < min_repeats for n in counts.values()):
        report['issues'].append('Insufficient distinct cases or independent repeats')
    if len(set(key[0] for key in nidx)) < min_repeats:
        report['issues'].append('Insufficient independent run identifiers')
    for key in sorted(nidx):
        n, g = nidx[key], lidx[key]
        ni = _vec(n['initial_position'], 'native initial')
        gi = _vec(g['initial_position'], 'live initial')
        mass_diff = abs(_number(n['mass'], 'native mass') - _number(g['mass'], 'live mass'))
        if sqrt(sum((a-b)**2 for a,b in zip(ni, gi))) > 1e-6 or mass_diff > 1e-6:
            report['issues'].append(f'Initial condition mismatch: run {key[0]} case {key[1]}')
            continue
        np = _vec(n['final_position'], 'native position')
        gp = _vec(g['final_position'], 'live position')
        nv = _vec(n['final_velocity'], 'native velocity')
        gv = _vec(g['final_velocity'], 'live velocity')
        pos_d = sqrt(sum((a-b)**2 for a,b in zip(np, gp)))
        vel_d = sqrt(sum((a-b)**2 for a,b in zip(nv, gv)))
        row = {'run':key[0], 'case':key[1], 'position_difference_m':pos_d,
               'velocity_difference_m_s':vel_d,
               'passed':pos_d <= max_position_error and vel_d <= max_speed_error}
        report['observations'].append(row)
        if not row['passed']:
            report['issues'].append(f'Native/live physics discrepancy: run {key[0]} case {key[1]}')
    report['status'] = 'passive_parity_consistent' if not report['issues'] else 'not_qualified'
    report['live_game_equivalence'] = (
        'self-reported observations consistent for the tested passive contact scenarios only'
        if not report['issues'] else 'unverified')
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--live', type=Path, help='Independent CC:Sable game capture; never generated synthetically')
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args(argv)
    native = json.loads(a.native.read_text(encoding='utf-8'))
    live = json.loads(a.live.read_text(encoding='utf-8')) if a.live else None
    report = audit(native, live)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Passive contact parity:', report['status'])
    for issue in report['issues']:
        print(' -', issue)
    return 0 if report['status'] == 'passive_parity_consistent' else 1


if __name__ == '__main__':
    raise SystemExit(main())
