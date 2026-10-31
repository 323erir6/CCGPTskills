# Create (base mod) — интеграция с CC

**Проверенный JAR:** `create-1.21.1-6.0.10.jar`.

## Назначение и особенности

В Create 6.0.10 найдены классы с поддержкой CC. Многие интеграции реализуются через generic peripheral и вспомогательные Lua-объекты, а не по принципу «один блок — один Java-класс Peripheral». Фактический набор доступных методов зависит от установленного блока и адаптера. Перечень выше — карта интеграций; окончательные имена команд нужно получить инспектором периферии.

## Методы периферий и классов

| Java-периферия или группа API | Найденные методы-кандидаты |
| --- | --- |
| `Kinetic gauges and motors` | `SpeedGaugeBlockEntity, StressGaugeBlockEntity, CreativeMotorBlockEntity, SpeedControllerBlockEntity, SequencedGearshiftBlockEntity` |
| `Display and logistics` | `DisplayLinkBlockEntity, NixieTubeBlockEntity, PackagerBlockEntity, RepackagerBlockEntity, StockTickerBlockEntity, RedstoneRequesterBlockEntity` |
| `Railway and machinery` | `TrackObserverBlockEntity, StationBlockEntity, SignalBlockEntity, StickerBlockEntity, Portable interfaces` |
| `ComputerCraft bridge` | `AbstractComputerBehaviour and Lua objects for package/order data` |

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
