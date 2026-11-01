#!/usr/bin/env python3
"""Classify CI failures from an existing text log; no LLM or API access."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

RULES = [
    ("lua_syntax", r"(?:luac|lua): .*?(?:syntax error|near '\\w+'|unexpected symbol)"),
    ("java_compile", r"(?:error: cannot find symbol|Compilation failed|> Task .*compileJava FAILED)"),
    ("python_test", r"(?:FAILED \(failures=|AssertionError|pytest .*failed)"),
    ("missing_api", r"(?:attempt to call a nil value|No such method|Cannot resolve method)"),
    ("missing_dependency", r"(?:ModuleNotFoundError|Could not resolve|package .* not found)"),
    ("timeout", r"(?:timed out|TimeoutExpired|time limit exceeded)"),
    ("permission", r"(?:Permission denied|Resource not accessible by integration)"),
]


def diagnose(text: str) -> dict:
    findings = []
    for kind, pattern in RULES:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        if matches:
            findings.append({"category": kind, "matches": len(matches)})
    return {"schema_version": 1, "findings": findings,
            "status": "failure_signatures_found" if findings else "no_known_failure_signature"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = diagnose(args.log.read_text(encoding="utf-8", errors="replace"))
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
