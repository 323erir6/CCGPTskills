import gzip
import tempfile
import unittest
from pathlib import Path
from agent.sim.simulate_schematic import execute
from agent.tests.test_schematics import make_create, make_sable

class TestTextOnlySimulation(unittest.TestCase):
    def test_single_create(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'create.nbt'
            path.write_bytes(gzip.compress(make_create()))
            result=execute([path],ticks=2,gravity=(0,0,0),strict_shapes=True)
        self.assertEqual(2,result['tick'])
        self.assertEqual(2,result['bodies'][0]['block_geometry']['blocks'])
        self.assertEqual('create_structure_nbt',result['bodies'][0]['format'])

    def test_multilevel_needs_layout(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'a.nbt';b=Path(d)/'b.nbt'
            a.write_bytes(gzip.compress(make_create()))
            b.write_bytes(gzip.compress(make_sable()))
            with self.assertRaisesRegex(ValueError,'require --layout'):
                execute([a,b],ticks=0)
            result=execute([a,b],ticks=0,layout=[{'position':[0,0,0]},
                {'position':[10,0,0]}])
            self.assertEqual(2,len(result['bodies']))
            self.assertEqual('sable_photomancy_v1',result['bodies'][1]['format'])
            self.assertEqual('explicit_layout',result['bodies'][1]['pose_source'])

if __name__=='__main__':unittest.main()
