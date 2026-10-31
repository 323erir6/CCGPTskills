# Advanced Peripherals 0.7.61b — player detection and other APIs

**Installed JAR:** `AdvancedPeripherals-1.21.1-0.7.61b.jar`. Official reference: https://docs.advanced-peripherals.de/latest/peripherals/player_detector/ and https://docs.advanced-peripherals.de/latest/.

## Player Detector

**Peripheral type:** `player_detector` on Minecraft 1.21.1+; `playerDetector` on older versions. The mod [Enhanced Detector Radar](enhanced-detector-radar.md) changes the default precision of `getPlayerPos/getPlayer` to **three decimals** when optional precision is omitted.

| Lua API | Arguments | Return |
| --- | --- | --- |
| `getPlayerPos(username)` or `getPlayer(username)` | player name string | player info table or `nil` |
| `getOnlinePlayers()` | none | array of online player names |
| `getPlayersInRange(range)` | radius | names within range of detector |
| `getPlayersInCoords(posOne,posTwo)` | coordinate tables | names inside exclusive-upper-bound cuboid |
| `getPlayersInCubic(w,h,d)` | width/height/depth | names in detector-centered cuboid |
| `isPlayerInRange(range,username)` | number, string | boolean |
| `isPlayerInCoords(posOne,posTwo,username)` | tables, string | boolean |
| `isPlayerInCubic(w,h,d,...)` | numeric dimensions, potentially version-specific name argument | boolean |
| `isPlayersInRange(range)` | number | boolean: any player in range |
| `isPlayersInCoords(posOne,posTwo)` | tables | boolean |
| `isPlayersInCubic(w,h,d)` | dimensions | boolean |

**Coordinate tables:** `{x=number,y=number,z=number}`. The coordinate-region interval is **[x1,x2), [y1,y2), [z1,z2)**: the upper corner is exclusive. A zero-size region contains no positions. Range is centered on the *detector block*, not on the connected computer.

**Player info fields** documented for supported versions: `uuid`, `name`, `dimension`, `eyeHeight`, `pitch`, `health`, `maxHealth`, `airSupply`, `respawnPosition`, `respawnDimension`, `respawnAngle`, `yaw`, `x`, `y`, `z`. Some depend on version/configuration. `name` and `uuid` are documented specifically for 1.21.1+.

### Player detector events

| Event | Additional arguments | Meaning |
| --- | --- | --- |
| `playerClick` | `username, deviceName` | detector clicked |
| `playerJoin` | `username, dimension` | user enters server |
| `playerLeave` | `username, dimension` | user leaves server |
| `playerChangedDimension` | `username, fromDimension, toDimension` | dimension transition |

Events occur when the detector is connected to the computer; wrapping it is not required just to receive events. The listener should validate the peripheral/device name for click events.

```lua
local d = peripheral.find("player_detector") or peripheral.find("playerDetector")
assert(d, "Player Detector missing")
local first={x=-10,y=64,z=-10}
local last={x=11,y=80,z=11}
local people=d.getPlayersInCoords(first,last)
for _,name in ipairs(people or {}) do
  local p=d.getPlayerPos(name)
  if p and type(p.x)=="number" then
    print(name,("%.3f %.3f %.3f"):format(p.x,p.y,p.z))
  end
end
```

## Version, range and privacy notes

Multidimensional detection requires specific server configuration; the official docs mention `playerDetMultiDimensional=true` and `playerDetMaxRange=-1` in relevant releases. These values can be restricted by server administrators. Do not assume unlimited range or access to all dimensions. Player positional data must be processed in accordance with server privacy rules.

## Other installed Advanced Peripherals families

The installed JAR also references other CC APIs such as the following:

- **Geo Scanner:** block scans and area sampling; its method names must be looked up from the exact installed implementation.
- **Block Reader:** reading block and block-entity properties.
- **Environment Detector:** time, weather, environment and nearby states.
- **Inventory Manager:** inventory interaction and item handling.
- **Energy Detector:** energy storage observations.
- **Chat Box:** chat and message operations subject to permissions.
- **NBT Storage, Redstone Integrator and mod bridges:** distinct peripheral families.

These devices have separate access controls, method signatures and return tables. Use `peripheral.getNames`, `getType`, `getMethods` before integrating any one. Do **not** treat the above family names as guaranteed peripheral type strings.

### Reliable compatibility probe

```lua
for _,name in ipairs(peripheral.getNames()) do
  print(name,peripheral.getType(name))
  local methods=peripheral.getMethods(name) or {}
  table.sort(methods)
  print(table.concat(methods,", "))
end
```

**Evidence:** official 0.7 Player Detector docs and a static scan of the installed 0.7.61b JAR. The additional-family API field names have not been exhaustively validated here; avoid writing calls to unverified methods.