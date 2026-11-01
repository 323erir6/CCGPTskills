"""Version-pinned full modpack inventory, API coverage and replay fixture."""
import gzip,json,unittest
from pathlib import Path
from agent.sim.mod_devices import DEVICE_FACTORIES
from agent.sim.mod_cli import run_plan

ROOT=Path(__file__).resolve().parents[2]

class TestModInventory(unittest.TestCase):
    def test_full_modpack_catalog_integrity(self):
        data=json.loads(gzip.decompress((ROOT/"agent/sim/mod_devices_manifest.json.gz").read_bytes()))
        self.assertEqual(data["schema_version"],2)
        self.assertGreaterEqual(len(data["artifacts"]),139)
        self.assertEqual(len(data["blockstates"]),11149)
        self.assertEqual(len(data["device_models"]),51)
        self.assertEqual(data["modelled_count"]+data["unmodelled_count"],len(data["blockstates"]))
        for name,cls in data["device_models"].items():
            self.assertEqual(DEVICE_FACTORIES[name][0].__name__,cls)
        seen=set()
        for entry in data["blockstates"]:
            self.assertNotIn(entry[0],seen)
            seen.add(entry[0])
            for source_index in entry[1:]:
                self.assertIsInstance(source_index,int)
                self.assertTrue(0<=source_index<len(data["artifacts"]))

    def test_scenario_json_contract(self):
        plan=json.loads((ROOT/"agent/scenarios/mod_blocks.json").read_text("utf-8"))
        result=run_plan(plan)
        self.assertEqual(result["world"]["tick"],20)
        self.assertEqual(len(result["devices"]),3)
        self.assertTrue(any(d["type"]=="synaxis_dynamic_motor" for d in result["devices"]))
        self.assertTrue(any(d["type"]=="creative_thruster" for d in result["devices"]))
        self.assertTrue(any(sum(v*v for v in d["last_force"])>0 for d in result["devices"]))
        self.assertTrue(result["events"])

if __name__=="__main__":unittest.main()
