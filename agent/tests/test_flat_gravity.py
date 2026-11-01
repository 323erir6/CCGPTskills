"""Superflat regression: 230 generated layers above Y=-64 end at Y=165.

The construction center is initially (0,300,0) and must rest at Y=166.5
after 400 game ticks at 120 Hz physics.
"""
import unittest
from agent.sim.geometry import Compound
from agent.sim.rigid import World


def block(identifier):
    return Compound.from_construct({
        "palette": [{"name": identifier, "properties": {}}],
        "blocks": [{"pos": [0, 0, 0], "state": 0}],
    }, strict_shapes=True)


class TestSuperflat(unittest.TestCase):
    def test_230_layers_resting_after_20_seconds(self):
        world = World(physics_hz=120, gravity=(0., -9.81, 0.))
        ground = world.add(block("minecraft:bedrock"), position=(0., 165.5, 0.), static=True)
        body = world.add(block("minecraft:grass_block"), position=(0., 300., 0.))
        result = world.advance(400)
        self.assertEqual(400, result["tick"])
        self.assertAlmostEqual(20., result["time"], places=8)
        self.assertEqual((0., 165.5, 0.), world.bodies[ground].position)
        for axis, expected in enumerate((0., 166.5, 0.)):
            self.assertAlmostEqual(expected, world.bodies[body].position[axis], places=7)
        self.assertAlmostEqual(0., world.bodies[body].velocity[1], places=7)
        self.assertEqual(1, len(world.events), "stationary contact should not flood event log")

    def test_static_ground_does_not_fall(self):
        world = World()
        ground = world.add(block("minecraft:stone"), position=(0., 0., 0.), static=True)
        world.advance(200)
        self.assertEqual((0., 0., 0.), world.bodies[ground].position)
        with self.assertRaisesRegex(ValueError, "static"):
            world.impulse(ground, (0., 1., 0.))


if __name__ == "__main__":
    unittest.main()
