"""Peripheral names, auxiliary devices and malformed-input checks."""
import unittest
from agent.sim.mod_devices import (DEVICE_FACTORIES, TiltAdapter, SignalPID,
    AnalogTransmission, AeroWorksServo, KineticSpeedController)
from agent.sim.mod_runtime import ModRuntime
from agent.sim.rigid import World


def one(name):
    return {"palette":[{"name":name,"properties":{}}],
            "blocks":[{"pos":[0,0,0],"state":0}]}


class TestAuxiliary(unittest.TestCase):
    def test_kinetic_state(self):
        rt=ModRuntime(World(profile="sable-2.0.5",gravity=(0,0,0)))
        rt.load_construct(one("create:rotation_speed_controller"))
        d=next(iter(rt.devices.values()))
        d.set_rpm(300)
        self.assertEqual(d.rpm,256)
        self.assertIn("no_create_kinetic_network",d.accuracy)

    def test_analog_signal(self):
        rt=ModRuntime(World(profile="sable-2.0.5",gravity=(0,0,0)))
        rt.load_construct(one("simulated:analog_transmission"))
        d=next(iter(rt.devices.values()))
        d.set_redstone(15)
        self.assertEqual(d.snapshot()["redstone_signal"],15)
        self.assertEqual(d.direction,-1)

    def test_tilt_cc(self):
        rt=ModRuntime(World(profile="sable-2.0.5",gravity=(0,0,0)))
        rt.load_construct(one("createpropulsion:tilt_adapter"))
        key=next(iter(rt.devices))
        rt.call(key,"setTargetAngle",-0.25)
        self.assertEqual(rt.devices[key].target,-.25)
        with self.assertRaises(AttributeError):rt.call(key,"setAngle",100)

    def test_pid_and_servo_state(self):
        rt=ModRuntime(World(profile="sable-2.0.5",gravity=(0,0,0)))
        rt.load_construct({"palette":[{"name":n,"properties":{}} for n in
                           ["synaxis:cimulink_pid_controller","aeroworks:mechanical_servo"]],
                          "blocks":[{"pos":[i,0,0],"state":i} for i in range(2)]})
        pid=next(d for d in rt.devices.values() if isinstance(d,SignalPID))
        servo=next(d for d in rt.devices.values() if isinstance(d,AeroWorksServo))
        pid.set_target(10);pid.set_input(7)
        servo.set_target_degrees(25)
        rt.advance(20)
        self.assertAlmostEqual(pid.output,3)
        self.assertGreater(servo.angle,0)
        self.assertLess(servo.angle,25)

if __name__=="__main__":unittest.main()
