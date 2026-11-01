"""Version-pinned scalar physics formulas, not full Rapier conformance tests."""
import unittest
from math import sqrt
from agent.sim.sable205 import (
    Sable205, SABLE_TAG, RAPIER_REVISION, EXTRACTED_JAR_SHA256,
    combine_friction, damp, free_step, coulomb_impulse_limit,
)
from agent.sim.geometry import Compound
from agent.sim.rigid import World


def cube():
    return Compound.from_construct({
        "palette": [{"name": "minecraft:grass_block", "properties": {}}],
        "blocks": [{"pos": [0, 0, 0], "state": 0}],
    }, strict_shapes=True)


class TestSable205(unittest.TestCase):
    def test_version_and_defaults(self):
        profile = Sable205()
        self.assertEqual(SABLE_TAG, "mc1.21.1-2.0.5-neoforge")
        self.assertEqual(len(RAPIER_REVISION), 40)
        self.assertEqual(len(EXTRACTED_JAR_SHA256), 64)
        self.assertEqual(profile.gravity, (0, -11, 0))
        self.assertEqual(profile.universal_drag, 0.09)
        self.assertEqual(profile.physics_hz, 40)
        self.assertAlmostEqual(profile.contact_friction, 0.7625)
        self.assertEqual(profile.max_ccd_substeps, 3)

    def test_damping_not_exponential(self):
        self.assertAlmostEqual(damp(5, 0.09, 0.025), 5 / 1.00225, places=12)
        self.assertLess(damp(5, .09, .025), 5)
        with self.assertRaises(ValueError):
            damp(1, -1, 0.025)

    def test_material_and_coulomb(self):
        self.assertEqual(combine_friction(.525, 1.), .7625)
        self.assertEqual(combine_friction(.525, 1., .5, .25), .0953125)
        self.assertEqual(coulomb_impulse_limit(4., .7625), 3.05)

    def test_no_contact_two_substeps(self):
        w = World(profile="sable-2.0.5")
        body_id = w.add(cube(), position=(0, 300, 0), velocity=(0, 0, 5))
        pos = (0., 300., 0.)
        vel = (0., 0., 5.)
        for _ in range(2):
            pos, vel = free_step(pos, vel, 1/40)
        w.advance(1)
        for a, b in zip(w.bodies[body_id].position, pos):
            self.assertAlmostEqual(a, b, places=10)
        for a, b in zip(w.bodies[body_id].velocity, vel):
            self.assertAlmostEqual(a, b, places=10)

    def test_approximate_contact_stop(self):
        w = World(profile="sable-2.0.5", ground_y=168)
        body_id = w.add(cube(), position=(0, 300, 0), velocity=(0, 0, 5))
        for i in range(1200):
            w.advance(1)
            b = w.bodies[body_id]
            if sqrt(sum(v*v for v in b.velocity)) < .001:
                break
        else:
            self.fail("no stopping event in 60 seconds")
        x, y, z = b.position
        self.assertAlmostEqual(x, 0., places=8)
        self.assertAlmostEqual(y, 168.5, places=8)
        self.assertGreater(z, 20.)
        self.assertLess(z, 23.)
        print(f"SABLE205_APPROX_STOP: x={x:.8f}, y={y:.8f}, z={z:.8f}, "
              f"time={w.time:.6f}, speed={sqrt(sum(v*v for v in b.velocity)):.8f}")


if __name__ == "__main__":
    unittest.main()
