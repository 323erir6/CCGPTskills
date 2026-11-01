#!/usr/bin/env python3
"""Text-only CLI for Create schematics and Sable Photomancy NBT blueprints."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
if __package__ in (None, ""):
    sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from agent.sim.schematics import load, SchematicError
from agent.sim.geometry import Compound, ShapeRegistry


def main(argv=None)->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schematic",type=Path)
    parser.add_argument("--out",type=Path,help="write normalized geometry JSON fixture")
    parser.add_argument("--summary",action="store_true",help="print only geometry summary")
    parser.add_argument("--shape-registry",type=Path,help="versioned blockstate VoxelShape JSON")
    parser.add_argument("--strict-shapes",action="store_true",help="error on unresolved block shapes")
    parser.add_argument("--max-bytes",type=int,default=64*1024*1024)
    args=parser.parse_args(argv)
    try:
        data=load(args.schematic,max_bytes=args.max_bytes)
        registry=ShapeRegistry.from_json(args.shape_registry) if args.shape_registry else None
        geometry=[Compound.from_construct(c,registry=registry,strict_shapes=args.strict_shapes).summary()
                  for c in data["constructs"]]
        out={"status":"ok","format":data["format"],"constructs":geometry}
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
            out["fixture"]=str(args.out)
        print(json.dumps(out if args.summary or args.out else {**out,"data":data},ensure_ascii=False,sort_keys=True))
        return 0
    except (SchematicError,OSError,ValueError) as exc:
        print(json.dumps({"status":"error","message":str(exc)},ensure_ascii=False),file=sys.stderr)
        return 1

if __name__=="__main__":raise SystemExit(main())
