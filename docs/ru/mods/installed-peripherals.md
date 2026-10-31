# Реестр API периферии сборки

**Сборка:** Minecraft 1.21.1, CC:Tweaked 1.120.0, NeoForge. Реестр составлен по фактическому архиву JAR и текущим исходникам. Ссылки ведут только в **самостоятельные русскоязычные документы**.

## Таблица охвата

| Мод | Документация | Поддержка CC |
| --- | --- | --- |
| CBC Programmable Fuzes | [Читать](./cbc-programmable-fuzes.md) | 22 подтверждённых метода, телеметрия и осмотр пушки |
| Enhanced Detector Radar | [Читать](./enhanced-detector-radar.md) | Дополнительные поля радара, точность и физические методы |
| Sable CC Tick Sync | [Читать](./sable-cc-tick-sync.md) | Глобальный API sableSync, частота выполнения |
| CC:Sable | [Читать](./cc-sable.md) | API координат, ориентации и атмосферы |
| NeoPeripheral | [Читать](./neoperipheral.md) | Радары, двигатель Sable, установки CBC, Synaxis |
| Advanced Peripherals | [Читать](./advanced-peripherals.md) | Детектор игроков и другие периферии |
| Create | [Читать](./create.md) | Встроенные интеграции Create |
| Create Addition | [Читать](./create-addition.md) | Моторы, сервоприводы, адаптеры |
| Create Propulsion | [Читать](./create-propulsion.md) | Двигатели, векторная тяга и питание |
| Create Radar | [Читать](./create-radar.md) | Радарные и управляющие периферии |
| Create Tweaked Controllers | [Читать](./create-tweaked-controllers.md) | Кнопки и оси контроллеров |
| Create Diesel Generators | [Читать](./create-diesel-generators.md) | Периферия химической турели |
| CC:AR | [Читать](./cc-ar.md) | Контроллер дополненной реальности |
| Tom's Peripherals | [Читать](./toms-peripherals.md) | GPU, монитор, клавиатура и динамический API |
| Vista | [Читать](./vista.md) | Видоискатель и WaveGate |
| Synaxis Patchpack | [Читать](./synaxis-patchpack.md) | Дополнительные методы камеры и мотора |
| Bits n Bobs | [Читать](./bits-n-bobs.md) | Периферия фонаря |
| Mianbao Sable Explosion Compat | [Читать](./mianbao-sable-explosion-compat.md) | Периферия explosive |
| CBC Realistic Ballistics | [Читать](./cbc-realistic-ballistics.md) | Физика баллистики без отдельного API |
| Sable High Altitude Transit | [Читать](./sable-high-altitude-transit.md) | Нет Lua-методов, меняет физику |
| CBC Aero Velocity Fix | [Читать](./cbc-aero-velocity-fix.md) | Нет Lua-методов |
| Sable Autonomous Chunk Loader | [Читать](./sable-autonomous-chunk-loader.md) | Косвенные изменения радара |
## Уровни подтверждения

- **Подтверждено Java-исходниками:** точные методы и типы параметров.
- **Подтверждено байткодом JAR:** классы и имена методов установлены, но не каждый метод обязательно виден в Lua.
- **Косвенная интеграция:** мод меняет физику или расписание без нового метода Lua.
- **Проверено в игре:** только после теста на реальном CC:Tweaked; такая проверка здесь не заявляется.

См. [все 143 файла](../modpack-audit.md) с точными именами и отключёнными версиями. Для получения списка реальных методов используйте [`inspect_peripherals.lua`](../../../examples/inspect_peripherals.lua).