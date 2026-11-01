# Testing and deployment

## Layers of confidence

1. **Syntax:** Compile all `.lua` files with a compatible Lua parser (CI uses Lua 5.3).
2. **Pure logic:** Execute deterministic unit tests for modules without CraftOS dependencies.
3. **CraftOS runtime:** Confirm `require` paths, scheduling and terminal behavior inside Minecraft or an appropriate emulator.
4. **Peripheral integration:** Exercise actual attached hardware with its installed mods and exact version.
5. **End-to-end:** Verify reboots, errors, missing devices and network interruptions.

## CI

The repository includes a lightweight GitHub Actions workflow in `.github/workflows/lua-ci.yml`. It checks Lua 5.3 parsing and executes the pure `math3d`, `pid`, `round` and `sublevel_pose` tests. The GOCODE workflow additionally runs the Python/Lua simulators on Ubuntu and the data-only Chat runner on Windows. Passing CI **does not** prove that modded peripheral APIs are available or that every sample works in-game.

## Deployment

Copy only the required scripts and their dependencies to the target CraftOS computer. Keep names stable, explicitly configure peripherals and avoid loading unknown downloaded programs. Test startup behavior separately; a program named `startup.lua` can execute automatically when the computer boots.

## Reproducible reports

Record Minecraft version, CC:Tweaked version, loader, add-on versions, peripheral names, input conditions, error messages and CI/test outcomes. Never replace diagnostic facts with guesses.

Sources: https://tweaked.cc/ and https://tweaked.cc/guide/computer_startup.html
