#!/usr/bin/env python3
"""Validate structured CC:Tweaked API manifests using only Python stdlib."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

METHOD_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
ALLOWED = {"source-confirmed", "runtime-confirmed", "documentation-confirmed", "unverified"}
ROOT = Path(__file__).resolve().parents[2]


def validate(payload: dict) -> list[str]:
    failures: list[str] = []
    if payload.get("schema_version") != 1:
        failures.append("schema_version must be 1")
    for key in ("id", "mod", "version", "minecraft", "source_url", "source_commit"):
        if not isinstance(payload.get(key), str) or not payload[key].strip():
            failures.append(f"{key} must be nonempty text")
    if not isinstance(payload.get("interfaces"), list) or not payload["interfaces"]:
        return failures + ["interfaces must be a nonempty list"]
    names = set()
    for interface in payload["interfaces"]:
        name = interface.get("name")
        if not isinstance(name, str) or not name:
            failures.append("interface has no name")
        elif name in names:
            failures.append(f"duplicate interface: {name}")
        names.add(name)
        if interface.get("kind") not in ("global", "peripheral"):
            failures.append(f"{name}: invalid kind")
        methods = interface.get("methods")
        if not isinstance(methods, list) or not methods:
            failures.append(f"{name}: no methods")
            continue
        seen = set()
        for method in methods:
            m = method.get("name")
            if not isinstance(m, str) or not METHOD_RE.fullmatch(m):
                failures.append(f"{name}: invalid method name: {m}")
                continue
            if m in seen:
                failures.append(f"{name}: duplicate method {m}")
            seen.add(m)
            if method.get("verification") not in ALLOWED:
                failures.append(f"{name}.{m}: invalid verification")
            for prop in ("arguments", "returns"):
                if not isinstance(method.get(prop), list):
                    failures.append(f"{name}.{m}: {prop} must be a list")
                elif any(not isinstance(a, str) or not a for a in method[prop]):
                    failures.append(f"{name}.{m}: {prop} contains invalid type")
            if not isinstance(method.get("source_path"), str) or not method["source_path"]:
                failures.append(f"{name}.{m}: source_path required")
    return failures


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=ROOT / "agent/api")
    args = parser.parse_args(argv)
    paths = sorted(args.directory.glob("*.json"))
    if not paths:
        print("ERROR: no API manifests found", file=sys.stderr)
        return 1
    failures = []
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"{path.name}: {exc}")
            continue
        failures.extend(f"{path.name}: {msg}" for msg in validate(data))
    for error in failures:
        print("ERROR:", error, file=sys.stderr)
    print(f"API manifests: {len(paths)} checked, {len(failures)} errors")
    return bool(failures)


if __name__ == "__main__":
    sys.exit(main())
