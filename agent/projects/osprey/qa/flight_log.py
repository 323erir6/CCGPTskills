"""Validate read-only CC:Sable position/velocity telemetry collected in Minecraft.

No propulsion, control actuation, destination tracking, target coordinates, or
navigation logic. This verifies DATA QUALITY, not trajectory performance.

Usage:
  python -m agent.projects.osprey.qa.flight_log input.jsonl --out report.json
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

MAX_LINES = 100_000
MAX_BYTES_PER_LINE = 16_384
WORLD_LIMIT = 30_000_000


def finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def vector(item, keys, bound):
    if not isinstance(item, dict) or any(not finite(item.get(k)) for k in keys):
        raise ValueError("missing, nonnumeric, or nonfinite vector component")
    result = tuple(float(item[k]) for k in keys)
    if any(abs(v) > bound for v in result):
        raise ValueError("vector outside supported numeric bounds")
    return result


def invalid_constant(x):
    raise ValueError("nonfinite JSON constant " + x)


def validate(data: list[dict], *, min_samples=10, max_gap_s=1.0, velocity_limit=1_000_000.0):
    """Fail closed on missing measurements, gaps, tampering or invalid sensor data."""
    if not isinstance(min_samples, int) or not 2 <= min_samples <= MAX_LINES:
        raise ValueError("min_samples outside 2..100000")
    if not finite(max_gap_s) or max_gap_s <= 0:
        raise ValueError("invalid max_gap_s")
    if not finite(velocity_limit) or velocity_limit <= 0:
        raise ValueError("invalid velocity_limit")
    failures = []
    previous = None
    max_gap = 0.0
    max_speed = 0.0
    max_rotation_speed = 0.0
    start_pos = end_pos = None
    first_time = last_time = None
    vehicle = None
    good = 0
    for index, frame in enumerate(data):
        try:
            if not isinstance(frame, dict) or frame.get('schema_version') != 1 or frame.get('kind') != 'sable_pose':
                raise ValueError('invalid frame schema')
            if not isinstance(frame.get('vehicle'), str) or not 1 <= len(frame['vehicle']) <= 64:
                raise ValueError('invalid vehicle name')
            if vehicle is None:
                vehicle = frame['vehicle']
            elif frame['vehicle'] != vehicle:
                raise ValueError('mixed vehicle identities')
            if not isinstance(frame.get('seq'), int) or isinstance(frame['seq'], bool) or frame['seq'] != index:
                raise ValueError('missing, duplicate, or unordered sequence')
            t = frame.get('t_s')
            if not finite(t) or t < 0 or t > 1e7:
                raise ValueError('invalid elapsed time')
            t = float(t)
            if previous is not None:
                dt = t - previous
                if dt <= 0:
                    raise ValueError('non-monotonic time')
                max_gap = max(max_gap, dt)
                if dt > max_gap_s:
                    raise ValueError('sample gap exceeds limit')
            previous = t
            if first_time is None:
                first_time = t
            last_time = t
            if frame.get('status') != 'ok':
                raise ValueError('sensor error frame')
            pos = vector(frame.get('pos'), ('x','y','z'), WORLD_LIMIT)
            vel = vector(frame.get('velocity'), ('x','y','z'), velocity_limit)
            ang = vector(frame.get('angular_velocity'), ('x','y','z'), velocity_limit)
            q = vector(frame.get('orientation'), ('x','y','z','w'), 2.)
            norm2 = sum(a*a for a in q)
            if not 0.9025 < norm2 < 1.1025:
                raise ValueError('invalid quaternion magnitude')
            speed = math.sqrt(sum(x*x for x in vel))
            spin = math.sqrt(sum(x*x for x in ang))
            max_speed = max(speed, max_speed)
            max_rotation_speed = max(spin, max_rotation_speed)
            if start_pos is None:
                start_pos = pos
            end_pos = pos
            good += 1
        except (ValueError, TypeError) as exc:
            failures.append({'frame': index, 'reason': str(exc)})
    if len(data) < min_samples:
        failures.append({'reason':'too few samples', 'got':len(data), 'need':min_samples})
    if not data:
        failures.append({'reason':'empty telemetry'})
    displacement = None if start_pos is None or end_pos is None else math.dist(start_pos, end_pos)
    return {
        'schema_version':1,
        'scope':'read-only CC:Sable telemetry integrity; NOT vehicle navigation qualification',
        'status':'passed' if not failures else 'failed',
        'samples':len(data),'valid_samples':good,
        'vehicle':vehicle,'elapsed_s':None if first_time is None else last_time-first_time,
        'max_sample_gap_s':max_gap,'max_speed_m_s':max_speed,
        'max_angular_speed_rad_s':max_rotation_speed,
        'net_displacement_m':displacement,
        'faults':failures[:100], 'fault_count':len(failures),
        'actual_game_equivalence':'unverified',
        'destination_accuracy':'not assessed',
        'release_qualified':False,
    }


def read_frames(path: Path):
    result=[]
    with path.open('r',encoding='utf-8') as file:
        for line_no, line in enumerate(file, 1):
            if line_no > MAX_LINES:
                raise ValueError('too many log frames')
            if len(line.encode('utf-8')) > MAX_BYTES_PER_LINE:
                raise ValueError(f'frame {line_no} too large')
            if not line.strip():
                raise ValueError(f'blank line {line_no}')
            try:
                result.append(json.loads(line, parse_constant=invalid_constant))
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(f'corrupt JSON at line {line_no}: {exc}') from exc
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log',type=Path)
    parser.add_argument('--out',type=Path)
    parser.add_argument('--min-samples',type=int,default=10)
    parser.add_argument('--max-gap',type=float,default=1.0)
    args=parser.parse_args(argv)
    try:
        result=validate(read_frames(args.log),min_samples=args.min_samples,max_gap_s=args.max_gap)
    except (ValueError,OSError) as exc:
        result={
            'schema_version':1,'status':'failed',
            'scope':'read-only CC:Sable telemetry integrity',
            'faults':[{'reason':str(exc)}], 'release_qualified':False,
        }
    payload=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(payload,'utf-8')
    print(payload,end='')
    return 0 if result['status']=='passed' else 1

if __name__=='__main__':
    raise SystemExit(main())
