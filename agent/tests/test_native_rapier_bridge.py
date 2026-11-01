"""Native JNI bridge tests: source protocol plus optional installed-JAR smoke run."""
import os
import unittest
from pathlib import Path

from agent.sim.native_rapier import SABLE_NAME, NESTED_JAR, BINARIES_NAME

SABLE_JAR = os.getenv("SABLE_JAR_PATH") or os.getenv("GOCODE_SABLE_JAR")


class TestNativeRapierBridge(unittest.TestCase):
    def test_source_available_without_redistributing_binary(self):
        root = Path(__file__).resolve().parents[1] / "native" / "src"
        self.assertTrue((root / "NativeHarness.java").is_file())
        self.assertTrue((root / "dev/ryanhcode/sable/physics/impl/rapier/Rapier3D.java").is_file())
        self.assertIn("2.0.5", SABLE_NAME)
        self.assertIn("sable_rapier", NESTED_JAR)
        self.assertIn("zip.l4z", BINARIES_NAME)

    def test_java_harness_exposes_native_collision_events(self):
        source = (Path(__file__).resolve().parents[1] / "native/src/NativeHarness.java").read_text()
        for command in ('"INIT"', '"SHIP"', '"BLOCK"', '"GROUND"',
                        '"STEP"', '"IMPULSE"', '"STATE"', '"COLLISIONS"'):
            self.assertIn(command, source)

    @unittest.skipUnless(SABLE_JAR, "set GOCODE_SABLE_JAR to the user-owned Sable 2.0.5 JAR")
    def test_real_native_voxel_terrain_contact(self):
        from agent.sim.native_rapier import sublevel_box_regression
        state = sublevel_box_regression(Path(SABLE_JAR))
        self.assertAlmostEqual(state["position"][1], 168.5, delta=.03)
        self.assertEqual(state["velocity"], [0., 0., 0.])


if __name__ == "__main__":
    unittest.main()
