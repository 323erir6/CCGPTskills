#!/usr/bin/env python3
"""Compare recorded Minecraft or reference traces with simulator snapshots."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path


def compare(expected, actual, absolute=1e-6, relative=1e-6, path="$"):
    issues = []
    if isinstance(expected, bool) or isinstance(actual, bool):
        if expected is not actual:
            issues.append(f"{path}: expected {expected!r}, got {actual!r}")
    elif isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        if not math.isfinite(expected) or not math.isfinite(actual):
            issues.append(f"{path}: non-finite comparison is forbidden")
        elif not math.isclose(expected, actual, rel_tol=relative, abs_tol=absolute):
            issues.append(f"{path}: expected {expected:.12g}, got {actual:.12g}, "
                          f"absolute error {abs(expected-actual):.12g}")
    elif type(expected) is not type(actual):
        issues.append(f"{path}: type mismatch "
                      f"{type(expected).__name__}/{type(actual).__name__}")
    elif isinstance(expected, dict):
        for key in sorted(set(expected) | set(actual)):
            if key not in expected:
                issues.append(f"{path}.{key}: unexpected field")
            elif key not in actual:
                issues.append(f"{path}.{key}: missing field")
            else:
                issues.extend(compare(expected[key], actual[key],
                                      absolute, relative, f"{path}.{key}"))
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            issues.append(f"{path}: length mismatch {len(expected)}/{len(actual)}")
        for i, (e, a) in enumerate(zip(expected, actual)):
            issues.extend(compare(e, a, absolute, relative, f"{path}[{i}]"))
    elif expected != actual:
        issues.append(f"{path}: expected {expected!r}, got {actual!r}")
    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("observed", type=Path)
    parser.add_argument("--abs", type=float, default=1e-6)
    parser.add_argument("--rel", type=float, default=1e-6)
    args = parser.parse_args()
    if not all(math.isfinite(x) and x >= 0 for x in (args.abs, args.rel)):
        parser.error("tolerances must be finite and nonnegative")
    expected = json.loads(args.reference.read_text("utf-8"))
    observed = json.loads(args.observed.read_text("utf-8"))
    issues = compare(expected, observed, args.abs, args.rel)
    print(json.dumps({"matched": not issues, "differences": issues},
                     ensure_ascii=False, indent=2))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
