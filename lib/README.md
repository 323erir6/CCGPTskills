# Reusable Lua modules / Повторно используемые модули

| File | English | Русский |
| --- | --- | --- |
| [math3d.lua](math3d.lua) | Pure vector and angle utilities | Векторы и углы |
| [pid.lua](pid.lua) | Discrete PID with anti-windup | Дискретный PID с anti-windup |
| [peripherals.lua](peripherals.lua) | Peripheral validation and discovery | Проверка и поиск периферии |
| [protocol.lua](protocol.lua) | Defensive network message envelopes | Проверка сетевых пакетов |
| [config.lua](config.lua) | Namespaced settings storage | Хранение настроек |

**EN:** Modules return plain Lua tables for `require`. Copy files to a CraftOS computer and adjust the module search path if the files are located elsewhere. Code is designed for CC:Tweaked but has not been executed in Minecraft in this repository.

**RU:** Модули возвращают обычные таблицы Lua для `require`. Скопируйте файлы на компьютер CraftOS; при другом расположении настройте поиск модулей. Код предназначен для CC:Tweaked, но в этом репозитории его выполнение внутри Minecraft не подтверждено.
