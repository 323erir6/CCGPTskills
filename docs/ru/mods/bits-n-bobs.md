# Bits n Bobs — интеграция с CC

**Проверенный JAR:** `bits_n_bobs-2.3.5.jar`.

## Назначение и особенности

Есть интеграция Headlamp с CC. Метод `setLamp` найден в Java, но фактические аргументы Lua и объект управления зависят от адаптера. Параметр Java `ILuaContext` вводится CC автоматически и **не передаётся из Lua**. Проверяйте `peripheral.getMethods` и используйте безопасный тест яркости.

## Методы периферий и классов

| Java-периферия или группа API | Найденные методы-кандидаты |
| --- | --- |
| `HeadlampPeripheral` | `setLamp(luaContext, brightness:int, ...) — Java declaration includes injected CC context` |

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
