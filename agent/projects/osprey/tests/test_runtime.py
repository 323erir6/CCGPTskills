"""Smoke test GOCODE's SYNTHETIC device pipeline, not Minecraft reachability."""
import unittest
from agent.projects.osprey.tools.build_schematic import build_nbt, create_layout
from agent.sim.nbt import loads
from agent.sim.schematics import normalize
from agent.sim.mod_runtime import ModRuntime
from agent.sim.rigid import World


class TestOspreyRuntime(unittest.TestCase):
    def test_rocket_devices_recognized(self):
        normalized=normalize(loads(build_nbt(create_layout())))
        runtime=ModRuntime(World(profile='sable-2.0.5',ground_y=168))
        body=runtime.load_construct(normalized['constructs'][0],
            position=(0,180,0),mass=23,
            device_config={'createpropulsion:solid_fuel_thruster':{
                'fuel_amount':800,'fuel_capacity':800,
                'fuel_per_second':1,'max_thrust_pn':230}})
        devices=[v for v in runtime.devices.values()]
        engines=[v for v in devices if v.block_id=='createpropulsion:solid_fuel_thruster']
        fins=[v for v in devices if v.block_id=='synaxis:compact_flap']
        self.assertEqual(len(engines),4)
        self.assertEqual(len(fins),4)
        for engine in engines:
            runtime.call(engine.key,'setPowerNormalized',1)
        snapshot=runtime.advance(3)
        self.assertEqual(len(snapshot['devices']),8)
        self.assertTrue(any(any(abs(x)>0 for x in d['last_force']) for d in snapshot['devices']))
        self.assertGreater(runtime.world.bodies[body].position[2],0)
        self.assertTrue(any('unresolved' in s.lower() or 'shape' in s.lower() or 'block' in s.lower() for s in snapshot['unresolved']))

if __name__=='__main__':unittest.main()
