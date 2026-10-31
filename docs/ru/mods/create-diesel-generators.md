# Create Diesel Generators — интеграция с CC

**Проверенный JAR:** `createdieselgenerators-1.21.1-1.3.15.jar`.

## Назначение и особенности

ChemicalTurretPeripheral предоставляет поворот по двум осям и spray. В Java поворот задаётся целочисленным аргументом, но единицы угла, пределы и условия работы распыления требуют проверки внутри игры. Это не та же периферия, что CBC CannonMount.

## Методы периферий и классов

| Java-периферия или группа API | Найденные методы-кандидаты |
| --- | --- |
| `ChemicalTurretPeripheral` | `getHorizontalRotation(), getVerticalRotation(), setHorizontalRotation(int), setVerticalRotation(int), spray()` |

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
