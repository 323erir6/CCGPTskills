# Create Radar — интеграция с CC

**Проверенный JAR:** `create_radar-0.4.4-1.21.1.jar`.

## Назначение и особенности

Методы реализованы через generic peripheral; аргумент Java BlockEntity передаётся адаптером автоматически и не указывается в Lua. Формат таблиц треков задаётся модом и требует просмотра реального результата. Пределы и знаки углов проверяются по установленному механизму. Контроллер управления и радарный подшипник — разные устройства.

## Методы периферий и классов

| Java-периферия или группа API | Найденные методы-кандидаты |
| --- | --- |
| `PlaneRadarPeripheral` | `getTracks(), getPosition(), getRange()` |
| `RadarBearingPeripheral` | `getTracks(), getPosition(), getRotation(), getRotationSpeed(), getRange(), getDishCount()` |
| `MonitorPeripheral` | `getSelectedTrackId(), getTracks(), getSelectedTrack()` |
| `FireControllerPeripheral` | `isPowered(), fireOn(), fireOff(), setPowered(boolean), keepFiring()` |
| `YawControllerPeripheral` | `setAngle(number), getAngle(), stopAuto()` |
| `PitchControllerPeripheral` | `setAngle(number), getAngle(), stopAuto()` |

## Проверка на компьютере в Minecraft

```lua
for _,name in ipairs(peripheral.getNames()) do
  local methods=peripheral.getMethods(name) or {}
  table.sort(methods)
  print(name,peripheral.getType(name))
  print(table.concat(methods,", "))
end
```

Программа только читает информацию и требует лишь стандартный CC:Tweaked.

## Проверенность и ограничения

Имена методов извлечены из Java-классов **именно установленного JAR** утилитой `javap`. Наличие Java-метода не означает автоматическую доступность в Lua: нужны аннотации, generic adapters, подходящий блок и разрешающие настройки. В таблице перечислены **кандидаты в Lua-методы**; служебные Java-конструкторы, `getType`, `equals`, `getTarget`, `attach` исключены. Формат возвращаемых таблиц и поведение приводов подтверждаются только испытанием в игре.
