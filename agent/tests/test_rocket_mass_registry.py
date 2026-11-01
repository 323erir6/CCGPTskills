"""Version-pinned mass rules for Create: Simulated and Sable 2.0.5."""
from pathlib import Path
import unittest
from agent.sim.rocket_mass_registry import MassRegistry
from agent.sim.rocket_mass_tracker import mass_properties
from agent.sim.schematics import load

ROOT=Path('/mnt/data/rocket_sim/jars')

class TestRocketMassRegistry(unittest.TestCase):
    def test_real_modpack_reference_mass(self):
        if not ROOT.exists(): self.skipTest('Installed JARs unavailable on CI')
        names={'sable':'sable-neoforge-1.21.1-2.0.5.jar',
             'simulated':'simulated-nested.jar',
             'propulsion':'createpropulsion-1.1.5.jar',
             'cbc':'createbigcannons-5.11.7+mc.1.21.1.jar',
             'cc':'cc-tweaked-1.21.1-forge-1.120.0.jar',
             'chunk_loader':'sable-autonomous-chunk-loader-1.8.1.jar'}
        reg=MassRegistry({key:ROOT/value for key,value in names.items()})
        rocket=load('/mnt/data/rszo_rocket_v0.nbt')['constructs'][0]
        report=reg.report(rocket)
        self.assertEqual([1.,1.,.25,.25,1.,1.], [b['mass'] for b in report['blocks']])
        self.assertEqual(report['total_mass'],4.5)
        self.assertTrue(reg.contains('sable:super_light','simulated:white_symmetric_sail'))
        items=[dict(pos=b['pos'],mass=b['mass'],local_center=(.5,.5,.5)) for b in report['blocks']]
        props=mass_properties(items)
        self.assertEqual(props['center_of_mass'],(.5,.5,3.))
        self.assertEqual(props['inertia_diagonal'],(17.875,17.875,.75))

    def test_tag_json_reading_with_fixture(self):
        import tempfile, zipfile, json
        with tempfile.TemporaryDirectory() as folder:
            jar=Path(folder)/'fake.jar'
            with zipfile.ZipFile(jar,'w') as z:
                z.writestr('data/create/tags/block/windmill_sails.json',
                           json.dumps({'values':['simulated:white_symmetric_sail']}))
                z.writestr('data/sable/tags/block/super_light.json',
                           json.dumps({'values':['#create:windmill_sails']}))
                z.writestr('data/sable/physics_block_properties/super_light.json',
                           json.dumps({'priority':1001,'selector':'#sable:super_light',
                                       'properties':{'sable:mass':0.25}}))
            registry=MassRegistry({'test':jar})
            sail=registry.mass_of('simulated:white_symmetric_sail',{'axis':'x'})
            self.assertEqual(sail['mass'],0.25)
            self.assertEqual(registry.mass_of('minecraft:stone')['mass'],1.0)

    def test_rule_precedence_with_mock(self):
        from collections import defaultdict
        reg=MassRegistry.__new__(MassRegistry)
        reg.tags=defaultdict(list, {'sable:super_light':['#create:windmill_sails'],
                                   'create:windmill_sails':['simulated:white_symmetric_sail']})
        reg.definitions=[{'selector':'#sable:super_light','mass':.25,'priority':1001,
                          'jar':'sable','file':'super_light.json','overrides':{}},
                         {'selector':'simulated:white_symmetric_sail','mass':.75,'priority':1100,
                          'jar':'test','file':'test.json','overrides':{'axis=z':{'sable:mass':1.25}}}]
        self.assertEqual(reg.mass_of('simulated:white_symmetric_sail',{'axis':'z'})['mass'],1.25)
        self.assertEqual(reg.mass_of('simulated:white_symmetric_sail',{'axis':'y'})['mass'],.75)
        self.assertEqual(reg.mass_of('minecraft:stone')['mass'],1.)

if __name__=='__main__':unittest.main()
