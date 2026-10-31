# Advanced Peripherals: Player Detector

## English

Official documentation: https://docs.advanced-peripherals.de/latest/peripherals/player_detector/

**Version-specific type naming:** Older releases document `playerDetector`; Minecraft **1.21.1+** documentation identifies the peripheral type as `player_detector`. Read `peripheral.getNames()` and `peripheral.getType(name)` before selecting a type.

Documented operations include `getOnlinePlayers()`, `getPlayerPos(username)`, and `getPlayersInRange(range)`. Some return fields differ by version; `getPlayerPos` may return `nil`, and the distance limit/configuration may restrict results.

Player-related events include `playerJoin`, `playerLeave` and `playerClick`; verify event availability and argument order against the exact installed version.

Minimal safe logic:
```lua
local detector = peripheral.find("player_detector")
  or peripheral.find("playerDetector")
if not detector then error("Player Detector not found") end
local names = detector.getOnlinePlayers()
if type(names) ~= "table" then error("Unexpected player list") end
for _, name in ipairs(names) do
  local data = detector.getPlayerPos(name)
  if type(data) == "table" and type(data.x) == "number" then
    print(name, data.x, data.y, data.z)
  end
end
```

**Privacy:** Treat player positions as sensitive game-server data; use only where the server and players permit it.

## Русский

Официальная документация: https://docs.advanced-peripherals.de/latest/peripherals/player_detector/

**Названия типов зависят от версии:** в старых версиях `playerDetector`, в документации для Minecraft **1.21.1+** — `player_detector`. Перед использованием проверяйте реальные названия и типы.

Документированы `getOnlinePlayers()`, `getPlayerPos(username)` и `getPlayersInRange(range)`. Набор полей зависит от версии, `getPlayerPos` может вернуть `nil`, а конфигурация сервера может ограничивать дальность.

События: `playerJoin`, `playerLeave`, `playerClick`; наличие и параметры следует сверить с конкретной версией.

Координаты игроков являются чувствительной информацией игрового сервера; используйте их с учётом серверных правил.
