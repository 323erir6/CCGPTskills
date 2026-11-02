import gzip
import json
import struct
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from agent.scripts.autonomous_project import project_status, record_evidence, validate_manifest
from agent.sim.schematic_preflight import inspect


def _tag(name, kind, payload):
    raw = name.encode("utf-8")
    return bytes([kind]) + struct.pack(">H", len(raw)) + raw + payload


def _compound(value):
    return b"".join(_tag(key, item[0], item[1]) for key, item in value.items()) + b"\x00"


def _text(value):
    raw = value.encode("utf-8")
    return struct.pack(">H", len(raw)) + raw


def _list(kind, payloads):
    return bytes([kind]) + struct.pack(">i", len(payloads)) + b"".join(payloads)


def _position(x, y, z):
    return _list(3, [struct.pack(">i", value) for value in (x, y, z)])


def _schematic(path, blocks):
    palette_values = []
    palette_index = {}
    records = []
    for position, name, properties in blocks:
        key = (name, tuple(sorted(properties.items())))
        if key not in palette_index:
            palette_index[key] = len(palette_values)
            value = {"Name": (8, _text(name))}
            if properties:
                value["Properties"] = (10, _compound({
                    prop: (8, _text(setting)) for prop, setting in properties.items()
                }))
            palette_values.append(_compound(value))
        records.append(_compound({
            "pos": (9, _position(*position)),
            "state": (3, struct.pack(">i", palette_index[key])),
        }))
    root = _compound({
        "DataVersion": (3, struct.pack(">i", 3953)),
        "size": (9, _position(8, 4, 4)),
        "palette": (9, _list(10, palette_values)),
        "blocks": (9, _list(10, records)),
        "entities": (9, _list(10, [])),
    })
    path.write_bytes(gzip.compress(bytes([10, 0, 0]) + root))


class TestSchematicPreflight(unittest.TestCase):
    def test_direct_link_requires_face_adjacency(self):
        with tempfile.TemporaryDirectory() as directory:
            schematic = Path(directory) / "direct.nbt"
            _schematic(schematic, [
                ((0, 0, 0), "computercraft:computer_advanced", {}),
                ((1, 0, 0), "example:radar", {}),
                ((1, 1, 0), "example:servo", {}),
            ])
            passed = inspect([schematic], {"schema_version": 1, "links": [{
                "id": "radar", "method": "direct",
                "computer": {"construct": 0, "pos": [0, 0, 0]},
                "peripheral": {"construct": 0, "pos": [1, 0, 0]},
            }]})
            failed = inspect([schematic], {"schema_version": 1, "links": [{
                "id": "servo", "method": "direct",
                "computer": {"construct": 0, "pos": [0, 0, 0]},
                "peripheral": {"construct": 0, "pos": [1, 1, 0]},
            }]})
        self.assertEqual(passed["status"], "passed")
        self.assertEqual(failed["status"], "schematic_defect")
        self.assertIn("diagonal", failed["issues"][0]["message"])

    def test_wired_link_requires_one_connected_network(self):
        with tempfile.TemporaryDirectory() as directory:
            schematic = Path(directory) / "wired.nbt"
            _schematic(schematic, [
                ((0, 0, 0), "computercraft:computer_advanced", {}),
                ((1, 0, 0), "computercraft:cable", {"modem": "west_on_peripheral"}),
                ((2, 0, 0), "computercraft:cable", {"modem": "east_on_peripheral"}),
                ((3, 0, 0), "example:radar", {}),
            ])
            report = inspect([schematic], {"schema_version": 1, "links": [{
                "id": "radar", "method": "wired",
                "computer": {"construct": 0, "pos": [0, 0, 0]},
                "peripheral": {"construct": 0, "pos": [3, 0, 0]},
            }]})
        self.assertEqual(report["status"], "passed")
        self.assertIn("runtime", report["checks"][0]["result"])


class TestAutonomousProjectState(unittest.TestCase):
    @staticmethod
    def _live_evidence(root, name="live", trials=1):
        report = root / f"{name}-headless-report.json"
        report.write_text(json.dumps({
            "status": "passed",
            "engine": "real NeoForge dedicated server with original Sable and mod JARs",
            "loaded_mods": [
                {"id": "sable", "version": "2.0.5"},
                {"id": "computercraft", "version": "1.120.0"},
                {"id": "sable_headless_telemetry", "version": "1.0.0"},
            ],
        }), encoding="utf-8")
        summary = root / f"{name}-run-summary.json"
        summary.write_text(json.dumps({
            "status": "passed", "mode": "full", "mod_jars": 3,
            "report": str(report),
        }), encoding="utf-8")
        evidence = root / f"{name}-qualification.json"
        evidence.write_text(json.dumps({
            "status": "passed", "trials": trials, "runtime_summary": str(summary),
        }), encoding="utf-8")
        return evidence

    def test_live_evidence_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "TECHNICAL_SPEC.md").write_text("# Test\n", encoding="utf-8")
            schematic = root / "main.nbt"
            _schematic(schematic, [
                ((0, 0, 0), "computercraft:computer_advanced", {}),
                ((1, 0, 0), "example:radar", {}),
            ])
            (root / "connections.json").write_text(json.dumps({
                "schema_version": 1,
                "links": [{
                    "id": "radar", "method": "direct",
                    "computer": {"construct": 0, "pos": [0, 0, 0]},
                    "peripheral": {"construct": 0, "pos": [1, 0, 0]},
                }],
            }), encoding="utf-8")
            manifest = root / "project.json"
            manifest.write_text(json.dumps({
                "schema_version": 1,
                "project_id": "test-project",
                "technical_spec": "TECHNICAL_SPEC.md",
                "schematics": ["main.nbt"],
                "connection_contract": "connections.json",
                "runtime": {"profile": "6.9.3", "minecraft": "1.21.1",
                            "neoforge": "21.1.248", "mode": "full"},
                "acceptance_criteria": [{
                    "id": "radar-live",
                    "description": "Radar is visible to the computer in the live runtime.",
                    "measurement": "Number of enumerated radar peripherals.",
                    "pass_condition": "Exactly one expected radar is enumerated with required methods.",
                    "minimum_trials": 1,
                    "required_evidence": ["static", "live_server"],
                }],
            }), encoding="utf-8")
            _, validation = validate_manifest(manifest)
            self.assertEqual(validation["preflight"]["status"], "passed")
            _, _, pending = project_status(manifest)
            self.assertEqual(pending["status"], "continue")
            for kind in ("static", "live_server"):
                evidence = (self._live_evidence(root) if kind == "live_server"
                            else root / f"{kind}.json")
                if kind != "live_server":
                    evidence.write_text('{"status":"passed"}\n', encoding="utf-8")
                record_evidence(SimpleNamespace(
                    manifest=manifest, criterion="radar-live", kind=kind,
                    result="verified", evidence=evidence, command="test command", note="",
                ))
            _, _, complete = project_status(manifest)
        self.assertEqual(complete["status"], "complete")
        self.assertEqual(complete["criteria"][0]["missing_evidence"], [])

    def test_new_failure_or_changed_inputs_invalidates_old_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spec = root / "TECHNICAL_SPEC.md"
            spec.write_text("# Test\n", encoding="utf-8")
            schematic = root / "main.nbt"
            _schematic(schematic, [
                ((0, 0, 0), "computercraft:computer_advanced", {}),
                ((1, 0, 0), "example:radar", {}),
            ])
            (root / "connections.json").write_text(json.dumps({
                "schema_version": 1,
                "links": [{
                    "id": "radar", "method": "direct",
                    "computer": {"construct": 0, "pos": [0, 0, 0]},
                    "peripheral": {"construct": 0, "pos": [1, 0, 0]},
                }],
            }), encoding="utf-8")
            manifest = root / "project.json"
            manifest.write_text(json.dumps({
                "schema_version": 1,
                "project_id": "stale-evidence",
                "technical_spec": "TECHNICAL_SPEC.md",
                "schematics": ["main.nbt"],
                "connection_contract": "connections.json",
                "runtime": {"profile": "6.9.3", "minecraft": "1.21.1",
                            "neoforge": "21.1.248", "mode": "full"},
                "acceptance_criteria": [{
                    "id": "radar-live", "description": "Radar is enumerated.",
                    "measurement": "Enumeration count.", "pass_condition": "Count is one.",
                    "minimum_trials": 1, "required_evidence": ["live_server"],
                }],
            }), encoding="utf-8")
            evidence = self._live_evidence(root)
            common = dict(manifest=manifest, criterion="radar-live", kind="live_server",
                          evidence=evidence, command="headless run", note="")
            record_evidence(SimpleNamespace(**common, result="verified"))
            self.assertEqual(project_status(manifest)[2]["status"], "complete")
            failed_evidence = root / "failed-live.json"
            failed_evidence.write_text('{"status":"failed"}\n', encoding="utf-8")
            failed_common = {**common, "evidence": failed_evidence}
            record_evidence(SimpleNamespace(**failed_common, result="failed"))
            self.assertEqual(project_status(manifest)[2]["status"], "continue")
            second_evidence = self._live_evidence(root, "live-again")
            second_common = {**common, "evidence": second_evidence}
            record_evidence(SimpleNamespace(**second_common, result="verified"))
            self.assertEqual(project_status(manifest)[2]["status"], "complete")
            dependency = Path(json.loads(second_evidence.read_text(encoding="utf-8"))["runtime_summary"])
            original_dependency = dependency.read_bytes()
            dependency.write_text('{"status":"tampered"}\n', encoding="utf-8")
            self.assertEqual(project_status(manifest)[2]["status"], "continue")
            dependency.write_bytes(original_dependency)
            self.assertEqual(project_status(manifest)[2]["status"], "complete")
            spec.write_text("# Changed test\n", encoding="utf-8")
            status = project_status(manifest)[2]
        self.assertEqual(status["status"], "continue")
        self.assertEqual(status["criteria"][0]["stale_records"], 3)


if __name__ == "__main__":
    unittest.main()
