# Peripheral discovery and adapters

## General discovery

```lua
for _, name in ipairs(peripheral.getNames()) do
  print(name, peripheral.getType(name))
  local methods = peripheral.getMethods(name) or {}
  print("  " .. table.concat(methods, ", "))
end
```

Device names from wired modems and mod packs can differ from face names. Prefer `peripheral.find(type)` when an exact, verified peripheral type is known. For a user-selected wired device, persist the actual name and revalidate it on startup.

## Defensive access

```lua
local name = "right"
if not peripheral.isPresent(name) then
  error("Required peripheral is missing: " .. name)
end
local device = assert(peripheral.wrap(name))
```

Wrap calls likely to fail after hot-unplug with `pcall` and check the success flag; do not assume a returned table is always valid.

## Add-on version differences

Third-party methods are **not** part of CC:Tweaked core. Their type names, signatures, limits, field names and thread behavior may change between versions.

At startup, probe the actual object type and available method list. Implement adapters with explicit capability checks. Fail with actionable error messages for unsupported versions rather than guessing method names.

## UI peripherals

A vanilla `monitor` supports terminal-style drawing and `monitor_touch` events on advanced monitors. A GPU peripheral from another mod is not equivalent to the vanilla monitor; discover its own documented API and coordinate system.

## See also

- [Modded integration notes](mods/installed-peripherals.md)
- [Peripheral inventory inspector](../../examples/inspect_peripherals.lua)
- https://tweaked.cc/module/peripheral.html
