# Разработка на CC:Tweaked — автономный справочник на русском

Это отдельное русскоязычное дерево документации для **проверенной сборки Minecraft 1.21.1 / NeoForge**. Названия методов подтверждаются исходниками Java, установленными JAR или официальной документацией. Версии и уровни достоверности фиксируются; неподтверждённые сведения отмечаются отдельно.

[Область применения: только Minecraft](game-scope.md)

## Стандартные API CraftOS

[Начало работы](getting-started.md) · [Основные API](core-apis.md) · [События](events.md) · [Сеть](networking.md) · [Периферия](peripherals.md) · [Математика и управление](maths-and-control.md) · [Интерфейс](ui-and-input.md) · [Черепахи и инвентари](turtles-and-inventories.md) · [Надёжность](reliability.md) · [Тестирование](testing-and-deployment.md)

## Книги API по модам

[Advanced Peripherals 0.7.61b](mods/advanced-peripherals.md) · [Create Addition](mods/create-addition.md) · [Create Propulsion](mods/create-propulsion.md) · [Create Radar](mods/create-radar.md)

| Раздел | Содержание |
| --- | --- |
| [CBC Programmable Fuzes](mods/cbc-programmable-fuzes.md) | 22 подтверждённых метода Lua, поля ответов |
| [Enhanced Detector Radar](mods/enhanced-detector-radar.md) | Точность, поля радаров, физические снимки |
| [Sable CC Tick Sync](mods/sable-cc-tick-sync.md) | `sableSync`, частоты и ограничения |
| [CC:Sable](mods/cc-sable.md) | Поза, преобразования координат, скорости, углы |
| [NeoPeripheral](mods/neoperipheral.md) | Двигатель Sable, радары, CBC, Synaxis |
| [Реестр периферии сборки](mods/installed-peripherals.md) | Другие доступные API модов |
| [Mianbao Sable Explosion Compat](mods/mianbao-sable-explosion-compat.md) | Периферия `explosive` |
| [CBC Realistic Ballistics](mods/cbc-realistic-ballistics.md) | Совместимость без нового Lua API |
| [Sable High Altitude Transit](mods/sable-high-altitude-transit.md) | Изменение физики без нового API |
| [CBC Aero Velocity Fix](mods/cbc-aero-velocity-fix.md) | Физический патч без API |
| [Sable Autonomous Chunk Loader](mods/sable-autonomous-chunk-loader.md) | Косвенное изменение радара |
| [Полный список модов](modpack-audit.md) | Все JAR и результаты проверки CC-ссылок |

## Инструменты программного агента

[Автоматические проверки, имитация периферии, API-манифесты и регрессионные тесты](gocode-agent.md).

## Источники и статус проверки

Данные собраны из [CCGPTskills](https://github.com/323erir6/CCGPTskills), исходных репозиториев и установленного архива модов. Ссылки на CC в байткоде доказывают интеграцию, но **не гарантируют, что каждый найденный Java-метод доступен в Lua**. Для этого нужны `@LuaFunction`, зарегистрированный диспетчер и фактический `peripheral.getMethods`.

Общие исполняемые Lua-модули находятся в `lib/`. Математические тесты не заменяют проверку периферии внутри Minecraft. Сторонние библиотеки не поставляются как скрытые зависимости.

## Примеры

- [Мировые координаты CC:Sable](../../examples/sublevel_world_position.lua), [ориентация](../../examples/sublevel_attitude.lua), [спидометр](../../examples/sublevel_speedometer.lua)
- [Инспектор периферии](../../examples/inspect_peripherals.lua)
- [Сеть и другие примеры](../../examples/README.md)

Английские документы находятся в [полностью отдельном каталоге](../en/INDEX.md).
