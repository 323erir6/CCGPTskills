#!/usr/bin/env python3
"""Text-only rigid-body replay from one or more Create/Photomancy .nbt blueprints.

A layout JSON is required for multiple bodies to avoid inventing world poses.
Rotating-body collision/complex mod shapes are approximations; see coverage.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys
if __package__ in (None, ""):
    sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from agent.sim.schematics import load
from agent.sim.geometry import Compound, ShapeRegistry
from agent.sim.rigid import World


def _vector(vals,length,label):
    if not isinstance(vals,list) or len(vals)!=length or not all(type(x) in (int,float) and math.isfinite(x) for x in vals):
        raise ValueError(f"{label} must be an array of {length} finite numbers")
    return tuple(float(x) for x in vals)


def execute(schematics, *, ticks=20, physics_hz=None, layout=None, registry=None,
            strict_shapes=False, gravity=None, trace=False,
            profile="sable-2.0.5", ground_y=None, ground_friction=None):
    if type(ticks) is not int or ticks < 0 or ticks > 100_000:
        raise ValueError("ticks must be an integer between 0 and 100000")
    if trace and ticks > 10_000:
        raise ValueError("trace is limited to 10000 ticks")
    if profile not in ("sable-2.0.5", "generic"):
        raise ValueError("profile must be sable-2.0.5 or generic")
    definitions=[]
    for path in schematics:
        info=load(Path(path))
        for construct in info["constructs"]:
            definitions.append((str(path),info["format"],construct))
    if not definitions:raise ValueError("no physical constructs found in schematic")
    if layout is None:
        if len(definitions)!=1:
            raise ValueError("multiple constructions require --layout JSON to define each world pose")
        layout=[{}]
    if len(layout)!=len(definitions):
        raise ValueError("layout length does not match physical construction count")
    world=World(physics_hz=physics_hz,gravity=gravity,
                profile=profile if profile != "generic" else None,
                ground_y=ground_y,ground_friction=ground_friction)
    info=[]
    for idx,((path,format,construct),placement) in enumerate(zip(definitions,layout)):
        if not isinstance(placement,dict):raise ValueError("invalid layout entry")
        geometry=Compound.from_construct(construct,registry=registry,strict_shapes=strict_shapes)
        pos=_vector(placement.get("position",[0,0,0]),3,"position")
        orient=_vector(placement.get("orientation",[1,0,0,0]),4,"orientation")
        velocity=_vector(placement.get("velocity",[0,0,0]),3,"velocity")
        angular=_vector(placement.get("angular_velocity",[0,0,0]),3,"angular_velocity")
        mass=placement.get("mass",1.0)
        ident=world.add(geometry,mass=mass,position=pos,velocity=velocity,
                        orientation=orient,angular_velocity=angular,
                        restitution=placement.get("restitution",0))
        info.append({"body_id":ident,"source":path,"format":format,"sublevel":construct["id"],
                     "pose_source":"explicit_layout" if placement else "simulator_origin_not_sable_pose",
                     "metadata_pose_raw":construct.get("relative_pose"),
                     "block_geometry":geometry.summary()})
    snapshots=[]
    for _ in range(ticks):
        snapshot=world.advance(1)
        if trace:snapshots.append(snapshot)
    return {"status":"ok","tick":world.tick,"physics_hz":world.physics_hz,
            "profile":profile,"gravity":world.gravity,
            "bodies":info,"snapshot":world.snapshot(),
            "trace":snapshots if trace else None,
            "fidelity":"schematic voxels + translational OBB CCD; not exact Sable physics"}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schematics",type=Path,nargs="+")
    parser.add_argument("--layout",type=Path,help="JSON list: position, orientation quaternion, velocity, mass")
    parser.add_argument("--shape-registry",type=Path)
    parser.add_argument("--strict-shapes",action="store_true")
    parser.add_argument("--profile",choices=("sable-2.0.5","generic"),default="sable-2.0.5")
    parser.add_argument("--hz",type=int)
    parser.add_argument("--gravity",type=float,nargs=3,metavar=("X","Y","Z"))
    parser.add_argument("--ground-y",type=float)
    parser.add_argument("--ground-friction",type=float)
    parser.add_argument("--ticks",type=int,default=20)
    parser.add_argument("--trace",action="store_true")
    parser.add_argument("--out",type=Path,help="write report JSON to file")
    args=parser.parse_args(argv)
    try:
        layout=json.loads(args.layout.read_text("utf-8")) if args.layout else None
        registry=ShapeRegistry.from_json(args.shape_registry) if args.shape_registry else None
        result=execute(args.schematics,ticks=args.ticks,physics_hz=args.hz,layout=layout,
                       registry=registry,strict_shapes=args.strict_shapes,trace=args.trace,
                       profile=args.profile,gravity=tuple(args.gravity) if args.gravity else None,
                       ground_y=args.ground_y,ground_friction=args.ground_friction)
        encoded=json.dumps(result,sort_keys=True,ensure_ascii=False)
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(encoded+"\n",encoding="utf-8")
        print(encoded)
        return 0
    except (ValueError,OSError,TypeError,RuntimeError) as exc:
        print(json.dumps({"status":"error","message":str(exc)},ensure_ascii=False),file=sys.stderr)
        return 1

if __name__=="__main__":raise SystemExit(main())
