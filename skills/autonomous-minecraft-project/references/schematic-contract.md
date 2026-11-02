# Human-authored schematic contract

Schematics are immutable project inputs. The agent may inspect them and create placement or device metadata, but may not redesign or regenerate them unless the human explicitly requests a schematic edit.

## Required checks

- Parse format from root NBT tags, not filename extension.
- Preserve every Photomancy sublevel as a separate physical construction.
- Preserve palette states, block entity NBT, relative poses, anchors, and unavailable states.
- Identify each computer, peripheral, actuator, modem, cable, weapon, sensor, engine, assembler, and moving interface required by the technical specification.
- Verify orientation and unobstructed movement or firing clearance from actual block states.
- Never infer that blocks on different Sable constructions share a wired network.

## Computer and peripheral rule

For a direct link, the Manhattan distance between block coordinates must be exactly one on the same construction. A diagonal, edge, or corner touch is invalid.

For a wired link:

1. Computer and peripheral must be on one physical construction.
2. Each endpoint must be orthogonally attached to a wired modem.
3. The modem/cable path must be a single connected network on that construction.
4. The live computer must enumerate the peripheral and expected methods before the test starts.

Run:

```sh
python -m agent.sim.schematic_preflight first.nbt second.nbt \
  --contract project/connections.json --out agent-results/schematic-preflight.json
```

The connection contract uses global construction indexes in schematic argument order:

```json
{
  "schema_version": 1,
  "links": [
    {
      "id": "controller-to-radar",
      "method": "direct",
      "computer": {"construct": 0, "pos": [1, 2, 3], "block": "computercraft:computer_advanced"},
      "peripheral": {"construct": 0, "pos": [2, 2, 3], "block": "example:radar"}
    }
  ]
}
```

## Defect report

When a schematic prevents operation, report:

- schematic path and hash;
- construction index/name;
- exact block coordinates;
- actual block/state and expected condition;
- which acceptance criterion cannot run;
- the smallest schematic correction;
- whether unaffected work can continue.

Do not replace missing hardware with a simulated device and then present the result as live qualification.
