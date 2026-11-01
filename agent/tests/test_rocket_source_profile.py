"""Unit tests for source-backed rocket extraction, independent of Minecraft runtime."""
import unittest
from agent.sim.rocket_source_profile import (
    SOLID_THRUSTER_BASE_NORTH, SAIL_BASE_Y, HE_SHELL_BASE_Y,
    orient_box, shape_for_block,
)
from agent.sim.rocket_mass_tracker import mass_properties

class TestRocketSourceProfile(unittest.TestCase):
    def test_exact_parts_from_bytecode(self):
        self.assertEqual(5,len(SOLID_THRUSTER_BASE_NORTH))
        self.assertEqual(SAIL_BASE_Y, ((0,6,0,16,10,16),))
        self.assertEqual(HE_SHELL_BASE_Y[0],(3,0,3,13,16,13))
    def test_sail_axis(self):
        self.assertEqual(orient_box(SAIL_BASE_Y[0],'sail','y'), [0,6,0,16,10,16])
        self.assertEqual(orient_box(SAIL_BASE_Y[0],'sail','x'), [6,0,0,10,16,16])
    def test_thruster_direction(self):
        self.assertEqual(orient_box(SOLID_THRUSTER_BASE_NORTH[0],'thruster','south'),[4,4,15,12,12,16])
    def test_mass_tracker_6_uniform_cubes(self):
        b=[{'pos':(0,0,z),'mass':.75,'local_center':(.5,.5,.5)} for z in range(6)]
        result=mass_properties(b)
        self.assertAlmostEqual(result['mass'],4.5)
        self.assertEqual(result['center_of_mass'],(.5,.5,3.))
        self.assertEqual(result['inertia_diagonal'],(13.875,13.875,.75))
        self.assertFalse(result['off_diagonal_present'])
    def test_mass_tensor_off_axis(self):
        result=mass_properties([{'pos':(0,0,0),'mass':1.,'local_center':(.5,.5,.5)},
                                {'pos':(2,1,0),'mass':1.,'local_center':(.5,.5,.5)}])
        self.assertNotEqual(result['inertia_tensor'][0][1],0.0)
        self.assertTrue(result['off_diagonal_present'])
    def test_unverified_requires_explicit_approval(self):
        shapes,reason=shape_for_block({'name':'unknown:shape'}, {'shapes':{}})
        self.assertIsNone(shapes)
        self.assertEqual(reason,'unverified')
if __name__=='__main__':unittest.main()
