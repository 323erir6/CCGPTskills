import json
import tempfile
import unittest
from pathlib import Path

from agent.scripts.run_headless_sable import load_scenario, mod_manifest, read_instance


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


if __name__ == "__main__":
    unittest.main()
