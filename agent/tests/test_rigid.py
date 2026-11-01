import unittest
from agent.sim.geometry import Compound
from agent.sim.rigid import World,centroid_inertia

def shape(coords):
    return Compound.from_construct({"palette":[{"name":"minecraft:stone","properties":{}}],
        "blocks":[{"pos":list(p),"state":0} for p in coords]})

class TestVoxelRigid(unittest.TestCase):
    def test_mass_inertia_not_sphere(self):
        c=shape([(0,0,0),(1,0,0),(2,0,0)])
        com,I=centroid_inertia(c,3)
        self.assertEqual((1.5,.5,.5),com)
        self.assertLess(I[0],I[1])
        self.assertAlmostEqual(.5,I[0])

    def test_high_speed_thin_targets(self):
        w=World(physics_hz=20,gravity=(0,0,0))
        a=w.add(shape([(0,0,0)]),mass=1,position=(0,0,0),velocity=(1000,0,0))
        b=w.add(shape([(0,0,0)]),mass=1,position=(30,0,0))
        w.advance(1)
        self.assertEqual(1,len(w.events))
        self.assertAlmostEqual(500,w.bodies[a].velocity[0])
        self.assertAlmostEqual(500,w.bodies[b].velocity[0])

    def test_hollow_geometry_no_false_contact(self):
        w=World(physics_hz=20,gravity=(0,0,0))
        a=w.add(shape([(0,0,0),(4,0,0)]))
        b=w.add(shape([(0,0,0)]),position=(0,0,0))
        w.advance(1)
        self.assertEqual([],w.events)

    def test_rejects_invalid_vectors_and_flags(self):
        with self.assertRaisesRegex(ValueError,"gravity"):
            World(gravity=(0,float("nan"),0))
        w=World(gravity=(0,0,0))
        with self.assertRaisesRegex(ValueError,"static"):
            w.add(shape([(0,0,0)]),static="false")
        body=w.add(shape([(0,0,0)]))
        with self.assertRaisesRegex(ValueError,"impulse"):
            w.impulse(body,(1,float("inf"),0))

if __name__=='__main__': unittest.main()
