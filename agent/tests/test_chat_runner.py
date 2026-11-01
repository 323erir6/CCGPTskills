import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from agent.sim.chat_runner import execute


def cube_body(**overrides):
    body = {
        "id": "craft",
        "blocks": [{"pos": [0, 0, 0], "name": "minecraft:iron_block"}],
        "mass": 4,
        "position": [0, 10, 0],
    }
    body.update(overrides)
    return body


class TestChatRunner(unittest.TestCase):
    def test_sable_profile_is_default_and_deterministic(self):
        scenario = {"schema_version": 1, "ticks": 2, "bodies": [cube_body()]}
        first = execute(scenario)
        second = execute(scenario)
        self.assertEqual(first, second)
        self.assertEqual(first["physics_hz"], 40)
        self.assertEqual(first["gravity"], (0.0, -11.0, 0.0))
        self.assertEqual(first["status"], "passed")
        self.assertIn("Minecraft", first["scope"])

    def test_impulse_force_trace_and_assertions(self):
        scenario = {
            "schema_version": 1,
            "name": "controlled movement",
            "ticks": 4,
            "trace_every": 2,
            "world": {"gravity": [0, 0, 0]},
            "bodies": [cube_body(position=[0, 0, 0])],
            "actions": [
                {"type": "impulse", "tick": 0, "body": "craft", "vector": [4, 0, 0]},
                {"type": "force", "start_tick": 1, "end_tick": 3,
                 "body": "craft", "vector": [0, 8, 0]},
            ],
            "assertions": [
                {"type": "position_range", "body": "craft", "axis": "x", "min": 0.1},
                {"type": "velocity_range", "body": "craft", "axis": "y", "min": 0.1},
                {"type": "max_unresolved_shapes", "max": 0},
            ],
        }
        report = execute(scenario)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(len(report["trace"]), 3)
        self.assertEqual(report["trace"][0]["events"], [])
        self.assertGreater(report["force_log_entries"], 0)

    def test_ground_contact_event(self):
        scenario = {
            "schema_version": 1,
            "ticks": 100,
            "trace_every": 10,
            "world": {"ground_y": 0},
            "bodies": [cube_body(position=[0, 2, 0])],
            "assertions": [{"type": "event", "event": "terrain_contact"}],
        }
        report = execute(scenario)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["trace"][0]["events"], [])
        self.assertEqual(sum(len(item["events"]) for item in report["trace"]), 1)
        self.assertAlmostEqual(report["snapshot"]["bodies"][0]["position"][1], 0.5)

    def test_rejects_code_and_unbounded_inputs(self):
        with self.assertRaisesRegex(ValueError, "unsupported"):
            execute({"schema_version": 1, "ticks": 1, "bodies": [cube_body()],
                     "actions": [{"type": "python", "body": "craft", "vector": [0, 0, 0]}]})
        with self.assertRaisesRegex(ValueError, "ticks"):
            execute({"schema_version": 1, "ticks": 100_001, "bodies": [cube_body()]})
        with self.assertRaisesRegex(ValueError, "actions require"):
            execute({"schema_version": 1, "ticks": 0, "bodies": [cube_body()],
                     "actions": [{"type": "impulse", "body": "craft", "vector": [0, 0, 0]}]})

    def test_cli_exit_code_for_failed_assertion(self):
        root = Path(__file__).resolve().parents[2]
        scenario = {"schema_version": 1, "ticks": 0, "bodies": [cube_body()],
                    "assertions": [{"type": "position_range", "body": "craft",
                                    "axis": "y", "max": 0}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scenario.json"
            path.write_text(json.dumps(scenario), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "agent.sim.chat_runner", str(path)],
                cwd=root, capture_output=True, text=True, check=False,
            )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "failed")


if __name__ == "__main__":
    unittest.main()
