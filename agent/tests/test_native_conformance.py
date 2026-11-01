"""Negative and positive checks for the generic, safe native contact QA gate."""
import unittest
from agent.validation.native_conformance import (
    make_cases, evaluate, DropCase, EXPECTED_CENTER_Y,
)


class TestNativeConformance(unittest.TestCase):
    def setUp(self):
        self.cases = make_cases(4)

    def sample(self, shift=0):
        return {
            c.id: {
                'position': [c.start_x, EXPECTED_CENTER_Y - .002 + shift, c.start_z],
                'velocity': [0., 0., 0.],
            } for c in self.cases
        }

    def test_distinct_symmetric_drop_sites(self):
        cases = make_cases(12)
        self.assertEqual(len(cases), 12)
        self.assertEqual(len({(c.start_x, c.start_z) for c in cases}), 12)
        self.assertTrue(all(c.start_y > EXPECTED_CENTER_Y for c in cases))

    def test_native_evidence_required(self):
        with self.assertRaisesRegex(ValueError, 'native runs are required'):
            evaluate(self.cases, [])

    def test_pass_does_not_claim_in_game_accuracy(self):
        report = evaluate(self.cases, [self.sample(), self.sample()])
        self.assertEqual(report['native_contact_status'], 'passed')
        self.assertEqual(report['game_equivalence'], 'unverified')
        self.assertIn('not tested', report['guidance_accuracy'])

    def test_vertical_contact_failure(self):
        batch = self.sample()
        batch[1]['position'][1] += 0.2
        self.assertEqual(evaluate(self.cases, [batch])['native_contact_status'], 'failed')

    def test_lateral_drift_failure(self):
        batch = self.sample()
        batch[1]['position'][0] += 0.4
        self.assertEqual(evaluate(self.cases, [batch])['native_contact_status'], 'failed')

    def test_nonzero_rest_speed_failure(self):
        batch = self.sample()
        batch[1]['velocity'][1] = 0.2
        self.assertEqual(evaluate(self.cases, [batch])['native_contact_status'], 'failed')

    def test_repeatability_failure(self):
        result = evaluate(self.cases, [self.sample(), self.sample(0.02)])
        self.assertEqual(result['native_contact_status'], 'failed')

    def test_nonfinite_native_result_is_rejected(self):
        batch = self.sample()
        batch[2]['position'][0] = float('nan')
        with self.assertRaisesRegex(ValueError, 'non-finite'):
            evaluate(self.cases, [batch])


if __name__ == '__main__':
    unittest.main()
