# Enhanced Detector Radar 1.0.5 — расширение API

**Источник:** [репозиторий](https://github.com/323erir6/Enhanced-Detector-Radar), коммит `e14b41b64a0d28871d69ec0bb51a2ee2a2ba1043`; изучены три Java Mixin из `src/main/java/dev/radarcompat/enhanceddetector/mixin/`. Мод расширяет уже существующие периферии, а **не создаёт новый самостоятельный тип радара**.

## Advanced Peripherals: Player Detector

`getPlayerPos(username[,precision])` и `getPlayer(username[,precision])` используют оригинальный API; если точность не указана, **3 знака после запятой** вместо прежнего значения. Явный аргумент точности сохраняет исходную семантику. Это изменение форматирования, а не повышение физической точности измерений.

В Minecraft 1.21.1 тип `player_detector`, в старых версиях `playerDetector`. Для несуществующего, недоступного или находящегося вне зоны игрока ответ может быть `nil`.

```lua
local detector = peripheral.find("player_detector") or peripheral.find("playerDetector")
assert(detector,"Player detector missing")
for _,name in ipairs(detector.getOnlinePlayers()) do
  local p=detector.getPlayerPos(name)
  if p and p.x and p.y and p.z then
    print(("%s: %.3f %.3f %.3f"):format(name,p.x,p.y,p.z))
  end
end
```

## NeoPeripheral Radar: `scanForSubLevels(radius[,absolute])`

Mixin перехватывает существующий `scanForSubLevels`. В творческом режиме радиус по умолчанию равен 16, иначе берётся `Config._RADAR_DEFAULT_RANGE`; в обычном режиме заданный радиус ограничивается диапазоном от 16 до `Config._RADAR_RANGE_LIMIT`. Абсолютный режим `absolute=true` допустим только для творческого радара.

**Ответ:** массив с индексами от 1. Исходные поля: `id` (таблица UUID), необязательное `name`, `x,y,z,distance,q_x,q_y,q_z,q_w`. Дополнительные поля:

| Поле | Тип | Значение |
| --- | --- | --- |
| `velocity_x` | number | Глобальная скорость X, блок/с |
| `velocity_y` | number | Глобальная скорость Y |
| `velocity_z` | number | Глобальная скорость Z |
| `size_x` | number | Локальная ширина ограничивающей области |
| `size_y` | number | Локальная высота |
| `size_z` | number | Локальная длина |

Неконечные компоненты скорости заменяются нулями. **Критически важно:** в обычном режиме `x,y,z` — приблизительные **относительные смещения от радара с шумом**, а не мировые координаты; ошибка пропорциональна расстоянию / π³. При этом `velocity_*` остаются в мировых осях.

Если установлен `sable_autonomous_chunk_loader`, этот Mixin отдаёт выполнение `scanForSubLevels` модулю загрузчика, чтобы избежать двух конкурирующих реализаций. Фактические поля нужно проверить в игре.

```lua
local radar=assert(peripheral.wrap("your_radar_name"))
for _,row in ipairs(radar.scanForSubLevels(256,false) or {}) do
  local x,y,z=row.velocity_x,row.velocity_y,row.velocity_z
  if type(x)=="number" and type(y)=="number" and type(z)=="number" then
    print(row.name or "unnamed",math.sqrt(x*x+y*y+z*z))
  end
end
```

## NeoPeripheral Sable Engine

Общий ограничитель частоты вызовов заменяется на `EmptyCallLimiter` при создании устройства. Флаг `sable_engine.enable` сохраняет своё значение; параметры `max_rate` и `rate_window` остаются в конфиге, но больше не ограничивают команды двигателя.

Новые Lua-методы:

- `getPhysicsState() -> table | nil`: целостный снимок состояния физического тела.
- `applyControlImpulse(linearX,linearY,linearZ,angularX,angularY,angularZ) -> boolean`: совместное применение линейного и углового импульса в мировых осях.
- `stepControl(linearX,linearY,linearZ,angularX,angularY,angularZ) -> table | nil`: применение импульсов и возврат состояния одним вызовом.

Поля снимка: положение `x,y,z`, ориентация `qx,qy,qz,qw`, линейная скорость `vx,vy,vz`, угловая скорость `wx,wy,wz`, масса `mass`. Неконечные компоненты импульсов отклоняются. Не смешивайте `q_w` в данных радара с `qw` в данных двигателя. Это именно **импульсы**, а не силы в единицу времени.

```lua
local engine=assert(peripheral.find("sable_engine"),"Sable engine missing")
local s=engine.getPhysicsState()
if s then print(textutils.serialize(s)) end
```

## Ограничения

- Отсутствующие методы: неверная версия или конфликт Mixin.
- Список радара ограничен реально доступными физическими конструкциями.
- Отмена лимита API не гарантирует высокой производительности сервера.
- Перед использованием координат уточняйте относительный/абсолютный режим.
- Если конструкция недоступна, `getPhysicsState` может вернуть `nil`.
- Проверяйте методы загруженного мода через `peripheral.getMethods(name)`.

**Исходники:** [PlayerDetectorPrecisionMixin](https://github.com/323erir6/Enhanced-Detector-Radar/blob/main/src/main/java/dev/radarcompat/enhanceddetector/mixin/PlayerDetectorPrecisionMixin.java), [RadarPeripheralMixin](https://github.com/323erir6/Enhanced-Detector-Radar/blob/main/src/main/java/dev/radarcompat/enhanceddetector/mixin/RadarPeripheralMixin.java), [SableEnginePeripheralMixin](https://github.com/323erir6/Enhanced-Detector-Radar/blob/main/src/main/java/dev/radarcompat/enhanceddetector/mixin/SableEnginePeripheralMixin.java).