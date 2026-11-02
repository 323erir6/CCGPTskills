#!/usr/bin/env python3
"""Persist and enforce an evidence-backed autonomous Minecraft project cycle."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agent.sim.schematic_preflight import inspect as inspect_schematics


SCHEMA_VERSION = 1
VALID_EVIDENCE = {"static", "unit", "synthetic", "native", "live_server", "client"}
VALID_RESULT = {"verified", "failed", "partial", "not_tested"}
PROJECT_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{1,63}$")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def _fingerprint(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _resolve(base: Path, value: str, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty path")
    path = Path(value)
    return path.resolve() if path.is_absolute() else (base / path).resolve()


def _resolved_reference(base_file: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a path")
    path = Path(value)
    return path.resolve() if path.is_absolute() else (base_file.parent / path).resolve()


def _validate_live_evidence(evidence_path: Path, minimum_trials: int) -> list[dict]:
    value = _read_json(evidence_path)
    if not isinstance(value, dict) or value.get("status") != "passed":
        raise ValueError("verified live_server evidence must be a passed JSON report")
    trials = value.get("trials", 1)
    if type(trials) is not int or trials < minimum_trials:
        raise ValueError(f"live_server evidence requires at least {minimum_trials} trials")
    if "runtime_summary" in value:
        summary_path = _resolved_reference(evidence_path, value["runtime_summary"],
                                           "runtime_summary")
        if not summary_path.is_file():
            raise FileNotFoundError(f"runtime summary does not exist: {summary_path}")
        summary = _read_json(summary_path)
        summary_source = summary_path
    else:
        summary = value
        summary_source = evidence_path
    if (not isinstance(summary, dict) or summary.get("status") != "passed"
            or summary.get("mode") != "full" or type(summary.get("mod_jars")) is not int
            or summary["mod_jars"] < 1):
        raise ValueError("live_server evidence must reference a passed full-mode run-summary.json")
    report_path = _resolved_reference(summary_source, summary.get("report"), "headless report")
    if not report_path.is_file():
        raise FileNotFoundError(f"headless report does not exist: {report_path}")
    report = _read_json(report_path)
    if (not isinstance(report, dict) or report.get("status") != "passed"
            or report.get("engine") != "real NeoForge dedicated server with original Sable and mod JARs"):
        raise ValueError("headless report is not passed real-runtime evidence")
    loaded = {item.get("id"): str(item.get("version"))
              for item in report.get("loaded_mods", []) if isinstance(item, dict)}
    expected = {"sable": "2.0.5", "computercraft": "1.120.0",
                "sable_headless_telemetry": "1.0.0"}
    missing = {mod: version for mod, version in expected.items() if loaded.get(mod) != version}
    if missing:
        raise ValueError(f"headless report is missing exact runtime mods: {missing}")
    return [
        {"path": str(summary_source), "sha256": _sha256(summary_source)},
        {"path": str(report_path), "sha256": _sha256(report_path)},
    ]


def validate_manifest(path: Path) -> tuple[dict, dict]:
    path = Path(path).resolve()
    manifest = _read_json(path)
    if not isinstance(manifest, dict) or manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"project manifest schema_version must be {SCHEMA_VERSION}")
    project_id = manifest.get("project_id")
    if not isinstance(project_id, str) or not PROJECT_ID.fullmatch(project_id):
        raise ValueError("project_id must contain 2-64 lowercase letters, digits, dot, dash or underscore")
    base = path.parent
    technical_spec = _resolve(base, manifest.get("technical_spec"), "technical_spec")
    if not technical_spec.is_file():
        raise FileNotFoundError(f"technical specification does not exist: {technical_spec}")
    schematic_values = manifest.get("schematics")
    if not isinstance(schematic_values, list) or not schematic_values:
        raise ValueError("schematics must contain at least one human-authored schematic path")
    schematics = [_resolve(base, item, f"schematics[{index}]")
                  for index, item in enumerate(schematic_values)]
    for schematic in schematics:
        if not schematic.is_file():
            raise FileNotFoundError(f"schematic does not exist: {schematic}")
    criteria = manifest.get("acceptance_criteria")
    if not isinstance(criteria, list) or not criteria:
        raise ValueError("acceptance_criteria must be a nonempty array derived from the technical specification")
    seen = set()
    normalised_criteria = []
    for index, criterion in enumerate(criteria):
        if not isinstance(criterion, dict):
            raise ValueError(f"acceptance_criteria[{index}] must be an object")
        ident = criterion.get("id")
        description = criterion.get("description")
        measurement = criterion.get("measurement")
        pass_condition = criterion.get("pass_condition")
        minimum_trials = criterion.get("minimum_trials")
        required = criterion.get("required_evidence")
        if not isinstance(ident, str) or not PROJECT_ID.fullmatch(ident) or ident in seen:
            raise ValueError(f"acceptance_criteria[{index}].id must be unique and machine-safe")
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"acceptance_criteria[{index}].description is required")
        if not isinstance(measurement, str) or not measurement.strip():
            raise ValueError(f"acceptance_criteria[{index}].measurement is required")
        if not isinstance(pass_condition, str) or not pass_condition.strip():
            raise ValueError(f"acceptance_criteria[{index}].pass_condition is required")
        if type(minimum_trials) is not int or not 1 <= minimum_trials <= 1_000_000:
            raise ValueError(f"acceptance_criteria[{index}].minimum_trials must be 1-1000000")
        if not isinstance(required, list) or not required or any(item not in VALID_EVIDENCE for item in required):
            raise ValueError(f"acceptance_criteria[{index}].required_evidence is invalid")
        seen.add(ident)
        normalised_criteria.append({"id": ident, "description": description,
                                    "measurement": measurement,
                                    "pass_condition": pass_condition,
                                    "minimum_trials": minimum_trials,
                                    "required_evidence": sorted(set(required))})
    runtime = manifest.get("runtime")
    if not isinstance(runtime, dict) or runtime.get("profile") != "6.9.3":
        raise ValueError("runtime.profile must be 6.9.3")
    if runtime.get("minecraft") != "1.21.1" or runtime.get("neoforge") != "21.1.248":
        raise ValueError("runtime must pin Minecraft 1.21.1 and NeoForge 21.1.248")
    if runtime.get("mode") != "full":
        raise ValueError("runtime.mode must be full; minimal mode is diagnostic evidence only")
    contract_value = manifest.get("connection_contract")
    if not isinstance(contract_value, str) or not contract_value:
        raise ValueError("connection_contract is required for computer/peripheral topology")
    contract_path = _resolve(base, contract_value, "connection_contract")
    if not contract_path.is_file():
        raise FileNotFoundError(f"connection contract does not exist: {contract_path}")
    contract = _read_json(contract_path)
    preflight = inspect_schematics(schematics, contract)
    validation = {
        "manifest": str(path),
        "project_id": project_id,
        "technical_spec": str(technical_spec),
        "technical_spec_sha256": _sha256(technical_spec),
        "schematics": [{"path": str(item), "sha256": _sha256(item)} for item in schematics],
        "criteria": normalised_criteria,
        "connection_contract": str(contract_path),
        "connection_contract_sha256": _sha256(contract_path),
        "preflight": preflight,
    }
    validation["input_fingerprint"] = _fingerprint({
        "project_id": project_id,
        "technical_spec_sha256": validation["technical_spec_sha256"],
        "schematics": validation["schematics"],
        "connection_contract_sha256": validation["connection_contract_sha256"],
        "runtime": runtime,
        "criteria": normalised_criteria,
    })
    return manifest, validation


def state_path(manifest_path: Path) -> Path:
    return Path(manifest_path).resolve().parent / "autonomy-state.json"


def load_state(manifest_path: Path, project_id: str) -> dict:
    path = state_path(manifest_path)
    if not path.is_file():
        return {"schema_version": 1, "project_id": project_id, "evidence": [],
                "schematic_issues": [], "iterations": 0}
    state = _read_json(path)
    if not isinstance(state, dict) or state.get("schema_version") != 1:
        raise ValueError("autonomy-state.json has an unsupported schema")
    if state.get("project_id") != project_id:
        raise ValueError("autonomy-state.json belongs to another project")
    if not isinstance(state.get("evidence"), list) or not isinstance(state.get("schematic_issues"), list):
        raise ValueError("autonomy-state.json is malformed")
    return state


def project_status(manifest_path: Path) -> tuple[dict, dict, dict]:
    manifest, validation = validate_manifest(manifest_path)
    state = load_state(manifest_path, validation["project_id"])
    evidence_by_criterion = {criterion["id"]: [] for criterion in validation["criteria"]}
    stale_by_criterion = {criterion["id"]: [] for criterion in validation["criteria"]}
    for record in state["evidence"]:
        criterion = record.get("criterion")
        if criterion not in evidence_by_criterion:
            continue
        reason = None
        if record.get("input_fingerprint") != validation["input_fingerprint"]:
            reason = "project_inputs_changed"
        else:
            evidence = Path(str(record.get("evidence", "")))
            if not evidence.is_file():
                reason = "evidence_missing"
            elif record.get("sha256") != _sha256(evidence):
                reason = "evidence_changed"
            else:
                for dependency in record.get("dependencies", []):
                    dependency_path = Path(str(dependency.get("path", "")))
                    if not dependency_path.is_file():
                        reason = "evidence_dependency_missing"
                        break
                    if dependency.get("sha256") != _sha256(dependency_path):
                        reason = "evidence_dependency_changed"
                        break
        if reason:
            stale_by_criterion[criterion].append({**record, "stale_reason": reason})
        else:
            evidence_by_criterion[criterion].append(record)
    criteria_status = []
    for criterion in validation["criteria"]:
        records = evidence_by_criterion[criterion["id"]]
        latest_by_kind = {}
        for record in records:
            latest_by_kind[record.get("kind")] = record
        passed_kinds = {kind for kind, record in latest_by_kind.items()
                        if record.get("result") == "verified"}
        missing = sorted(set(criterion["required_evidence"]) - passed_kinds)
        criteria_status.append({**criterion, "status": "verified" if not missing else "pending",
                                "missing_evidence": missing,
                                "current_records": len(records),
                                "stale_records": len(stale_by_criterion[criterion["id"]]),
                                "latest_results": {
                                    kind: record.get("result")
                                    for kind, record in sorted(latest_by_kind.items(), key=lambda item: str(item[0]))
                                }})
    schematic_hashes = {item["path"]: item["sha256"] for item in validation["schematics"]}
    open_issues = []
    for issue in state["schematic_issues"]:
        if issue.get("status", "open") != "open":
            continue
        current_hash = schematic_hashes.get(issue.get("schematic"))
        open_issues.append({**issue, "schematic_changed": bool(
            current_hash and current_hash != issue.get("schematic_sha256")
        )})
    if validation["preflight"]["status"] != "passed":
        overall = "blocked_schematic"
    elif open_issues:
        overall = "blocked_schematic"
    elif all(item["status"] == "verified" for item in criteria_status):
        overall = "complete"
    else:
        overall = "continue"
    return manifest, state, {
        "schema_version": 1,
        "project_id": validation["project_id"],
        "input_fingerprint": validation["input_fingerprint"],
        "status": overall,
        "iterations": state.get("iterations", 0),
        "criteria": criteria_status,
        "schematic_preflight": validation["preflight"],
        "open_schematic_issues": open_issues,
        "rule": (
            "Continue autonomously while status is continue. Ask a human only for an open schematic "
            "defect or a genuinely unavailable execution authority/resource."
        ),
    }


def record_evidence(args) -> dict:
    manifest, validation = validate_manifest(args.manifest)
    state = load_state(args.manifest, validation["project_id"])
    criterion_ids = {item["id"] for item in validation["criteria"]}
    if args.criterion not in criterion_ids:
        raise ValueError(f"unknown criterion: {args.criterion}")
    if args.kind not in VALID_EVIDENCE or args.result not in VALID_RESULT:
        raise ValueError("invalid evidence kind or result")
    evidence_path = Path(args.evidence).resolve()
    if not evidence_path.is_file():
        raise FileNotFoundError(f"evidence file does not exist: {evidence_path}")
    criterion = next(item for item in validation["criteria"] if item["id"] == args.criterion)
    dependencies = []
    if args.result == "verified" and args.kind == "live_server":
        dependencies = _validate_live_evidence(evidence_path, criterion["minimum_trials"])
    record = {
        "criterion": args.criterion,
        "kind": args.kind,
        "result": args.result,
        "evidence": str(evidence_path),
        "sha256": _sha256(evidence_path),
        "input_fingerprint": validation["input_fingerprint"],
        "dependencies": dependencies,
        "command": args.command,
        "note": args.note,
    }
    state["evidence"].append(record)
    state["iterations"] = int(state.get("iterations", 0)) + 1
    _write_json(state_path(args.manifest), state)
    return record


def add_schematic_issue(args) -> dict:
    _, validation = validate_manifest(args.manifest)
    state = load_state(args.manifest, validation["project_id"])
    schematic = Path(args.schematic).resolve()
    known = {Path(item["path"]): item for item in validation["schematics"]}
    if schematic not in known:
        raise ValueError("issue schematic is not listed in the project manifest")
    issue = {
        "id": f"schematic-{len(state['schematic_issues']) + 1}",
        "status": "open",
        "schematic": str(schematic),
        "schematic_sha256": known[schematic]["sha256"],
        "construct": args.construct,
        "position": args.position,
        "message": args.message,
        "required_human_action": args.required_action,
    }
    state["schematic_issues"].append(issue)
    _write_json(state_path(args.manifest), state)
    return issue


def close_schematic_issue(args) -> dict:
    _, validation = validate_manifest(args.manifest)
    state = load_state(args.manifest, validation["project_id"])
    for issue in state["schematic_issues"]:
        if issue.get("id") == args.issue:
            issue["status"] = "closed"
            issue["resolution_note"] = args.note
            _write_json(state_path(args.manifest), state)
            return issue
    raise ValueError(f"unknown schematic issue: {args.issue}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="operation", required=True)
    for name in ("validate", "status", "gate"):
        child = subparsers.add_parser(name)
        child.add_argument("manifest", type=Path)
    record = subparsers.add_parser("record")
    record.add_argument("manifest", type=Path)
    record.add_argument("--criterion", required=True)
    record.add_argument("--kind", choices=sorted(VALID_EVIDENCE), required=True)
    record.add_argument("--result", choices=sorted(VALID_RESULT), required=True)
    record.add_argument("--evidence", type=Path, required=True)
    record.add_argument("--command", required=True)
    record.add_argument("--note", default="")
    issue = subparsers.add_parser("schematic-issue")
    issue.add_argument("manifest", type=Path)
    issue.add_argument("--schematic", type=Path, required=True)
    issue.add_argument("--construct", type=int, required=True)
    issue.add_argument("--position", type=int, nargs=3, required=True)
    issue.add_argument("--message", required=True)
    issue.add_argument("--required-action", required=True)
    close = subparsers.add_parser("close-schematic-issue")
    close.add_argument("manifest", type=Path)
    close.add_argument("--issue", required=True)
    close.add_argument("--note", required=True)
    args = parser.parse_args(argv)
    try:
        if args.operation == "validate":
            _, validation = validate_manifest(args.manifest)
            output = validation
            code = 0 if validation["preflight"]["status"] == "passed" else 2
        elif args.operation in {"status", "gate"}:
            _, _, output = project_status(args.manifest)
            if args.operation == "status":
                code = 0
            else:
                code = 0 if output["status"] == "complete" else 2
        elif args.operation == "record":
            output = record_evidence(args)
            code = 0
        elif args.operation == "schematic-issue":
            output = add_schematic_issue(args)
            code = 2
        else:
            output = close_schematic_issue(args)
            code = 0
        print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
        return code
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "error", "message": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
