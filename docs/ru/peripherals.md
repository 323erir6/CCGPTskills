# Обнаружение периферии и адаптеры

## Проверка устройств

```lua
for _, name in ipairs(peripheral.getNames()) do
  print(name, peripheral.getType(name))
  local methods = peripheral.getMethods(name) or {}
  print("  " .. table.concat(methods, ", "))
end
```

Названия устройств в проводной сети и сторонних модах отличаются от `left`, `right`, `top` и других сторон. `peripheral.find(type)` удобно применять только при известном типе устройства.

## Проверка доступности

```lua
local name = "right"
if not peripheral.isPresent(name) then
  error("Required peripheral is missing: " .. name)
end
local device = assert(peripheral.wrap(name))
```

При возможном отключении устройства обрабатывайте сбои вызовов через `pcall`, а результаты проверяйте перед использованием.

## Совместимость дополнений

Методы сторонних модов не относятся к базовому API CC:Tweaked. Типы, сигнатуры, ограничения и поля возвращаемых таблиц могут отличаться.

Проверяйте реальные методы и реализуйте адаптеры с контролем возможностей. При неподдерживаемой версии выводите понятную ошибку вместо выдуманного API.

## Экраны

Стандартный `monitor` поддерживает операции терминала; продвинутый монитор может выдавать событие `monitor_touch`. Внешние GPU-периферии не являются тем же API и требуют собственной документации.

См. [Интеграции модов](../../mods/README.md) и [инспектор](../../examples/inspect_peripherals.lua).

Источник: https://tweaked.cc/module/peripheral.html
