#!/usr/bin/env python3
"""Run a repository-owned JSON plan against schematic-derived functional blocks."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from agent.sim.mod_runtime import ModRuntime
from agent.sim.schematics import load
from agent.sim.rigid import World
from agent.sim.geometry import ShapeRegistry


def run_plan(plan):
    if not isinstance(plan,dict):raise ValueError("JSON plan must be object")
    wopts=plan.get("world",{})
    runtime=ModRuntime(World(profile="sable-2.0.5",**wopts),
                       air_pressure=plan.get("air_pressure",1.0))
    if "schematic" in plan:
        raise ValueError("schematics must be resolved by --schematic; not from arbitrary plan paths")
    data=plan.get("normalized",{})
    if data:
        runtime.load_schematic(data,
          masses=plan.get("masses"),origins=plan.get("origins"),
          device_config=plan.get("device_config"),
          strict_shapes=plan.get("strict_shapes",False))
    for event in plan.get("events",[]):
        command=event.get("command")
        if command=="advance":runtime.advance(event.get("ticks",1))
        elif command=="call":runtime.call(event["key"],event["method"],*event.get("args",[]))
        elif command=="attach":runtime.attach_computer(event["key"])
        elif command=="detach":runtime.detach_computer(event["key"])
        elif command=="redstone":runtime.redstone(event["key"],event["signal"])
        elif command=="rpm":runtime.set_kinetic_rpm(event["key"],event["value"])
        else:raise ValueError("unknown command: "+str(command))
    return runtime.snapshot()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("plan",type=Path,help="trusted JSON test scenario")
    ap.add_argument("--schematic",type=Path,help="Create/Photomancy .nbt")
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    plan=json.loads(args.plan.read_text("utf-8"))
    if args.schematic:
        plan["normalized"]=load(args.schematic)
    outcome=run_plan(plan)
    report=json.dumps(outcome,indent=2,sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(report+"\n",encoding="utf-8")
    else:print(report)
    if outcome["unresolved"]:print(f"WARN {len(outcome['unresolved'])} unresolved behaviors",file=sys.stderr)
    return 0

if __name__=="__main__":raise SystemExit(main())
