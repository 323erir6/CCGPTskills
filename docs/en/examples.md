# Example programs

All examples are self-contained except when they import a listed `lib/` module. Some require peripheral add-ons. Code examples are educational and must be tested on the exact game versions before being used for persistent automation.

| File | Expected purpose |
| --- | --- |
| [inspect_peripherals.lua](../../examples/inspect_peripherals.lua) | List all accessible devices, peripheral types and methods |
| [rednet_receiver.lua](../../examples/rednet_receiver.lua) | Receive only messages on a named protocol, validate packet envelope |
| [rednet_sender.lua](../../examples/rednet_sender.lua) | Send a versioned message to a chosen computer ID |
| [monitor_dashboard.lua](../../examples/monitor_dashboard.lua) | Character-cell monitor UI with resizing and touch events |
| [redstone_pulse.lua](../../examples/redstone_pulse.lua) | Bounded-duration Redstone pulse with output reset |
| [analog_redstone.lua](../../examples/analog_redstone.lua) | Analog level (0–15) with time limit and cleanup |
| [turtle_safe_move.lua](../../examples/turtle_safe_move.lua) | Turtle movement checking fuel and blocking on obstacles |
| [player_detector.lua](../../examples/player_detector.lua) | Advanced Peripherals Player Detector discovery and position display |
| [inventory_report.lua](../../examples/inventory_report.lua) | Read-only sparse-inventory report |
| [gps_position.lua](../../examples/gps_position.lua) | GPS coordinate query with timeout |
| [terminal_menu.lua](../../examples/terminal_menu.lua) | Keyboard-driven CraftOS text menu |
| [control_simulation.lua](../../examples/control_simulation.lua) | Standalone simulated plant driven by discrete PID |
| [position_speed.lua](../../examples/position_speed.lua) | Speed estimate from two manually sampled positions |
| [sublevel_world_position.lua](../../examples/sublevel_world_position.lua) | Sable local point to world point using pose |
| [sublevel_attitude.lua](../../examples/sublevel_attitude.lua) | Read Sable pose and display yaw/pitch/roll |
| [sublevel_speedometer.lua](../../examples/sublevel_speedometer.lua) | Sable velocity magnitude and signed forward speed |

## Installation

Copy the chosen example to the CraftOS computer and keep any referenced `lib/` modules in matching paths. For Rednet demos, place sender and receiver on separate CC computers with communicating modems. The receiver must be running and use the same protocol as the sender. For physics examples, install CC:Sable and verify `sublevel.isInPlotGrid()`.

## Test boundaries

Passing syntax checks alone does not prove that devices are installed or working. For monitors, verify screen size and touch events. For motors, verify axes/signs and permitted power. No example should be assumed safe for unattended physical automation until device-level verification.