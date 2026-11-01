"""Behavioral tests for real modpack block contracts (not full native physics)."""
import unittest
from math import isclose
from agent.sim.geometry import Compound
from agent.sim.rigid import World
from agent.sim.mod_runtime import ModRuntime
from agent.sim.mod_devices import (
    DEVICE_FACTORIES, atmospheric_factor, ion_powered_fraction,
    PropulsionThruster, AeronauticsPropeller, SynaxisMotor, SynaxisJet,
    SynaxisFlap, AeroPropellerBearing, rotate_local,
)


def construct(blocks):
    names = list(dict.fromkeys(b[0] for b in blocks))
    return {"palette":[{"name":n,"properties":{"facing":"south"}} for n in names],
            "blocks":[{"pos":list(p),"state":names.index(n)} for n,p in blocks]}


class TestDevices(unittest.TestCase):
    def test_bytecode_atmospheric_factor(self):
        self.assertAlmostEqual(atmospheric_factor(True,0,1),1)
        self.assertAlmostEqual(atmospheric_factor(True,1,1),.2)
        self.assertAlmostEqual(atmospheric_factor(False,0,1),1.15)
        self.assertAlmostEqual(atmospheric_factor(False,1,1),1.)
        self.assertEqual(ion_powered_fraction(100,200,50),.25)

    def test_verified_registry_names(self):
        expected={"createpropulsion:creative_thruster","createpropulsion:thruster",
                  "createpropulsion:vector_thruster","synaxis:dynamic_joint_motor",
                  "synaxis:jet","synaxis:compact_flap","aeronautics:wooden_propeller",
                  "aeronautics:propeller_bearing"}
        self.assertTrue(expected.issubset(DEVICE_FACTORIES))

    def test_nbt_auto_attach_and_actual_peripheral_method_names(self):
        rt=ModRuntime(World(profile="sable-2.0.5",gravity=(0,0,0)))
        bid=rt.load_construct(construct([
            ("minecraft:stone",(0,0,0)),("createpropulsion:creative_thruster",(1,0,0)),
            ("synaxis:dynamic_joint_motor",(2,0,0))
        ]),mass=10)
        self.assertEqual(len(rt.devices),2)
        key=next(k for k in rt.devices if "creative_thruster" in k)
        motor=next(k for k in rt.devices if "dynamic_joint_motor" in k)
        self.assertEqual(rt.devices[key].cc_type,"creative_thruster")
        self.assertEqual(rt.devices[motor].cc_type,"synaxis_dynamic_motor")
        self.assertIn("GetTarget",rt.devices[motor].methods())
        self.assertNotIn("getTarget",rt.devices[motor].methods())
        self.assertRaises(AttributeError, rt.call,motor,"getTarget")
        self.assertIsNone(rt.call(motor,"setTarget",1.5))
        self.assertEqual(rt.call(motor,"GetTarget"),1.5)
        self.assertEqual(rt.world.bodies[bid].mass,10)

    def test_force_at_point_and_torque_in_body_orientation(self):
        rt=ModRuntime(World(profile="sable-2.0.5",gravity=(0,0,0)))
        bid=rt.load_construct(construct([
            ("minecraft:stone",(0,0,0)),("createpropulsion:creative_thruster",(2,0,0))
        ]),mass=10,device_config={"createpropulsion:creative_thruster":{"max_thrust_pn":100}})
        key=next(iter(rt.devices))
        rt.call(key,"setPowerNormalized",1)
        rt.advance(1)
        b=rt.world.bodies[bid]
        self.assertGreater(b.velocity[2],0)
        self.assertLess(b.angular_velocity[1],0)  # r_x positive, F_z positive -> torque_y negative
        self.assertAlmostEqual(sum(x*x for x in rt.devices[key].last_force)**.5,100,places=5)
        self.assertEqual(rt.devices[key].getPower(),1)
        self.assertTrue(rt.world.force_log)

    def test_redstone_priority_then_detach(self):
        rt=ModRuntime(World(profile="sable-2.0.5",gravity=(0,0,0)))
        rt.load_construct(construct([("createpropulsion:creative_thruster",(0,0,0))]),
                          device_config={"createpropulsion:creative_thruster":{"max_thrust_pn":500}})
        key=next(iter(rt.devices))
        rt.redstone(key,15)
        rt.advance(1)
        self.assertEqual(rt.devices[key].getPower(),1)
        rt.call(key,"setPowerNormalized",0.3)
        rt.advance(1)
        self.assertEqual(rt.devices[key].getPower(),0.3)
        rt.detach_computer(key)
        rt.advance(1)
        self.assertEqual(rt.devices[key].getPower(),1)

    def test_no_free_fuel_or_energy(self):
        rt=ModRuntime(World(profile="sable-2.0.5",gravity=(0,0,0)))
        rt.load_construct(construct([("createpropulsion:ion_thruster",(0,0,0))]),
                          device_config={"createpropulsion:ion_thruster":{
                              "max_thrust_pn":800,"energy_fe":0,"energy_per_second":10}})
        key=next(iter(rt.devices));rt.call(key,"setPowerNormalized",1)
        rt.advance(20)
        self.assertEqual(rt.devices[key].last_effective_thrust,0)
        self.assertEqual(rt.world.bodies[1].velocity,(0.,0.,0.))

    def test_exact_aero_small_prop_thrust_math(self):
        rt=ModRuntime(World(profile="sable-2.0.5",gravity=(0,0,0)))
        rt.load_construct(construct([("aeronautics:wooden_propeller",(0,0,0))]),mass=2)
        key=next(iter(rt.devices));rt.set_kinetic_rpm(key,120)
        rt.advance(60)
        dev=rt.devices[key]
        self.assertIsInstance(dev,AeronauticsPropeller)
        self.assertAlmostEqual(dev.thrust,120,delta=.1)
        self.assertGreater(rt.world.bodies[1].velocity[2],0)

    def test_bearing_sail_power_non_linear(self):
        rt=ModRuntime(World(profile="sable-2.0.5",gravity=(0,0,0)))
        rt.load_construct(construct([("aeronautics:propeller_bearing",(0,0,0))]),mass=2)
        key=next(iter(rt.devices));rt.set_kinetic_rpm(key,100)
        rt.advance(40)
        self.assertTrue(any("sail power" in s for s in rt.unresolved))
        self.assertEqual(rt.devices[key].thrust,0)
        rt2=ModRuntime(World(profile="sable-2.0.5",gravity=(0,0,0)))
        rt2.load_construct(construct([("aeronautics:propeller_bearing",(0,0,0))]),mass=2,
                          device_config={"aeronautics:propeller_bearing":{"sail_power":4}})
        key2=next(iter(rt2.devices));rt2.set_kinetic_rpm(key2,100)
        rt2.advance(50)
        self.assertAlmostEqual(rt2.devices[key2].thrust,4**1.5*100*.2,delta=.5)

    def test_synaxis_servo_controls_and_convergence(self):
        rt=ModRuntime(World(profile="sable-2.0.5",gravity=(0,0,0)))
        rt.load_construct(construct([("synaxis:dynamic_revolute_motor",(0,0,0))]))
        key=next(iter(rt.devices));dev=rt.devices[key]
        rt.call(key,"setPID",5,0,1)
        rt.call(key,"setTarget",1.0)
        rt.advance(100)
        self.assertAlmostEqual(dev.angle,1,delta=.1)
        self.assertEqual(rt.call(key,"GetTarget"),1)
        self.assertEqual(rt.call(key,"collect")["gainD"],1)

    def test_unknown_behavior_is_explicit(self):
        rt=ModRuntime(World(profile="sable-2.0.5",gravity=(0,0,0)))
        rt.load_construct(construct([("aeronautics:levitite",(0,0,0))]))
        self.assertFalse(rt.devices)
        self.assertTrue(any("not implemented" in s for s in rt.unresolved))

    def test_invalid_input_rejected(self):
        rt=ModRuntime(World(profile="sable-2.0.5",gravity=(0,0,0)))
        rt.load_construct(construct([("synaxis:jet",(0,0,0))]))
        key=next(iter(rt.devices))
        with self.assertRaises(ValueError):rt.call(key,"setTrust",float("nan"))
        rt.call(key,"setTrust",1)
        rt.advance(1)
        self.assertTrue(any("not source-calibrated" in e for e in rt.unresolved))


if __name__=="__main__":unittest.main()
