"""Live Minecraft parity gate rejects fabricated evidence and missing coverage."""
import copy
import unittest
from agent.validation.live_parity import audit, SCENARIO


class ParityTests(unittest.TestCase):
    def setUp(self):
        self.native = {
            'test_scope':SCENARIO,
            'physics_engine':'original Sable Rapier 2.0.5 JNI',
            'native_contact_status':'passed',
            'sable_jar_sha256':'abc123',
            'measurements':[],
        }
        for run in range(1,4):
            for case in range(1,9):
                self.native['measurements'].append({
                    'run':run,'case':case,'mass':1.0,
                    'initial_position':[case*4.0,174.0,0.0],
                    'final_position':[case*4.0,168.5,0.0],
                    'final_velocity':[0.0,0.0,0.0],
                })
        self.live = {
            'schema_version':1,'source':'minecraft_live',
            'capture_method':'cc_sable_passive_contact', 'time_basis':'verified_server_ticks',
            'test_scope':SCENARIO,'world_surface_y':168,'gravity_y':-11,
            'modpack_fingerprint':'modpack-hash', 'world_config_fingerprint':'config-hash',
            'sable_jar_sha256':'abc123',
            'measurements':copy.deepcopy(self.native['measurements']),
        }

    def test_missing_live_never_qualifies(self):
        r=audit(self.native,None)
        self.assertEqual(r['status'],'not_qualified')
        self.assertTrue(r['issues'])

    def test_synthetic_label_is_rejected(self):
        self.live['source']='synthetic_mock'
        with self.assertRaisesRegex(ValueError,'source and capture'):
            audit(self.native,self.live)

    def test_matching_fixture_tests_comparator_not_authenticity(self):
        r=audit(self.native,self.live)
        self.assertEqual(r['status'],'passive_parity_consistent')
        self.assertIn('self-reported',r['live_game_equivalence'])
        self.assertEqual(len(r['observations']),24)
        self.assertIn('not tested',r['weapons_accuracy'])

    def test_duplicate_capture_is_rejected(self):
        self.live['measurements'].append(self.live['measurements'][0])
        with self.assertRaisesRegex(ValueError,'duplicate observation'):
            audit(self.native,self.live)

    def test_mismatch_is_not_qualified(self):
        self.live['measurements'][0]['final_position'][1]+=0.4
        r=audit(self.native,self.live)
        self.assertEqual(r['status'],'not_qualified')
        self.assertFalse(r['observations'][0]['passed'])

    def test_missing_repeat_or_case_is_not_qualified(self):
        self.live['measurements']=self.live['measurements'][:-1]
        r=audit(self.native,self.live)
        self.assertIn('Mismatched case/run coverage',r['issues'][0])

    def test_unverified_clock_rejected(self):
        self.live['time_basis']='wall_clock_estimate'
        r=audit(self.native,self.live)
        self.assertEqual(r['status'],'not_qualified')
        self.assertTrue(any('timebase' in x for x in r['issues']))

    def test_wrong_jar_is_not_qualified(self):
        self.live['sable_jar_sha256']='different'
        self.assertEqual(audit(self.native,self.live)['status'],'not_qualified')

    def test_wrong_world_is_not_qualified(self):
        self.live['world_surface_y']=60
        self.assertEqual(audit(self.native,self.live)['status'],'not_qualified')

    def test_non_finite_is_rejected(self):
        self.live['measurements'][0]['final_position'][0]=float('nan')
        with self.assertRaisesRegex(ValueError,'finite'):
            audit(self.native,self.live)

    def test_legacy_native_report_does_not_invent_velocity(self):
        self.native['measurements'][0].pop('final_velocity')
        r=audit(self.native,self.live)
        self.assertEqual(r['status'],'not_qualified')
        self.assertIn('axis-resolved',r['issues'][0])

    def test_native_failure_rejected(self):
        self.native['native_contact_status']='failed'
        with self.assertRaisesRegex(ValueError,'not passed'):
            audit(self.native,self.live)


if __name__=='__main__':unittest.main()
