#!/usr/bin/env python3
"""Validate user-authored Minecraft schematics before autonomous live testing.

The checker never repairs or invents schematic geometry. It verifies explicit
computer-to-peripheral links and reports defects that require a human-authored
schematic revision.
"""
from __future__ import annotations

import argparse
from collections import deque
import json
from pathlib import Path
import sys
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agent.sim.schematics import SchematicError, load


SCHEMA_VERSION = 1
COMPUTER_BLOCKS = {
    "computercraft:computer_normal",
    "computercraft:computer_advanced",
    "computercraft:computer_command",
}
NETWORK_BLOCKS = {"computercraft:cable", "computercraft:wired_modem_full"}
DIRECTIONS = {
    "east": (1, 0, 0),
    "west": (-1, 0, 0),
    "up": (0, 1, 0),
    "down": (0, -1, 0),
    "south": (0, 0, 1),
    "north": (0, 0, -1),
}


def _position(value: Any, label: str) -> tuple[int, int, int]:
    if not isinstance(value, list) or len(value) != 3 or not all(type(v) is int for v in value):
        raise ValueError(f"{label} must contain three integer block coordinates")
    return tuple(value)


def _neighbours(position: tuple[int, int, int]):
    for delta in DIRECTIONS.values():
        yield tuple(position[index] + delta[index] for index in range(3))


def _flatten(schematic_paths: list[Path]) -> list[dict]:
    constructs = []
    for source in schematic_paths:
        data = load(source)
        for local_index, construct in enumerate(data["constructs"]):
            palette = construct["palette"]
            blocks = {}
            for record in construct["blocks"]:
                state = palette[record["state"]]
                blocks[tuple(record["pos"])] = {
                    "name": state["name"],
                    "properties": state.get("properties", {}),
                    "block_entity": record.get("block_entity"),
                }
            constructs.append({
                "source": str(source),
                "source_construct": local_index,
                "source_id": construct.get("id"),
                "name": construct.get("name"),
                "blocks": blocks,
            })
    return constructs


def _endpoint(value: Any, label: str, constructs: list[dict]) -> tuple[int, tuple[int, int, int], dict]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    construct_index = value.get("construct")
    if type(construct_index) is not int or not 0 <= construct_index < len(constructs):
        raise ValueError(f"{label}.construct does not identify a physical construction")
    position = _position(value.get("pos"), f"{label}.pos")
    block = constructs[construct_index]["blocks"].get(position)
    if block is None:
        raise ValueError(f"{label} has no block at construct {construct_index}, position {list(position)}")
    expected = value.get("block")
    if expected is not None and (not isinstance(expected, str) or block["name"] != expected):
        raise ValueError(
            f"{label} expected {expected!r}, found {block['name']!r} at construct "
            f"{construct_index}, position {list(position)}"
        )
    return construct_index, position, block


def _attached_network_nodes(position: tuple[int, int, int], blocks: dict) -> set[tuple[int, int, int]]:
    attached = set()
    for direction, delta in DIRECTIONS.items():
        node_pos = tuple(position[index] - delta[index] for index in range(3))
        node = blocks.get(node_pos)
        if node is None or node["name"] not in NETWORK_BLOCKS:
            continue
        if node["name"] == "computercraft:wired_modem_full":
            attached.add(node_pos)
            continue
        modem = str(node["properties"].get("modem", ""))
        if modem.startswith(direction + "_"):
            attached.add(node_pos)
    return attached


def _network_component(start: set[tuple[int, int, int]], blocks: dict) -> set[tuple[int, int, int]]:
    visited = set(start)
    queue = deque(start)
    while queue:
        position = queue.popleft()
        for neighbour in _neighbours(position):
            block = blocks.get(neighbour)
            if block is None or block["name"] not in NETWORK_BLOCKS or neighbour in visited:
                continue
            visited.add(neighbour)
            queue.append(neighbour)
    return visited


def inspect(schematic_paths: list[Path], contract: dict) -> dict:
    if not isinstance(contract, dict) or contract.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"connection contract schema_version must be {SCHEMA_VERSION}")
    constructs = _flatten([Path(path) for path in schematic_paths])
    links = contract.get("links", [])
    if not isinstance(links, list):
        raise ValueError("connection contract links must be an array")

    issues = []
    checks = []
    used_computers = set()
    for index, link in enumerate(links):
        try:
            if not isinstance(link, dict):
                raise ValueError("link must be an object")
            method = link.get("method")
            if method not in {"direct", "wired"}:
                raise ValueError("method must be direct or wired")
            computer_construct, computer_pos, computer = _endpoint(
                link.get("computer"), f"links[{index}].computer", constructs
            )
            peripheral_construct, peripheral_pos, peripheral = _endpoint(
                link.get("peripheral"), f"links[{index}].peripheral", constructs
            )
            if computer["name"] not in COMPUTER_BLOCKS:
                raise ValueError(f"computer endpoint is {computer['name']!r}, not a CC:Tweaked computer")
            if computer_construct != peripheral_construct:
                raise ValueError(
                    "computer and peripheral are on different physical constructions; "
                    "all connected devices must be on the same Sable construction"
                )
            used_computers.add((computer_construct, computer_pos))
            distance = sum(abs(computer_pos[axis] - peripheral_pos[axis]) for axis in range(3))
            if method == "direct":
                if distance != 1:
                    detail = "diagonal contact is invalid" if max(
                        abs(computer_pos[axis] - peripheral_pos[axis]) for axis in range(3)
                    ) == 1 else "blocks are not face-adjacent"
                    raise ValueError(f"direct peripheral link is invalid: {detail}")
                result = "static_verified"
            else:
                blocks = constructs[computer_construct]["blocks"]
                computer_nodes = _attached_network_nodes(computer_pos, blocks)
                peripheral_nodes = _attached_network_nodes(peripheral_pos, blocks)
                if not computer_nodes:
                    raise ValueError("computer has no face-attached wired modem on this construction")
                if not peripheral_nodes:
                    raise ValueError("peripheral has no face-attached wired modem on this construction")
                component = _network_component(computer_nodes, blocks)
                if not component.intersection(peripheral_nodes):
                    raise ValueError("computer and peripheral wired modems are not in one cable network")
                result = "static_topology_verified_runtime_enumeration_required"
            checks.append({
                "index": index,
                "id": link.get("id", f"link-{index}"),
                "method": method,
                "construct": computer_construct,
                "computer": {"pos": list(computer_pos), "block": computer["name"]},
                "peripheral": {"pos": list(peripheral_pos), "block": peripheral["name"]},
                "result": result,
            })
        except ValueError as error:
            issues.append({"index": index, "id": link.get("id") if isinstance(link, dict) else None,
                           "message": str(error)})

    discovered_computers = []
    for construct_index, construct in enumerate(constructs):
        for position, block in construct["blocks"].items():
            if block["name"] in COMPUTER_BLOCKS:
                discovered_computers.append({
                    "construct": construct_index,
                    "pos": list(position),
                    "block": block["name"],
                    "saved_computer_id": next((block["block_entity"].get(key)
                                                for key in ("ComputerId", "ComputerID", "computer_id")
                                                if isinstance(block.get("block_entity"), dict)
                                                and type(block["block_entity"].get(key)) is int), None),
                    "saved_label": next((block["block_entity"].get(key)
                                          for key in ("Label", "label")
                                          if isinstance(block.get("block_entity"), dict)
                                          and isinstance(block["block_entity"].get(key), str)), None),
                    "covered_by_contract": (construct_index, position) in used_computers,
                })

    return {
        "schema_version": 1,
        "status": "schematic_defect" if issues else "passed",
        "rule": (
            "A computer must be orthogonally face-adjacent to its peripheral or connected "
            "through one wired-modem network, and every endpoint must belong to one physical construction."
        ),
        "constructs": [
            {key: value for key, value in construct.items() if key != "blocks"}
            | {"block_count": len(construct["blocks"])}
            for construct in constructs
        ],
        "checks": checks,
        "issues": issues,
        "discovered_computers": discovered_computers,
        "runtime_requirement": (
            "Every wired link must additionally pass peripheral.getNames/getMethods in the live runtime."
        ),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schematics", type=Path, nargs="+")
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        contract = json.loads(args.contract.read_text(encoding="utf-8"))
        report = inspect(args.schematics, contract)
        encoded = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(encoded, encoding="utf-8")
        print(encoded, end="")
        return 0 if report["status"] == "passed" else 2
    except (OSError, ValueError, TypeError, json.JSONDecodeError, SchematicError) as error:
        print(json.dumps({"status": "error", "message": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
