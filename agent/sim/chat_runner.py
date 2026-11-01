#!/usr/bin/env python3
"""Bounded JSON scenario runner for the text-only Minecraft Sable simulator.

The input format contains data only: it never evaluates Python or Lua from the
scenario. All values describe Minecraft blocks, ticks and simulation units.
This is not a real-world engineering or weapon-design calculator.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agent.sim.geometry import Compound
from agent.sim.rigid import World

SCHEMA_VERSION = 1
MAX_TICKS = 100_000
MAX_BODIES = 128
MAX_BLOCKS = 20_000
MAX_TRACE_SAMPLES = 2_000
MAX_ACTIONS = 10_000


def _number(value, label, *, minimum=None, maximum=None):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    value = float(value)
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{label} must be at most {maximum}")
    return value


def _integer(value, label, *, minimum=None, maximum=None):
    if type(value) is not int:
        raise ValueError(f"{label} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{label} must be at most {maximum}")
    return value


def _vector(value, length, label):
    if not isinstance(value, list) or len(value) != length:
        raise ValueError(f"{label} must be an array of {length} finite numbers")
    return tuple(_number(item, f"{label}[{index}]") for index, item in enumerate(value))


def _body_geometry(body, strict_shapes):
    blocks = body.get("blocks")
    boxes = body.get("boxes")
    if (blocks is None) == (boxes is None):
        raise ValueError("each body must define exactly one of blocks or boxes")
    if blocks is not None:
        if not isinstance(blocks, list) or not blocks:
            raise ValueError("body blocks must be a nonempty array")
        if len(blocks) > MAX_BLOCKS:
            raise ValueError(f"body exceeds {MAX_BLOCKS} blocks")
        palette = []
        palette_ids = {}
        records = []
        for index, block in enumerate(blocks):
            if not isinstance(block, dict):
                raise ValueError(f"blocks[{index}] must be an object")
            position = block.get("pos")
            if (not isinstance(position, list) or len(position) != 3
                    or not all(type(item) is int for item in position)):
                raise ValueError(f"blocks[{index}].pos must contain three integers")
            name = block.get("name", "minecraft:iron_block")
            properties = block.get("properties", {})
            if not isinstance(name, str) or not name or ":" not in name:
                raise ValueError(f"blocks[{index}].name must be a namespaced block id")
            if not isinstance(properties, dict) or not all(
                    isinstance(key, str) and isinstance(value, str)
                    for key, value in properties.items()):
                raise ValueError(f"blocks[{index}].properties must map strings to strings")
            key = (name, tuple(sorted(properties.items())))
            if key not in palette_ids:
                palette_ids[key] = len(palette)
                palette.append({"name": name, "properties": properties})
            records.append({"pos": position, "state": palette_ids[key]})
        return Compound.from_construct(
            {"palette": palette, "blocks": records}, strict_shapes=strict_shapes
        ), "minecraft_block_positions"

    if not isinstance(boxes, list) or not boxes:
        raise ValueError("body boxes must be a nonempty array")
    if len(boxes) > MAX_BLOCKS:
        raise ValueError(f"body exceeds {MAX_BLOCKS} boxes")
    primitives = []
    for index, box in enumerate(boxes):
        values = _vector(box, 6, f"boxes[{index}]")
        low, high = values[:3], values[3:]
        if not all(low[axis] < high[axis] for axis in range(3)):
            raise ValueError(f"boxes[{index}] must have increasing bounds")
        primitives.append(((low, high), index))
    return Compound(primitives, [], len(boxes)), "explicit_user_boxes"


def _normalise_actions(actions, names, ticks):
    if actions is None:
        return [], []
    if not isinstance(actions, list) or len(actions) > MAX_ACTIONS:
        raise ValueError(f"actions must be an array with at most {MAX_ACTIONS} entries")
    if actions and ticks == 0:
        raise ValueError("actions require ticks greater than zero")
    impulses = []
    continuous = []
    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            raise ValueError(f"actions[{index}] must be an object")
        kind = action.get("type")
        if kind not in {"impulse", "force", "torque"}:
            raise ValueError(f"actions[{index}].type is unsupported")
        body_name = action.get("body")
        if body_name not in names:
            raise ValueError(f"actions[{index}].body is unknown")
        vector = _vector(action.get("vector"), 3, f"actions[{index}].vector")
        start = _integer(action.get("tick", action.get("start_tick", 0)),
                         f"actions[{index}].start_tick", minimum=0, maximum=ticks - 1)
        if kind == "impulse":
            impulses.append((start, names[body_name], vector))
            continue
        end = _integer(action.get("end_tick", start + 1),
                       f"actions[{index}].end_tick", minimum=start + 1,
                       maximum=ticks)
        point = action.get("point")
        if point is not None:
            point = _vector(point, 3, f"actions[{index}].point")
        if kind == "torque" and point is not None:
            raise ValueError(f"actions[{index}].point is valid only for force")
        continuous.append((kind, start, end, names[body_name], vector, point))
    return impulses, continuous


def _assertions(assertions, names, world):
    if assertions is None:
        return []
    if not isinstance(assertions, list) or len(assertions) > 1000:
        raise ValueError("assertions must be an array with at most 1000 entries")
    results = []
    axes = {"x": 0, "y": 1, "z": 2}
    for index, assertion in enumerate(assertions):
        if not isinstance(assertion, dict):
            raise ValueError(f"assertions[{index}] must be an object")
        kind = assertion.get("type")
        body_name = assertion.get("body")
        body = world.bodies.get(names.get(body_name)) if body_name is not None else None
        passed = False
        actual = None
        if kind in {"position_range", "velocity_range"}:
            if body is None:
                raise ValueError(f"assertions[{index}].body is unknown")
            axis_name = assertion.get("axis")
            if axis_name not in axes:
                raise ValueError(f"assertions[{index}].axis must be x, y or z")
            source = body.position if kind == "position_range" else body.velocity
            actual = source[axes[axis_name]]
            minimum = (_number(assertion["min"], f"assertions[{index}].min")
                       if "min" in assertion else -math.inf)
            maximum = (_number(assertion["max"], f"assertions[{index}].max")
                       if "max" in assertion else math.inf)
            if minimum > maximum:
                raise ValueError(f"assertions[{index}] min exceeds max")
            passed = minimum <= actual <= maximum
        elif kind == "speed_range":
            if body is None:
                raise ValueError(f"assertions[{index}].body is unknown")
            actual = math.sqrt(sum(value * value for value in body.velocity))
            minimum = _number(assertion.get("min", 0), f"assertions[{index}].min", minimum=0)
            maximum = (_number(assertion["max"], f"assertions[{index}].max", minimum=0)
                       if "max" in assertion else math.inf)
            if minimum > maximum:
                raise ValueError(f"assertions[{index}] min exceeds max")
            passed = minimum <= actual <= maximum
        elif kind == "event":
            event_name = assertion.get("event")
            if not isinstance(event_name, str) or not event_name:
                raise ValueError(f"assertions[{index}].event must be a string")
            actual = sum(event.get("event") == event_name for event in world.events)
            minimum = _integer(assertion.get("min_count", 1),
                               f"assertions[{index}].min_count", minimum=0)
            passed = actual >= minimum
        elif kind == "max_unresolved_shapes":
            actual = sum(len(item.geometry.unresolved) for item in world.bodies.values())
            maximum = _integer(assertion.get("max", 0), f"assertions[{index}].max", minimum=0)
            passed = actual <= maximum
        else:
            raise ValueError(f"assertions[{index}].type is unsupported")
        results.append({"index": index, "type": kind, "passed": passed, "actual": actual})
    return results


def execute(scenario):
    if not isinstance(scenario, dict):
        raise ValueError("scenario must be a JSON object")
    if scenario.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
    ticks = _integer(scenario.get("ticks", 20), "ticks", minimum=0, maximum=MAX_TICKS)
    trace_every = _integer(scenario.get("trace_every", 0), "trace_every",
                           minimum=0, maximum=max(1, ticks))
    if trace_every and math.ceil(ticks / trace_every) + 1 > MAX_TRACE_SAMPLES:
        raise ValueError(f"trace would exceed {MAX_TRACE_SAMPLES} samples")
    world_spec = scenario.get("world", {})
    if not isinstance(world_spec, dict):
        raise ValueError("world must be an object")
    profile = scenario.get("profile", "sable-2.0.5")
    if profile not in {"sable-2.0.5", "generic"}:
        raise ValueError("profile must be sable-2.0.5 or generic")
    profile_arg = profile if profile != "generic" else None
    physics_hz = world_spec.get("physics_hz")
    if physics_hz is not None:
        physics_hz = _integer(physics_hz, "world.physics_hz", minimum=20, maximum=2000)
    gravity = world_spec.get("gravity")
    if gravity is not None:
        gravity = _vector(gravity, 3, "world.gravity")
    ground_y = world_spec.get("ground_y")
    if ground_y is not None:
        ground_y = _number(ground_y, "world.ground_y")
    ground_friction = world_spec.get("ground_friction")
    if ground_friction is not None:
        ground_friction = _number(ground_friction, "world.ground_friction", minimum=0)
    world = World(profile=profile_arg, physics_hz=physics_hz, gravity=gravity,
                  ground_y=ground_y, ground_friction=ground_friction)

    body_specs = scenario.get("bodies")
    if not isinstance(body_specs, list) or not body_specs or len(body_specs) > MAX_BODIES:
        raise ValueError(f"bodies must contain between 1 and {MAX_BODIES} entries")
    names = {}
    body_info = []
    strict_shapes = scenario.get("strict_shapes", False)
    if type(strict_shapes) is not bool:
        raise ValueError("strict_shapes must be a boolean")
    for index, body_spec in enumerate(body_specs):
        if not isinstance(body_spec, dict):
            raise ValueError(f"bodies[{index}] must be an object")
        name = body_spec.get("id")
        if not isinstance(name, str) or not name or name in names:
            raise ValueError(f"bodies[{index}].id must be a unique nonempty string")
        geometry, source = _body_geometry(body_spec, strict_shapes)
        static = body_spec.get("static", False)
        if type(static) is not bool:
            raise ValueError(f"bodies[{index}].static must be a boolean")
        ident = world.add(
            geometry,
            mass=body_spec.get("mass", 1.0),
            position=_vector(body_spec.get("position", [0, 0, 0]), 3,
                             f"bodies[{index}].position"),
            velocity=_vector(body_spec.get("velocity", [0, 0, 0]), 3,
                             f"bodies[{index}].velocity"),
            orientation=_vector(body_spec.get("orientation", [1, 0, 0, 0]), 4,
                                f"bodies[{index}].orientation"),
            angular_velocity=_vector(body_spec.get("angular_velocity", [0, 0, 0]), 3,
                                    f"bodies[{index}].angular_velocity"),
            damping=body_spec.get("damping"),
            restitution=body_spec.get("restitution", 0.0),
            static=static,
        )
        names[name] = ident
        body_info.append({"id": name, "numeric_id": ident, "geometry_source": source,
                          "geometry": geometry.summary()})

    impulses, continuous = _normalise_actions(scenario.get("actions"), names, ticks)
    impulses_by_tick = {}
    for tick, ident, vector in impulses:
        impulses_by_tick.setdefault(tick, []).append((ident, vector))

    if continuous:
        def apply_continuous(active_world, _dt):
            for kind, start, end, ident, vector, point in continuous:
                if start <= active_world.tick < end:
                    if kind == "force":
                        active_world.step_force(ident, vector, world_point=point,
                                                source="chat_json_scenario")
                    else:
                        active_world.step_torque(ident, vector, source="chat_json_scenario")
        world.add_physics_callback(apply_continuous)

    trace = []
    event_cursor = 0
    def capture_trace():
        nonlocal event_cursor
        snapshot = world.snapshot()
        snapshot["events"] = snapshot["events"][event_cursor:]
        snapshot["events_scope"] = "since_previous_trace_sample"
        event_cursor = len(world.events)
        return snapshot
    if trace_every:
        trace.append(capture_trace())
    for tick in range(ticks):
        for ident, vector in impulses_by_tick.get(tick, []):
            world.impulse(ident, vector)
        world.advance(1)
        if trace_every and ((tick + 1) % trace_every == 0 or tick + 1 == ticks):
            trace.append(capture_trace())

    assertion_results = _assertions(scenario.get("assertions"), names, world)
    passed = all(item["passed"] for item in assertion_results)
    final_snapshot = world.snapshot()
    for item in final_snapshot["bodies"]:
        item["scenario_id"] = next(name for name, ident in names.items() if ident == item["id"])
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if passed else "failed",
        "scenario": scenario.get("name", "unnamed"),
        "scope": "Minecraft 1.21.1 Sable modpack simulation only",
        "profile": profile,
        "units": {
            "distance": "Minecraft blocks",
            "time": "simulated seconds derived from game ticks",
            "mass": "simulation mass units; not a real-world material model",
        },
        "fidelity": {
            "classification": "source-informed deterministic approximation",
            "native_sable": False,
            "limitations": [
                "not Minecraft server execution",
                "not the native Rapier contact solver",
                "fixed-orientation translation CCD within each substep",
                "unsupported block shapes remain explicit",
            ],
        },
        "physics_hz": world.physics_hz,
        "gravity": world.gravity,
        "bodies": body_info,
        "assertions": assertion_results,
        "snapshot": final_snapshot,
        "trace": trace if trace_every else None,
        "force_log_entries": len(world.force_log),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path, help="trusted JSON data file")
    parser.add_argument("--out", type=Path, help="write report JSON")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)
    try:
        scenario = json.loads(args.scenario.read_text(encoding="utf-8"))
        report = execute(scenario)
        encoded = json.dumps(report, ensure_ascii=False, sort_keys=True,
                             indent=2 if args.pretty else None)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(encoded + "\n", encoding="utf-8")
        print(encoded)
        return 0 if report["status"] == "passed" else 2
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False),
              file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
