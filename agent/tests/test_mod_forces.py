"""Force and angular torque tests from mod actors into geometry-based body."""
import unittest
from agent.sim.mod_runtime import ModRuntime
from agent.sim.rigid import World
from agent.sim.mod_devices import ReactionWheel,ConfiguredActuator,HydraulicActuator


def one(name):
    return {"palette":[{"name":name,"properties":{"facing":"up"}}],
            "blocks":[{"pos":[0,0,0],"state":0}]}

class TestForces(unittest.TestCase):
    def test_reaction_wheel_changes_body_angular_velocity(self):
        runtime=ModRuntime(World(profile="sable-2.0.5",gravity=(0,0,0)))
        body=runtime.load_construct(one("createpropulsion:reaction_wheel"),mass=10,
             device_config={"createpropulsion:reaction_wheel":{"max_torque":2}})
        motor=next(iter(runtime.devices.values()))
        motor.set_command(1)
        runtime.advance(4)
        self.assertGreater(runtime.world.bodies[body].angular_velocity[1],0)
        self.assertGreater(runtime.world.bodies[body].orientation[2],0)

    def test_no_invented_reaction_wheel_power(self):
        runtime=ModRuntime(World(profile="sable-2.0.5",gravity=(0,0,0)))
        body=runtime.load_construct(one("createpropulsion:reaction_wheel"))
        dev=next(iter(runtime.devices.values()))
        dev.set_command(1)
        runtime.advance(5)
        self.assertEqual(runtime.world.bodies[body].angular_velocity,(0.,0.,0.))
        self.assertTrue(runtime.unresolved)

    def test_configured_burner_lift(self):
        runtime=ModRuntime(World(profile="sable-2.0.5",gravity=(0,-11,0)))
        body=runtime.load_construct(one("aeronautics:adjustable_burner"),mass=1,
            device_config={"aeronautics:adjustable_burner":{"max_force":25}})
        dev=next(iter(runtime.devices.values()))
        dev.set_throttle(1)
        runtime.advance(5)
        self.assertGreater(runtime.world.bodies[body].velocity[1],0)

    def test_hydraulic_travel(self):
        runtime=ModRuntime(World(profile="sable-2.0.5",gravity=(0,0,0)))
        runtime.load_construct(one("synaxis:hydraulic_linear_actuator"))
        dev=next(iter(runtime.devices.values()))
        dev.set_target(.5)
        runtime.advance(100)
        self.assertAlmostEqual(dev.position,.5,places=6)

if __name__=="__main__":unittest.main()
