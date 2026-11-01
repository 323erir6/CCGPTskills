"""Tests the generated Create .nbt using the existing GOCODE importer."""
from __future__ import annotations
import unittest
from pathlib import Path
from agent.projects.osprey.tools.build_schematic import create_layout,build_nbt
from agent.sim.nbt import loads
from agent.sim.schematics import normalize

class TestAirframe(unittest.TestCase):
    def test_nbt_roundtrip(self):
        raw=build_nbt(create_layout())
        normalized=normalize(loads(raw))
        self.assertEqual(normalized['format'],'create_structure_nbt')
        blocks=normalized['constructs'][0]['blocks']
        self.assertEqual(len(blocks),23)
        self.assertEqual(normalized['size'],[5,5,16])
    def test_symmetric_engines_and_fins(self):
        craft=create_layout()
        engines=[b for b in craft if b['name']=='createpropulsion:solid_fuel_thruster']
        fins=[b for b in craft if b['name']=='synaxis:compact_flap']
        self.assertEqual(len(engines),4)
        self.assertEqual(len(fins),4)
        self.assertEqual(sum(b['pos'][0]-2 for b in engines),0)
        self.assertEqual(sum(b['pos'][1]-2 for b in engines),0)
        self.assertEqual(sum(b['pos'][0]-2 for b in fins),0)
        self.assertEqual(sum(b['pos'][1]-2 for b in fins),0)
    def test_no_duplicate_positions(self):
        craft=create_layout()
        self.assertEqual(len(craft),len({tuple(b['pos']) for b in craft}))
    def test_no_block_entity_or_fuel_fabrication(self):
        nbt=loads(build_nbt(create_layout()))
        self.assertTrue(all('nbt' not in block for block in nbt['blocks']))
    def test_only_installed_mod_block_ids(self):
        ids={b['name'] for b in create_layout()}
        self.assertTrue(all(':' in name for name in ids))
        self.assertEqual(len(ids),5)

if __name__=='__main__':unittest.main()
