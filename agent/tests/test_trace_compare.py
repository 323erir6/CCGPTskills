"""Checks for trace differences, including Python bool/int ambiguity."""
import unittest

from agent.sim.compare import compare


class TestTraceCompare(unittest.TestCase):
    def test_match(self):
        self.assertEqual([], compare({"tick": 2, "pose": [1.0, 2.0]},
                                     {"tick": 2, "pose": [1.0000001, 2.0]}))

    def test_mismatch(self):
        issues = compare({"speed": 5.0, "valid": True},
                         {"speed": 8.0, "valid": 1})
        self.assertEqual(2, len(issues))
        self.assertTrue(any("speed" in issue for issue in issues))

    def test_nested(self):
        issues = compare({"a": {"x": 1}}, {"a": {}})
        self.assertIn("missing field", issues[0])


if __name__ == "__main__":
    unittest.main()
