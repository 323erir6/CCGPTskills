#!/usr/bin/env python3
"""Lightweight high-signal static checks. Not a proof of code safety."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RULES = [
    ("nonportable_atan2", re.compile(r"\bmath\.atan2\s*\("),
     "Prefer version-verified math.atan(y,x) for CC:Tweaked"),
    ("lua_load_network", re.compile(r"\bloadstring?\s*\(\s*(?:message|packet|received|payload)\b"),
     "Review execution of network-supplied Lua"),
]


def review_file(path: Path):
    issues = []
    for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        code = line.split("--", 1)[0]  # avoid comments
        for code_name, regex, hint in RULES:
            if regex.search(code):
                issues.append((path, number, code_name, hint))
    return issues


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args(argv)
    paths = args.paths or [ROOT / "agent/mocks"]
    candidates = sorted({f for p in paths for f in (p.rglob("*.lua") if p.is_dir() else [p])
                         if f.is_file() and f.suffix == ".lua"})
    issues = [issue for candidate in candidates for issue in review_file(candidate)]
    for path, line, code, msg in issues:
        print(f"{path}:{line}: {code}: {msg}")
    print(f"Review: {len(candidates)} Lua files, {len(issues)} high-signal findings")
    return bool(issues)


if __name__ == "__main__":
    sys.exit(main())
