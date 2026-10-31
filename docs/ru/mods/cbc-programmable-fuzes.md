# CBC Programmable Fuzes 1.4.1 — API для CC:Tweaked

**Достоверность:** методы прочитаны непосредственно из [FuzePeripheralMethods.java](https://github.com/323erir6/CBC-Programmable-Fuzes/blob/main/src/main/java/ua/ivan/cbcprogrammablefuzes/peripheral/FuzePeripheralMethods.java), [FuzeCapabilities.java](https://github.com/323erir6/CBC-Programmable-Fuzes/blob/main/src/main/java/ua/ivan/cbcprogrammablefuzes/peripheral/FuzeCapabilities.java), реестров телеметрии и `FuzeConfig.java` версии **1.4.1** для Minecraft 1.21.1. Это подтверждение исходным кодом, не результат запуска в игре.

## Подключение

Мод регистрирует дополнительный CC-периферийный тип `programmable_fuze` с псевдонимом `cbc_programmable_fuze`. Периферия доступна совместимым размещённым снарядам с программируемым взрывателем и собранным артиллерийским установкам, где имеется поддерживаемый снаряд. Существующие методы блока не заменяются. Подключение производится через проводной модем. Точное имя выясняется через `peripheral.getNames()`, тип и список методов — через `peripheral.getType(name)` и `peripheral.getMethods(name)`.

```lua
local fuze = assert(peripheral.find("programmable_fuze"), "Fuze peripheral missing")
print(textutils.serialize(peripheral.getMethods(peripheral.getName(fuze))))
```

При нескольких подходящих устройствах выбирайте их по конкретному имени; метод `find` без фильтра возвращает первое найденное.

## Полный перечень 22 Lua-методов

Аргумент Java `ProgrammableFuzeAccess target` внедряется автоматически и **не передаётся из Lua**.

| Метод | Аргументы Lua | Возвращает |
| --- | --- | --- |
| `hasProgrammableFuze()` | нет | boolean: в устройстве есть программируемый взрыватель |
| `setProximity(radius,active)` | число, boolean | true/ошибка: режим близости |
| `setTimer(seconds,active)` | число, boolean | true/ошибка: временной режим |
| `setPersistent(active)` | boolean | true/ошибка: сохранять снаряд |
| `setFuzeChannel(channel)` | string | true/ошибка: установить канал |
| `listFuzeProjectiles(channel)` | string | список активных снарядов |
| `getFuzeTelemetry(channel,id)` | string, строковый UUID | `true,table` либо `false` |
| `setFuzeProjectileTimer(channel,id,seconds,active)` | string,string,number,boolean | boolean: настройки в полёте |
| `setFuzeProjectileProximity(channel,id,radius,active)` | string,string,number,boolean | boolean |
| `setFuzeProjectilePersistent(channel,id,active)` | string,string,boolean | boolean |
| `setFuzeProjectileChannel(channel,id,newChannel)` | 3 строки | boolean |
| `setFuzeProjectileSettings(channel,id,timerSeconds,timerActive,proximityRadius,proximityActive,persistent)` | значения строго в указанном порядке | boolean: атомарная замена |
| `hasTrajectoryCorrectionModule()` | нет | boolean: установлен модуль коррекции |
| `setCorrectionChannel(channel)` | строка | true/ошибка |
| `setCorrectionPersistent(active)` | boolean | true/ошибка |
| `setImpactCoordinates(x,y,z)` | 3 числа | true/ошибка: цель в мировых координатах |
| `listCorrectionProjectiles(channel)` | string | список модулей в полёте |
| `getCorrectionTelemetry(channel,id)` | 2 строки | `true,table` либо `false` |
| `setCorrectionProjectileTarget(channel,id,x,y,z)` | 2 строки, 3 числа | boolean |
| `getLoadedProjectileInfo()` | нет | `true,table` либо `false` |
| `getLoadedPropellantInfo()` | нет | `true,table` либо `false` |
| `getCannonInfo()` | нет | `true,table` либо `false` |

`set...` могут вызвать `LuaException`, когда сервер запрещает программирование, не найден соответствующий предмет или значения выходят за диапазон. Для обработки ожидаемых ошибок используйте `pcall`. У некоторых методов полёта `false` означает отсутствие зарегистрированного UUID в канале.

## Пределы и частота

Значения по умолчанию из `FuzeConfig.java`: радиус **2 блока**, время **15 секунд**, допустимый радиус по умолчанию **0–64**, время **0–86 400 секунд**. Абсолютные пределы конфигурации: радиус 1 024, таймер 31 536 000 с. Сервер может менять границы и отключать отдельные функции. Таймер округляется **вверх** до шага 1/20 с по формуле `ceil(seconds*20)/20`. NaN и бесконечности отклоняются. Для модуля коррекции параметры по умолчанию: множитель дальности 1.10 и доступный поворот 6°/км. Это параметры модели, а не гарантия точности.

Часть методов с аннотацией `mainThread=true` требует продолжения на основном потоке. Методы изменения параметров уже летящего снаряда используют буфер последнего состояния, чтобы не накапливать очередь при ускоренных вычислениях Sable. Положительный ответ не обязательно означает немедленное применение на текущем физическом шаге.

## Таблица телеметрии взрывателя

Список `listFuzeProjectiles(channel)` содержит `id`, `type`, `ageTicks`, `timerSecondsRemaining`.

Полная `getFuzeTelemetry(channel,id)` содержит `id`, `channel`, `dimension`, `type`, `x`, `y`, `z`, `velocityX`, `velocityY`, `velocityZ`, `speed`, `ageTicks`, `timerTicksRemaining`, `timerSecondsRemaining`, `armed`, `updatePending`. Дополнительные поля настроек могут добавляться `FuzeSettings`; для полей, не перечисленных здесь, требуется проверка реальной возвращаемой таблицы.

## Таблица коррекции

`listCorrectionProjectiles(channel)` выдаёт `id`, `type`, `ageTicks`.

`getCorrectionTelemetry` выдаёт `id`, `channel`, `dimension`, `type`, мировые координаты `x,y,z`, скорость `velocityX/Y/Z`, `speed`, `ageTicks`, `hasTarget`, необязательные `targetX/Y/Z`, `targetDistance`, `correctionDegreesRemaining`, `correctionDistanceRemaining`, `guidanceActive`, `targetForward`, `rangeMultiplierApplied`. Проверяйте `hasTarget` перед доступом к координатам цели.

## Сведения о пушке, зарядах и снаряде

`getCannonInfo()` для собранной конструкции возвращает имеющиеся из полей: `assembled`, `cannonClass`, `lengthBlocks`, `muzzleDistanceBlocks`, `weight`, `initialOrientation`, `axis`, `startPosition`, `cannonType`, `ballisticProfile`, материал и его характеристики. Для большой пушки: `material`, `weightPerBlock`, `minimumVelocityPerBarrel`, `maxSafePropellantStress`, `failureMode`, `weldable`, `weldDamage`, `weldStressPenalty`, `minimumSpread`, `spreadReductionPerBarrel`, `maxSafeCharges`. Для автопушки возможны `maximumBarrelLength`, `baseSpeedBlocksPerTick`, `baseSpeedMetersPerSecond`, `speedIncreasePerBarrelBlocksPerTick`, `maximumSpeedIncreases`, `projectileLifetimeTicks`.

`getLoadedProjectileInfo()`: `id`, `name`, `blockCount`, `positions`, `complete`, `projectileEntity`, `projectileMass`, `addedChargePower`, `minimumChargePower`, `physicalDiameterMetres`, `hasFuze`, `hasProgrammableFuze`, `hasTracer`, `hasTrajectoryCorrectionModule`. Набор зависит от вида боеприпаса. `physicalDiameterMetres` — диаметр хитбокса, **не обязательно номинальный калибр** для расчёта баллистики.

`getLoadedPropellantInfo()`: `count`, `segments`, `usesSeparateCharges`, `totalChargePower`, `totalStress`, `totalSpread`, `effectiveRecoil`, иногда `maxSafeCharges`, `overloaded`. В элементах `segments` могут находиться `id`, `name`, `position`, `chargePower`, `stress`, `spread`, `recoil`, `damp`, `waterlogged`. Для автопушек отдельные заряды не используются.

## Готовый пример чтения без изменения настроек

```lua
local fuze = assert(peripheral.find("programmable_fuze"), "Fuze peripheral missing")
local ok, info = fuze.getLoadedProjectileInfo()
if ok then
  print(textutils.serialize(info))
else
  print("Projectile not available")
end
local channel = "unsecured"
for _, item in ipairs(fuze.listFuzeProjectiles(channel) or {}) do
  local available, data = fuze.getFuzeTelemetry(channel, item.id)
  if available then
    print(data.id, data.speed, data.timerSecondsRemaining)
  end
end
```

## Типичные проблемы

1. Устройство отсутствует: не подключён модем, блок неподдерживаемый или установка не собрана.
2. Метод отсутствует: неверная версия; запросите `peripheral.getMethods(name)`.
3. Программирование отключено в конфигурации сервера.
4. Радиус или время не соответствуют установленным пределам.
5. Телеметрия вернула `false`: UUID не существует, выбран другой канал, запись устарела более 30 секунд или объект удалён.
6. `dimension` не совпадает с измерением целевой системы.
7. Аддон предоставляет другой тип установки: проверьте фактические методы периферии.

**Исходный коммит:** `d3ba2fd8cd0a74facd71c7f9c3718bdb66cc0282`.