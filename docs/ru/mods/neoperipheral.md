# NeoPeripheral 1.4ve — подробный справочник периферии CC

**Проверено:** `neoperipheral-1.4ve.jar` из архива на 143 мода; имена методов и Java-сигнатуры извлечены из реальных `.class` через `javap`. Моды [Enhanced Detector Radar](enhanced-detector-radar.md), [Sable Autonomous Chunk Loader](sable-autonomous-chunk-loader.md) и Synaxis Patchpack могут изменять исходные периферии.

## Обнаружение периферии

```lua
local names=peripheral.getNames()
table.sort(names)
for _,name in ipairs(names) do
  print("DEVICE",name,peripheral.getType(name))
  local methods=peripheral.getMethods(name) or {}
  table.sort(methods)
  print(table.concat(methods,", "))
end
```

Не каждый публичный Java-метод доступен в Lua: нужны `@LuaFunction`, регистрация CC и соответствующая настройка мода. Реальный список `peripheral.getMethods(name)` имеет приоритет.

## Двигатель Sable Engine

В классе `SableEnginePeripheral` объявлены:

| Метод | Аргументы | Назначение |
| --- | --- | --- |
| `getUUID()` | нет | UUID конструкции |
| `isOnSubLevel()` | нет | наличие физической конструкции |
| `getName()` | нет | имя |
| `getMass()` | нет | масса |
| `getPosition()` | нет | координаты |
| `getOrientation()` | нет | ориентация |
| `getLinearVelocity()` | нет | линейная скорость |
| `getAngularVelocity()` | нет | угловая скорость |
| `getCenterOfMass()` | нет | центр масс |
| `applyLinearImpulse(x,y,z)` | 3 числа | линейный импульс |
| `applyAngularImpulse(x,y,z)` | 3 числа | угловой импульс |
| `applyImpulseAtPoint(ix,iy,iz,px,py,pz)` | 6 чисел | импульс в заданной точке |
| `applyImpulseAtRelativePoint(ix,iy,iz,rx,ry,rz)` | 6 чисел | импульс относительно тела |

Реальный состав таблиц `getPosition/getOrientation` считайте через `textutils.serialize`; не придумывайте названия вложенных ключей. Системы координат для импульсов в точке проверяйте по установленной реализации.

При наличии **Enhanced Detector Radar 1.0.5** добавляются `getPhysicsState()`, `applyControlImpulse(lx,ly,lz,ax,ay,az)`, `stepControl(lx,ly,lz,ax,ay,az)`. Поля снимка: `x,y,z,qx,qy,qz,qw,vx,vy,vz,wx,wy,wz,mass`.

```lua
local d=assert(peripheral.find("sable_engine"),"Sable engine missing")
if type(d.getPhysicsState)=="function" then
  local state=d.getPhysicsState()
  if state then print(textutils.serialize(state)) end
end
```

Это пример без изменения физики.

## Радарные периферии

`RadarPeripheral`: `isCreative()`, `scanForSubLevels([radius[,absolute]])`. `TriangleRadarPeripheral`: `scanForSubLevels()`; разные типы устройств не гарантируют одинаковую структуру ответа.

В сборке Enhanced Detector Radar дополняет сканирование полями `velocity_x/y/z`, `size_x/y/z`. В обычном режиме `x/y/z` могут быть **относительными координатами с шумом**, тогда как скорость задана по глобальным осям. Кватернион радара называется `q_x,q_y,q_z,q_w`, а в состоянии двигателя — `qx,qy,qz,qw`.

`EntityRadarPeripheral`: `scanForEntities(...)`, `scanForPlayers(...)`. Не приравнивайте их к API Advanced Peripherals Player Detector: аргументы и фильтры задаются отдельно.

```lua
local radar=assert(peripheral.wrap("radar_name"))
for _,row in ipairs(radar.scanForSubLevels(128,false) or {}) do
  print(textutils.serialize(row))
end
```

## Пушечные установки CBC

| Класс | Доступные методы |
| --- | --- |
| `CannonMountPeripheral` | `assemble`, `fire`, `disassemble`, `isRunning`, `getYaw`, `getPitch`, `setYaw`, `setPitch`, `getX/Y/Z`, `getDirection` |
| `FixedCannonMountPeripheral` | тот же основной набор |
| `CompactCannonMountPeripheral` | `assemble`, `fire`, `disassemble`, `isRunning`, `getPitch`, `setPitch`, `getX/Y/Z`, `getDirection`; **методы yaw здесь отсутствуют** |

`fire()` в Java возвращает `void`, не следует ожидать от него булевого подтверждения. Методы других аддонов могут также появляться на общей периферии.

## Synaxis

`DynamicMotorPeripheral`: `setGainP`, `setGainI`, `setGainD`, `setPID`, `getGainP/I/D`, `setTarget`, `GetTarget` (**большая G в исходном классе**), `setMode`, `getMode`, `setGravityCompensation`, `getGravityCompensation`, `collect`.

`CompactFlapPeripheral`: `setAngle`, `getAngle`, `setTilt`, `getTilt`, `assemble`, `disassemble`.

`CameraPeripheral`: `getPitch`, `getYaw`, `getDistance`, `isRayEnabled`, `setRayEnabled`, `rayRange`, `setRayRange`, `collect`.

`JetPeripheral`: `setTrust` и `getTrust` (**Trust, а не Thrust по байткоду**), `setHorizontalAngle`, `getHorizontalAngle`, `setVerticalAngle`, `getVerticalAngle`, `collect`.

`AnchorPeripheral`: `setAirResistance`, `getAirResistance`, `setExtraGravity`, `getExtraGravity`, `setRotationalResistance`, `getRotationalResistance`, `collect`. `KineticResistorPeripheral`: `getRatio`, `setRatio`.

**Единицы углов:** тип double в Java не определяет градусы или радианы. Проверяйте систему координат и текущие значения перед включением регулятора.

## Другие классы

`LinkedControllerHubPeripheral`: `getButton`, `getButtons`, `getKeys`. Существует отдельный `TweakedLinkedControllerHubPeripheral`; названия событий и методов следует проверять на реальном компьютере.

Также есть NFC Reader/Master, Crypto, Socket и модемные классы; не все найденные Java-методы гарантированно выставлены в Lua.

## Типовые проблемы

1. Сверьте тип и методы фактического периферийного объекта.
2. Проверяйте UUID конструкции и возвращаемые ключи таблиц.
3. Не путайте мировые и локальные координаты.
4. Не считайте физический импульс обычной силой/сек.
5. `sableSync` появляется только с соответствующим модом.
6. `sable_engine.enable` может выключать экспонирование двигателя.
7. Удаление ограничителя частоты не гарантирует постоянный TPS.

**Подтверждение:** сигнатуры установленных классов и исходный Mixin Enhanced Detector Radar. Игровая проверка всех методов не проводилась.