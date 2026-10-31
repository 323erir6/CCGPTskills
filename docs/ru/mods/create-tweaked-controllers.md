# Create Tweaked Controllers — интеграция с CC

**Проверенный JAR:** `create_tweaked_controllers-1.21.1-1.2.7.jar`.

## Назначение и особенности

Индексы кнопок и осей относятся к настройке подключённого контроллера, а не к стандартной раскладке клавиатуры. getButton сообщает состояние кнопки, getAxis возвращает значение оси. Индексы и нормализация зависят от конфигурации. Режим точности меняет детализацию выходного значения, а не физическое качество датчика.

## Методы периферий и классов

| Java-периферия или группа API | Найденные методы-кандидаты |
| --- | --- |
| `TweakedLecternPeripheral` | `hasUser(), getUserUUID(), getButton(int), getAxis(int), setFullPrecision(boolean), isFullPrecision()` |

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
