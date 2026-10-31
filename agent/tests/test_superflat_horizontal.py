"""230 dirt + 1 bedrock + 1 grass: surface at Y=168, body center Y=168.5.

Approximate friction regression; not a validated native Rapier calculation.
"""
import unittest
from math import sqrt
from agent.sim.geometry import Compound
from agent.sim.rigid import World


def cube():
    return Compound.from_construct({
        "palette": [{"name": "minecraft:grass_block", "properties": {}}],
        "blocks": [{"pos": [0, 0, 0], "state": 0}],
    }, strict_shapes=True)


class TestSuperflatHorizontal(unittest.TestCase):
    def test_initial_z_speed_and_stop_threshold(self):
        world = World(physics_hz=120, gravity=(0, -11, 0),
                      ground_y=168.0, ground_friction=sqrt(0.525 * 0.5))
        body = world.add(cube(), position=(0, 300, 0),
                         velocity=(0, 0, 5), damping=0.09)
        for tick in range(1, 1200):
            world.advance(1)
            vx, vy, vz = world.bodies[body].velocity
            if sqrt(vx * vx + vy * vy + vz * vz) < 0.001:
                break
        else:
            self.fail("did not reach speed threshold in 60 seconds")
        x, y, z = world.bodies[body].position
        self.assertEqual(x, 0)
        self.assertAlmostEqual(y, 168.5, places=6)
        self.assertAlmostEqual(z, 21.8, delta=0.06)
        self.assertEqual(len(world.events), 1)
        self.assertEqual(world.events[0]["event"], "terrain_contact")
        print(f"SUPERFLAT_STOP tick={tick} time={world.time:.6f} "
              f"pos=({x:.6f}, {y:.6f}, {z:.6f}) "
              f"speed={sqrt(vx*vx+vy*vy+vz*vz):.8f}")

    def test_plane_height_and_rest(self):
        world = World(physics_hz=120, gravity=(0, -11, 0), ground_y=168)
        body = world.add(cube(), position=(0, 168.5, 0))
        world.advance(100)
        self.assertAlmostEqual(world.bodies[body].position[1], 168.5)
        self.assertAlmostEqual(world.bodies[body].velocity[1], 0)


if __name__ == "__main__":
    unittest.main()
