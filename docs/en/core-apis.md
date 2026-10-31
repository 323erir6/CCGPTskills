# Core CraftOS API reference

The following is a curated map, not a replacement for the official versioned documentation.

| API | Purpose | Typical calls |
| --- | --- | --- |
| `term` | Terminal output | `getSize`, `setCursorPos`, `write`, `clear` |
| `colors` | Color constants | `colors.white`, `colors.blue` |
| `fs` | Sandboxed filesystem | `exists`, `open`, `makeDir`, `combine` |
| `settings` | Persistent configuration | `define`, `get`, `set`, `load`, `save` |
| `textutils` | Serialization and JSON | `serialize`, `unserialize`, `serializeJSON` |
| `peripheral` | Discovery and invocation | `getNames`, `getType`, `getMethods`, `wrap`, `find`, `call` |
| `redstone` | Logic and analog signals | `getInput`, `setOutput`, `getAnalogInput`, `setAnalogOutput` |
| `rednet` | ID-based modem communication | `open`, `send`, `receive`, `broadcast` |
| `gps` | Modem-based position | `locate` |
| `http` | HTTP/WebSockets | `get`, `post`, `websocket` |
| `turtle` | Mobile robot control | `forward`, `turnLeft`, `inspect`, `getFuelLevel` |

## Important conventions

`peripheral.wrap(name)` returns a wrapped device or `nil`. Wrapped functions are usually invoked with `device.method(args)`, not object-style colon syntax.

Use `fs.open(path, "r")` and close handles after reading. Use `fs.open(path, "w")` to replace content; use `"a"` to append.

`settings.save(path)` and `settings.load(path)` are explicit persistence operations. `settings.set` alone is not a durable save.

A modem may be local (side names) or reachable by wired network (network-attached peripheral names).

## Minimal safe file read

```lua
local h = fs.open("config.txt", "r")
if not h then error("Cannot open config.txt") end
local content = h.readAll()
h.close()
print(content)
```

## Sources

- https://tweaked.cc/
- https://tweaked.cc/module/settings.html
- https://tweaked.cc/module/peripheral.html
