# CC:AR — интеграция с CC

**Проверенный JAR:** `cc_ar-0.2.1.jar`.

## Назначение и особенности

AR-контроллер поддерживает именованные элементы 2D и 3D, метки и отдельную команду обновления. Порядок аргументов графических методов зависит от конкретного метода: перед использованием проверяйте точные сигнатуры и способ привязки к координатам. Это AR-геометрия, не символы монитора CraftOS и не GPU Tom's.

## Методы периферий и классов

| Java-периферия или группа API | Найденные методы-кандидаты |
| --- | --- |
| `ARControllerPeripheral` | `drawLine3D(id,color,x1,y1,z1,x2,y2,z2), drawLine2D(id,color,x1,y1,x2,y2), drawItemIcon2D(...), drawItemIcon3D(...), drawText2D(...), drawText3D(...), drawRect2D(...), delete(id), clear(), setLabel(label), getAllElements(), setAnchor(...), update()` |

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
