# Advanced Peripherals 0.7.61b — Player Detector и другие API

**Установленный JAR:** `AdvancedPeripherals-1.21.1-0.7.61b.jar`. Официальные справочники: https://docs.advanced-peripherals.de/latest/peripherals/player_detector/ и https://docs.advanced-peripherals.de/latest/.

## Детектор игроков

**Тип:** `player_detector` для Minecraft 1.21.1+, `playerDetector` в старых версиях. Расширение [Enhanced Detector Radar](enhanced-detector-radar.md) делает точность по умолчанию равной **трём десятичным знакам** при вызове `getPlayerPos/getPlayer` без аргумента точности.

| Lua-метод | Аргументы | Возвращает |
| --- | --- | --- |
| `getPlayerPos(username)`, `getPlayer(username)` | никнейм | информация об игроке либо `nil` |
| `getOnlinePlayers()` | нет | список игроков в сети |
| `getPlayersInRange(range)` | радиус | игроки рядом с детектором |
| `getPlayersInCoords(posOne,posTwo)` | две таблицы координат | игроки внутри области |
| `getPlayersInCubic(w,h,d)` | ширина, высота, глубина | игроки в области вокруг блока |
| `isPlayerInRange(range,username)` | число, строка | boolean |
| `isPlayerInCoords(posOne,posTwo,username)` | две таблицы, строка | boolean |
| `isPlayerInCubic(w,h,d,...)` | размеры, возможный аргумент имени зависит от версии | boolean |
| `isPlayersInRange(range)` | число | boolean: есть ли хотя бы один |
| `isPlayersInCoords(posOne,posTwo)` | две таблицы | boolean |
| `isPlayersInCubic(w,h,d)` | размеры | boolean |

**Координаты:** `{x=number,y=number,z=number}`. Для `getPlayersInCoords` верхняя граница не включается: **[x1,x2), [y1,y2), [z1,z2)**. Область нулевого размера пуста. Радиус рассчитывается от самого детектора, а не от подключённого компьютера.

**Данные игрока:** `uuid`, `name`, `dimension`, `eyeHeight`, `pitch`, `health`, `maxHealth`, `airSupply`, `respawnPosition`, `respawnDimension`, `respawnAngle`, `yaw`, `x`, `y`, `z`. Некоторые поля зависят от конфигурации и версии; `name` и `uuid` официально добавлены для 1.21.1+.

### События

| Событие | Дополнительные аргументы | Смысл |
| --- | --- | --- |
| `playerClick` | `username,deviceName` | нажатие по детектору |
| `playerJoin` | `username,dimension` | вход на сервер |
| `playerLeave` | `username,dimension` | выход |
| `playerChangedDimension` | `username,fromDimension,toDimension` | переход между измерениями |

Для получения событий достаточно подключённого детектора; `peripheral.wrap()` отдельно не обязателен. При обработке `playerClick` проверяйте имя устройства.

```lua
local d=peripheral.find("player_detector") or peripheral.find("playerDetector")
assert(d,"Player Detector missing")
local a={x=-10,y=64,z=-10}
local b={x=11,y=80,z=11}
for _,name in ipairs(d.getPlayersInCoords(a,b) or {}) do
  local p=d.getPlayerPos(name)
  if p and type(p.x)=="number" then
    print(name,("%.3f %.3f %.3f"):format(p.x,p.y,p.z))
  end
end
```

## Настройки дальности и конфиденциальность

Для межпространственного обнаружения могут понадобиться `playerDetMultiDimensional=true` и `playerDetMaxRange=-1` (как описано в официальной документации). Администратор может ограничить дальность и доступ к другим измерениям. Не считайте наличие детектора разрешением на сбор или публикацию координат игроков вопреки правилам сервера.

## Другие типы периферии в установленной версии

- **Geo Scanner:** поиск и изучение блоков в области.
- **Block Reader:** свойства блоков и сущностей блоков.
- **Environment Detector:** погода, время и условия среды.
- **Inventory Manager:** взаимодействие с инвентарями.
- **Energy Detector:** доступ к данным накопителей.
- **Chat Box:** чат и сообщения с ограничениями доступа.
- **NBT Storage, Redstone Integrator, мосты к другим модам:** отдельные интерфейсы.

Для них нельзя автоматически переносить аргументы детектора игроков. Проверяйте `peripheral.getNames`, `getType`, `getMethods` на установленном устройстве. Перечисленные английские названия групп **не являются гарантированными строковыми типами peripheral**.

```lua
for _,name in ipairs(peripheral.getNames()) do
  print(name,peripheral.getType(name))
  local methods=peripheral.getMethods(name) or {}
  table.sort(methods)
  print(table.concat(methods,", "))
end
```

**Достоверность:** официальный справочник Player Detector версии 0.7 и статический анализ JAR 0.7.61b. Полные поля остальных семейств ещё требуют проверки; не используйте вымышленные методы.