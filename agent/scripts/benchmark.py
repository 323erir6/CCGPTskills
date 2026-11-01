#!/usr/bin/env python3
"""Run deterministic check commands and write a machine-readable report."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES = ROOT / "agent/benchmarks/cases.json"


def discover_runtimes() -> dict[str, str | None]:
    configured_lua = os.environ.get("LUA_BIN")
    lua = configured_lua if configured_lua and shutil.which(configured_lua) else None
    if lua is None:
        lua = next((path for name in ("lua5.3", "lua")
                    if (path := shutil.which(name))), None)
    return {"python": sys.executable, "lua": lua}


def _resolve(command: list[str], runtimes: dict[str, str | None]) -> tuple[list[str], str | None]:
    aliases = {"{python}": "python", "python3": "python",
               "{lua}": "lua", "lua5.3": "lua"}
    resolved = list(command)
    runtime_name = aliases.get(resolved[0])
    if runtime_name:
        executable = runtimes.get(runtime_name)
        if not executable:
            return resolved, runtime_name
        resolved[0] = executable
    return resolved, None


def run(cases: list, root: Path, timeout: float, *, runtimes=None,
        skip_unavailable: bool = False) -> dict:
    runtimes = discover_runtimes() if runtimes is None else runtimes
    results = []
    for case in cases:
        command = case["command"]
        if not isinstance(command, list) or not command or not all(isinstance(x, str) for x in command):
            raise ValueError(f"Invalid command for case: {case.get('id')}")
        command, missing_runtime = _resolve(command, runtimes)
        started = time.monotonic()
        if missing_runtime:
            entry = {"id": case["id"], "passed": False,
                     "skipped": skip_unavailable,
                     "error": f"missing runtime: {missing_runtime}",
                     "elapsed_seconds": 0.0}
            results.append(entry)
            continue
        try:
            result = subprocess.run(command, cwd=root, capture_output=True, text=True,
                                    timeout=timeout, check=False)
            passed = result.returncode == 0 and case.get("expected", "") in result.stdout
            entry = {"id": case["id"], "passed": passed, "skipped": False,
                     "exit_code": result.returncode,
                     "stdout": result.stdout[-4000:], "stderr": result.stderr[-4000:]}
        except subprocess.TimeoutExpired:
            entry = {"id": case["id"], "passed": False, "skipped": False,
                     "error": "timeout"}
        except OSError as exc:
            entry = {"id": case["id"], "passed": False, "skipped": False,
                     "error": str(exc)}
        entry["elapsed_seconds"] = round(time.monotonic() - started, 3)
        results.append(entry)
    return {"schema_version": 2, "total": len(results),
            "passed": sum(item["passed"] for item in results),
            "skipped": sum(item.get("skipped", False) for item in results),
            "cases": results}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--output", type=Path, default=ROOT / "agent-results/benchmark.json")
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--skip-unavailable", action="store_true",
                        help="report unavailable runtimes as skipped instead of failed")
    args = parser.parse_args(argv)
    cases = json.loads(args.cases.read_text(encoding="utf-8"))["cases"]
    output = run(cases, ROOT, args.timeout, skip_unavailable=args.skip_unavailable)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for item in output["cases"]:
        label = "PASS" if item["passed"] else "SKIP" if item.get("skipped") else "FAIL"
        print(label + " " + item["id"])
    print(f"Score: {output['passed']} passed, {output['skipped']} skipped, "
          f"{output['total']} total")
    return 0 if output["passed"] + output["skipped"] == output["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
