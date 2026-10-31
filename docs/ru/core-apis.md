# Основные API CraftOS

Краткая карта интерфейсов; полный справочник находится на официальном сайте.

| API | Назначение | Примеры |
| --- | --- | --- |
| `term` | Терминал | `getSize`, `setCursorPos`, `write`, `clear` |
| `colors` | Цвета | `colors.white`, `colors.blue` |
| `fs` | Файловая система | `exists`, `open`, `makeDir`, `combine` |
| `settings` | Настройки | `define`, `get`, `set`, `load`, `save` |
| `textutils` | Сериализация, JSON | `serialize`, `unserialize`, `serializeJSON` |
| `peripheral` | Поиск и вызов устройств | `getNames`, `getType`, `getMethods`, `wrap`, `find`, `call` |
| `redstone` | Цифровые и аналоговые сигналы | `getInput`, `setOutput`, `getAnalogInput`, `setAnalogOutput` |
| `rednet` | Сетевые сообщения | `open`, `send`, `receive`, `broadcast` |
| `gps` | Координаты по модемам | `locate` |
| `http` | HTTP и WebSocket | `get`, `post`, `websocket` |
| `turtle` | Управление роботом | `forward`, `turnLeft`, `inspect`, `getFuelLevel` |

## Особенности

`peripheral.wrap(name)` возвращает объект либо `nil`. Вызов метода обычно имеет вид `device.method(args)`, без двоеточия.

Для чтения файла используйте `fs.open(path, "r")`, для замены `"w"`, для добавления `"a"`. Дескриптор файла нужно закрывать.

`settings.set` меняет значение в памяти. Для сохранения в файл отдельно вызывается `settings.save(path)`.

Имя проводного сетевого устройства может отличаться от названия стороны блока.

## Безопасное чтение

```lua
local h = fs.open("config.txt", "r")
if not h then error("Cannot open config.txt") end
local content = h.readAll()
h.close()
print(content)
```

Источники: https://tweaked.cc/, https://tweaked.cc/module/settings.html
