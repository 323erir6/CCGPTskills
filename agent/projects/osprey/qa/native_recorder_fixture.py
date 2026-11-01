"""Native Sable/Rapier generic one-block freefall -> read-only log QA integration.

The fixture contains NO propulsion, fins, navigation, or target coordinates.
It exercises JNI sensor readback and the telemetry integrity pipeline only.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from agent.projects.osprey.qa.flight_log import validate, read_frames
from agent.sim.native_rapier import NativeScene

DT = 1 / 40
SENSOR_HZ = 10


def generate(jar: Path, samples: int = 60):
    if not isinstance(samples,int) or not 10 <= samples <= 600:
        raise ValueError('samples must be between 10 and 600')
    frames=[]
    with NativeScene(jar) as scene:
        scene.init(gravity=(0,-11,0),drag=0.09)
        mat=scene.material('minecraft:stone',mu=1.0)
        scene.ground(168,0,0,radius=1,material=mat)
        scene.ship(1,(5.5,181.0,5.5),(0.,0.,0.,1.),4.5,(.5,.5,.5),(.75,.75,.75),
                   (0,0,0,0,0,0),[(0,0,0,mat)])
        for i in range(samples):
            if i:
                for _ in range(4):
                    scene.step(DT)
            state=scene.state(1)
            def vec3(x):return dict(zip(('x','y','z'),x))
            frame={
                'schema_version':1,'kind':'sable_pose',
                'vehicle':'INERT-CUBE-JNI','seq':i,'t_s':i/SENSOR_HZ,
                'status':'ok','source':'native_sable_rapier_2.0.5_fixture',
                'pos':vec3(state['position']),
                'velocity':vec3(state['velocity']),
                'angular_velocity':vec3(state['omega']),
                'orientation':dict(zip(('x','y','z','w'),state['quat']))
            }
            frames.append(frame)
    return frames


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar',required=True,type=Path)
    parser.add_argument('--log',required=True,type=Path)
    parser.add_argument('--report',required=True,type=Path)
    parser.add_argument('--samples',type=int,default=60)
    args=parser.parse_args(argv)
    if not args.jar.is_file():
        parser.error('local user-owned Sable mod JAR required')
    frames=generate(args.jar,args.samples)
    args.log.parent.mkdir(parents=True,exist_ok=True)
    args.log.write_text(''.join(json.dumps(f,allow_nan=False)+'\n' for f in frames),encoding='utf-8')
    result=validate(read_frames(args.log),min_samples=10,max_gap_s=.25)
    result['source']='native_Sable_2.0.5_JNI_generic_cube_only'
    result['in_game_samples']=0
    result['actual_game_equivalence']='unverified'
    result['release_qualified']=False
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2)+'\n','utf-8')
    print(f'Inert-cube native readback: {result["status"]} ({result["samples"]} frames).')
    return 0 if result['status']=='passed' else 1

if __name__=='__main__':
    raise SystemExit(main())
