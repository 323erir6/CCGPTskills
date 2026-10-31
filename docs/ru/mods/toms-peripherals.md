# Tom's Peripherals — интеграция с CC

**Проверенный JAR:** `toms-peripherals-1.21-1.3.1.jar`.

## Назначение и особенности

GPU Tom's — не обычный терминал и не CC:AR. Методы распределяются динамически через ITMPeripheral, поэтому просмотр внешнего Java-класса не даёт полного списка Lua-методов вложенного GPU-класса. **Нельзя придумывать сигнатуры setSize, sync, draw и событий мыши.** Выполните инспектор на реальном устройстве и сохраните аргументы/ответы. При ускорении Lua через Sable CC Tick Sync графические операции могут оставаться в очереди обычных игровых тиков.

## Методы периферий и классов

| Java-периферия или группа API | Найденные методы-кандидаты |
| --- | --- |
| `GPU peripheral / monitor` | `GPUBlockEntity.GPUPeripheral, dynamic ITMPeripheral and ITMLuaObject dispatch; discover method names through peripheral.getMethods()` |
| `Keyboard` | `KeyboardBlockEntity emits event callbacks; input is not the same as vanilla terminal key events` |
| `Redstone port` | `RedstonePortBlockEntity provides per-side and bundled signals through its wrapped peripheral` |
| `Watchdog timer` | `WatchDogTimerBlockEntity exposes watchdog state and time limits through its peripheral` |
| `Other devices` | `Modem and monitor providers use the mod's own peripheral adapter` |

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
