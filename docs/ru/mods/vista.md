# Vista — интеграция с CC

**Проверенный JAR:** `vista-1.21.1-5.5.7-neoforge (1).jar`.

## Назначение и особенности

ViewFinder предоставляет управление поворотом, масштабом и блокировкой камеры; WaveGate — чтение и запись URL. Знаки/единицы углов, диапазон zoom и ограничения URL не подтверждаются одним списком сигнатур. Это разные устройства.

## Методы периферий и классов

| Java-периферия или группа API | Найденные методы-кандидаты |
| --- | --- |
| `ViewFinderPeripheral` | `getYaw(), setYaw(number), getPitch(), setPitch(number), setZoom(int), getZoom(), setLocked(boolean), isLocked()` |
| `WaveGatePeripheral` | `getUrl(), setUrl(string)` |

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
