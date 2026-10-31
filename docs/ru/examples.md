# Примеры программ

Примеры работают самостоятельно, кроме случаев, когда явно подключается `lib/`. Некоторым нужны дополнительные моды и периферии. Все программы необходимо проверять в конкретной сборке Minecraft до использования в постоянной автоматизации.

| Файл | Назначение |
| --- | --- |
| [inspect_peripherals.lua](../../examples/inspect_peripherals.lua) | Список устройств, типов и доступных методов |
| [rednet_receiver.lua](../../examples/rednet_receiver.lua) | Приём сообщений с проверкой протокола и структуры |
| [rednet_sender.lua](../../examples/rednet_sender.lua) | Отправка пакета с версией и ID адресата |
| [monitor_dashboard.lua](../../examples/monitor_dashboard.lua) | Интерфейс символьного монитора с событиями |
| [redstone_pulse.lua](../../examples/redstone_pulse.lua) | Ограниченный импульс Redstone со сбросом |
| [analog_redstone.lua](../../examples/analog_redstone.lua) | Аналоговый сигнал 0–15 с тайм-аутом |
| [turtle_safe_move.lua](../../examples/turtle_safe_move.lua) | Движение черепахи с проверкой топлива и препятствий |
| [player_detector.lua](../../examples/player_detector.lua) | Детектор игроков Advanced Peripherals и вывод координат |
| [inventory_report.lua](../../examples/inventory_report.lua) | Отчёт о заполненных слотах инвентаря |
| [gps_position.lua](../../examples/gps_position.lua) | Определение мировых координат через GPS |
| [terminal_menu.lua](../../examples/terminal_menu.lua) | Текстовое меню с управлением клавиатурой |
| [control_simulation.lua](../../examples/control_simulation.lua) | Симуляция PID с упрощённой физикой |
| [position_speed.lua](../../examples/position_speed.lua) | Расчёт скорости по двум введённым точкам |
| [sublevel_world_position.lua](../../examples/sublevel_world_position.lua) | Преобразование локальной точки Sable в мировую |
| [sublevel_attitude.lua](../../examples/sublevel_attitude.lua) | Углы yaw/pitch/roll из Sable |
| [sublevel_speedometer.lua](../../examples/sublevel_speedometer.lua) | Полная и продольная скорость конструкции Sable |

## Запуск

Скопируйте программу на компьютер CraftOS; дополнительные модули оставляйте в указанных путях `lib/`. Для Rednet примеров отправитель и приёмник должны быть на разных компьютерах, соединённых модемами, и использовать одинаковый протокол. Для физики необходим CC:Sable и проверка `sublevel.isInPlotGrid()`.

## Условия проверки

Успешная проверка синтаксиса не означает наличие периферии. Для экранов проверяйте размеры и события касания, для двигателей — знаки осей и пределы усилий. До испытаний с фактическим оборудованием нельзя предполагать безопасность автономного управления.