# Getting started with CC:Tweaked

CC:Tweaked runs CraftOS programs written in Lua inside Minecraft computers, turtles and pocket computers. These examples use the built-in APIs rather than a desktop Lua interpreter.

## First program

1. Open a computer and run `edit hello`.
2. Enter `print("Hello, CraftOS!")`.
3. Save, close the editor and execute `hello`.
4. List attached devices with the built-in `peripherals` command.

## Execution model

- One CraftOS computer has an event queue. `os.pullEvent()` waits for events and normally raises a termination error for Ctrl+T.
- `sleep(seconds)` yields control to the environment; avoid unbounded busy loops.
- `parallel.waitForAny` and `parallel.waitForAll` cooperate by yielding, not by running OS threads.
- Code that relies on display colors must check `term.isColor()` where appropriate.
- Only turtles expose the `turtle` API. Peripheral add-ons require separately installed mods.

## File organization

Use a small entry program with dedicated modules for configuration, networking, devices, rendering and control. Prefer `require` for reusable libraries and keep device lookup close to initialization.

## Version checklist

Record Minecraft version, CC:Tweaked version, mod loader, peripheral add-on versions and exact device names. Version-dependent methods must be verified against installed devices. See `peripheral.getNames()` and `peripheral.getMethods(name)`.

## Running examples

Copy a single `.lua` file to a CraftOS computer, then run it by file name. For modules in `lib/`, copy the module and import it with `require` using the local module path.

## References

- https://tweaked.cc/
- https://tweaked.cc/module/peripheral.html
- https://tweaked.cc/module/os.html
