# CC:Tweaked Lua Development Library

A bilingual (English / Русский) reference and example collection for writing ComputerCraft and CC:Tweaked Lua programs.

Двуязычная (English / Русский) библиотека справочных материалов и примеров программ на Lua для ComputerCraft и CC:Tweaked.

## Scope / Область применения

- Core CraftOS APIs, events, peripheral discovery, terminal/monitor interfaces, networking, configuration and file handling.
- Reusable Lua utilities and executable example programs.
- Version-aware integration notes for third-party peripheral mods.
- Practical checks for API compatibility, error handling, and cooperative scheduling.

- Базовые API CraftOS, события, обнаружение периферии, интерфейсы терминалов/мониторов, сеть, настройки и файловая система.
- Повторно используемые Lua-модули и запускаемые примеры.
- Примечания по совместимости сторонних периферийных модов.
- Проверки совместимости API, обработка ошибок и кооперативная многозадачность.

## Documentation / Документация

| English | Русский |
| --- | --- |
| [Getting started](docs/en/getting-started.md) | [Начало работы](docs/ru/getting-started.md) |
| [Core APIs](docs/en/core-apis.md) | [Основные API](docs/ru/core-apis.md) |
| [Events and concurrency](docs/en/events.md) | [События и многозадачность](docs/ru/events.md) |
| [Networks and protocols](docs/en/networking.md) | [Сети и протоколы](docs/ru/networking.md) |
| [Peripherals and compatibility](docs/en/peripherals.md) | [Периферия и совместимость](docs/ru/peripherals.md) |
| [Coordinates and control](docs/en/maths-and-control.md) | [Координаты и управление](docs/ru/maths-and-control.md) |
| [Reliability and security](docs/en/reliability.md) | [Надёжность и безопасность](docs/ru/reliability.md) |

See [Examples](examples/README.md), [Libraries](lib/README.md), [Modded APIs](mods/README.md), and [Development conventions](AGENTS.md).

См. [Примеры](examples/README.md), [Библиотеки](lib/README.md), [API модов](mods/README.md) и [Правила разработки](AGENTS.md).

## Compatibility / Совместимость

Core examples target CC:Tweaked CraftOS Lua. A mod-specific API must be verified against the installed Minecraft, mod loader, and mod version; **method names and table layouts must not be guessed**.

Базовые примеры предназначены для CraftOS Lua в CC:Tweaked. API модов необходимо сверять с версиями Minecraft, загрузчика и мода; **запрещается угадывать имена методов и структуру возвращаемых таблиц**.

## Reference / Источники

- [Official CC:Tweaked Lua API documentation](https://tweaked.cc/)
- [Official CC:Tweaked API for mod developers](https://www.tweaked.cc/mc-1.21.x/javadoc/index.html)
- [Advanced Peripherals documentation](https://docs.advanced-peripherals.de/latest/)
- [CC:Tweaked source repository](https://github.com/cc-tweaked/CC-Tweaked)

Examples are independent educational implementations, not copies of upstream documentation. Third-party integrations can require additional mods and configuration.

Примеры являются самостоятельными учебными реализациями, а не копиями документации разработчиков. Сторонние интеграции могут требовать установки модов и дополнительной настройки.
