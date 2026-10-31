#!/usr/bin/env python3
"""Run deterministic check commands and write a machine-readable report."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES = ROOT / "agent/benchmarks/cases.json"


def run(cases: list, root: Path, timeout: float) -> dict:
    results = []
    for case in cases:
        command = case["command"]
        if not isinstance(command, list) or not command or not all(isinstance(x, str) for x in command):
            raise ValueError(f"Invalid command for case: {case.get('id')}")
        started = time.monotonic()
        try:
            result = subprocess.run(command, cwd=root, capture_output=True, text=True,
                                    timeout=timeout, check=False)
            passed = result.returncode == 0 and case.get("expected", "") in result.stdout
            entry = {"id": case["id"], "passed": passed, "exit_code": result.returncode,
                     "stdout": result.stdout[-4000:], "stderr": result.stderr[-4000:]}
        except subprocess.TimeoutExpired:
            entry = {"id": case["id"], "passed": False, "error": "timeout"}
        except OSError as exc:
            entry = {"id": case["id"], "passed": False, "error": str(exc)}
        entry["elapsed_seconds"] = round(time.monotonic() - started, 3)
        results.append(entry)
    return {"schema_version": 1, "total": len(results),
            "passed": sum(item["passed"] for item in results), "cases": results}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--output", type=Path, default=ROOT / "agent-results/benchmark.json")
    parser.add_argument("--timeout", type=float, default=30)
    args = parser.parse_args(argv)
    cases = json.loads(args.cases.read_text(encoding="utf-8"))["cases"]
    output = run(cases, ROOT, args.timeout)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for item in output["cases"]:
        print(("PASS" if item["passed"] else "FAIL") + " " + item["id"])
    print(f"Score: {output['passed']}/{output['total']}")
    return 0 if output["passed"] == output["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
