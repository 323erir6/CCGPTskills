"""Native-JNI readback integration, skipped when user-owned JAR unavailable."""
import os
from pathlib import Path
import unittest

from agent.projects.osprey.qa.native_recorder_fixture import generate
from agent.projects.osprey.qa.flight_log import validate


JAR = Path(os.getenv('GOCODE_SABLE_JAR', 'agent/native/test-mods/sable-neoforge-1.21.1-2.0.5.jar'))


@unittest.skipUnless(JAR.is_file(), 'Set GOCODE_SABLE_JAR to the user-owned Sable 2.0.5 JAR')
class TestNativeRecorder(unittest.TestCase):
    def test_native_cube_telemetry_integrity_and_qualifier(self):
        records=generate(JAR, 20)
        result=validate(records,min_samples=20,max_gap_s=.25)
        self.assertEqual(result['status'],'passed')
        self.assertEqual(result['valid_samples'],20)
        self.assertFalse(result['release_qualified'])
        self.assertEqual(result['destination_accuracy'],'not assessed')

if __name__=='__main__':unittest.main()
