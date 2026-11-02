import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from agent.scripts.run_headless_sable import (
    HEADLESS_PROJECT,
    load_scenario,
    mod_manifest,
    read_instance,
    resolve_gradle_wrapper,
    stage_blueprints,
    stage_computer_programs,
)
from agent.tests.test_schematics import make_sable


class TestHeadlessSableLauncher(unittest.TestCase):
    def test_scenario_is_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scenario.json"
            path.write_text(json.dumps({"schema_version": 1, "duration_ticks": 20,
                                        "commands": [{"tick": 2, "command": "say test"}]}),
                            encoding="utf-8")
            self.assertEqual(load_scenario(path)["duration_ticks"], 20)
            path.write_text(json.dumps({"schema_version": 1, "duration_ticks": 20_000}),
                            encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duration_ticks"):
                load_scenario(path)

    def test_scenario_accepts_bounded_runtime_block_probes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scenario.json"
            path.write_text(json.dumps({
                "schema_version": 1,
                "duration_ticks": 20,
                "block_probes": [{"id": "controller", "pos": [0, 64, 0],
                                  "expected_block": "computercraft:computer_advanced",
                                  "from_tick": 5, "activate_computer": True,
                                  "turn_on": True,
                                  "expected_peripheral_types": ["speaker"]}],
            }), encoding="utf-8")
            probe = load_scenario(path)["block_probes"][0]
            self.assertEqual(probe["from_tick"], 5)
            self.assertTrue(probe["turn_on"])

    def test_exact_instance_versions_and_sable_jar_are_required(self):
        with tempfile.TemporaryDirectory() as directory:
            instance = Path(directory)
            mods = instance / "minecraft/mods"
            mods.mkdir(parents=True)
            (instance / "instance.cfg").write_text("[General]\nname=6.9.3\n", encoding="utf-8")
            (instance / "mmc-pack.json").write_text(json.dumps({"components": [
                {"uid": "net.minecraft", "version": "1.21.1"},
                {"uid": "net.neoforged", "version": "21.1.248"},
            ]}), encoding="utf-8")
            (instance / "instance.cfg").write_text("[General]\nname=6.9.2\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "base instance 6.9.3"):
                read_instance(instance)
            (instance / "instance.cfg").write_text("[General]\nname=6.9.3\n", encoding="utf-8")
            with self.assertRaisesRegex(FileNotFoundError, "Sable 2.0.5"):
                read_instance(instance)
            (mods / "sable-neoforge-1.21.1-2.0.5.jar").write_bytes(b"fixture")
            self.assertEqual(read_instance(instance)["components"]["net.neoforged"], "21.1.248")

    def test_manifest_hashes_only_enabled_jars(self):
        with tempfile.TemporaryDirectory() as directory:
            mods = Path(directory)
            (mods / "sable-neoforge-1.21.1-2.0.5.jar").write_bytes(b"sable")
            (mods / "another.jar").write_bytes(b"other")
            (mods / "Ixeris-4.6.5+1.21.1-neoforge.jar").write_bytes(b"client only")
            (mods / "old.jar.disabled").write_bytes(b"disabled")
            self.assertEqual(len(mod_manifest(mods, "full")), 2)
            minimal = mod_manifest(mods, "minimal")
            self.assertEqual([item["name"] for item in minimal],
                             ["sable-neoforge-1.21.1-2.0.5.jar"])

    def test_repository_gradle_wrapper_is_self_contained(self):
        wrapper = resolve_gradle_wrapper()
        self.assertEqual(wrapper.parent, HEADLESS_PROJECT.resolve())
        self.assertTrue((HEADLESS_PROJECT / "gradle/wrapper/gradle-wrapper.jar").is_file())

    def test_stages_blueprints_and_computer_programs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            blueprint = root / "vehicle.nbt"
            blueprint.write_bytes(make_sable())
            run_dir = root / "run"
            staged = stage_blueprints([f"vehicle={blueprint}"], run_dir)
            self.assertEqual(staged[0]["constructs"], 1)
            self.assertTrue((run_dir / "sable-headless-world/sable_blueprints/vehicle.nbt").is_file())

            source = root / "program"
            source.mkdir()
            (source / "startup.lua").write_text("print('ready')\n", encoding="utf-8")
            manifest = root / "computers.json"
            manifest.write_text(json.dumps({"schema_version": 1, "computers": [
                {"id": 42, "source": "program"},
            ]}), encoding="utf-8")
            programs = stage_computer_programs(manifest, run_dir)
            self.assertEqual(programs[0]["files"], 1)
            self.assertTrue((run_dir / "sable-headless-world/computercraft/computer/42/startup.lua").is_file())

    def test_direct_script_execution_can_import_blueprint_parser(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            blueprint = root / "vehicle.nbt"
            blueprint.write_bytes(make_sable())
            run_dir = root / "run"
            script = HEADLESS_PROJECT.parent / "scripts/run_headless_sable.py"
            code = (
                "import runpy; from pathlib import Path; "
                f"ns=runpy.run_path({str(script)!r}); "
                f"ns['stage_blueprints'](['vehicle='+{str(blueprint)!r}], Path({str(run_dir)!r}))"
            )
            result = subprocess.run([sys.executable, "-c", code], cwd=root,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((run_dir / "sable-headless-world/sable_blueprints/vehicle.nbt").is_file())


if __name__ == "__main__":
    unittest.main()
