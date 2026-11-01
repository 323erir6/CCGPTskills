"""Fail-closed log validation tests for non-destructive, read-only experiments."""
import json
import math
import random
import copy
import tempfile
import unittest
from pathlib import Path
from agent.projects.osprey.qa.flight_log import read_frames,validate


def good_frame(i, t=None):
    return {
        'schema_version':1,'kind':'sable_pose','vehicle':'LAB-01','seq':i,
        't_s':i*.1 if t is None else t,'status':'ok',
        'pos':{'x':0.,'y':180.-i*.1,'z':0.},
        'orientation':{'x':0.,'y':0.,'z':0.,'w':1.},
        'velocity':{'x':0.,'y':-i*.05,'z':0.},
        'angular_velocity':{'x':0.,'y':0.,'z':0.},
    }


class ReadOnlyRecorderQualityTests(unittest.TestCase):
    def frames(self, count=20):
        return [good_frame(i) for i in range(count)]

    def test_valid_test_log_passes_but_never_qualifies_vehicle(self):
        report=validate(self.frames())
        self.assertEqual(report['status'],'passed')
        self.assertFalse(report['release_qualified'])
        self.assertEqual(report['destination_accuracy'],'not assessed')

    def test_nonfinite_position_rejected(self):
        a=self.frames();a[3]['pos']['x']=math.nan
        self.assertEqual(validate(a)['status'],'failed')

    def test_quaternion_magnitude_rejected(self):
        a=self.frames();a[3]['orientation']['w']=0
        self.assertEqual(validate(a)['status'],'failed')

    def test_missing_velocity_rejected(self):
        a=self.frames();del a[3]['velocity']
        self.assertEqual(validate(a)['status'],'failed')

    def test_bad_sequence_rejected(self):
        a=self.frames();a[6]['seq']=4
        self.assertEqual(validate(a)['status'],'failed')

    def test_nonmonotonic_time_rejected(self):
        a=self.frames();a[4]['t_s']=0.2
        self.assertEqual(validate(a)['status'],'failed')

    def test_large_time_gap_rejected(self):
        a=self.frames();a[4]['t_s']=5
        self.assertEqual(validate(a)['status'],'failed')

    def test_sensor_error_frame_rejected(self):
        a=self.frames();a[3]['status']='sensor_error'
        self.assertEqual(validate(a)['status'],'failed')

    def test_vehicle_identity_changed_rejected(self):
        a=self.frames();a[8]['vehicle']='SPURIOUS'
        self.assertEqual(validate(a)['status'],'failed')

    def test_insufficient_samples_rejected(self):
        self.assertEqual(validate(self.frames(5))['status'],'failed')

    def test_corrupted_json_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'log.jsonl'
            p.write_text(json.dumps(good_frame(0))+'\n'+json.dumps(good_frame(1))+'\n{'+'\n',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'corrupt JSON'):
                read_frames(p)

    def test_json_nan_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'log.jsonl'
            p.write_text('{"x": NaN}\n')
            with self.assertRaisesRegex(ValueError,'nonfinite'):
                read_frames(p)

    def test_deterministic_corruption_matrix_240_cases(self):
        rng=random.Random(20261101)
        for _ in range(240):
            frames=copy.deepcopy(self.frames())
            ix=rng.randint(1,len(frames)-2)
            variant=rng.randrange(6)
            f=frames[ix]
            if variant == 0: f['pos']['y']=math.inf
            elif variant == 1: f['seq']=-10
            elif variant == 2: f['t_s']=-3
            elif variant == 3: f['orientation']={'x':0,'y':0,'z':0,'w':0}
            elif variant == 4: f['velocity']['y']='nan'
            else: f['vehicle']='OTHER-OBJECT'
            self.assertEqual(validate(frames)['status'],'failed',msg=f'variant {variant}')

    def test_complete_jsonl_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'log.jsonl'
            expected=self.frames()
            p.write_text(''.join(json.dumps(e)+'\n' for e in expected),'utf-8')
            self.assertEqual(read_frames(p),expected)
            self.assertEqual(validate(read_frames(p))['status'],'passed')

if __name__=='__main__':unittest.main()
