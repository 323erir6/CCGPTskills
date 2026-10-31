# Synaxis Patchpack — интеграция с CC

**Проверенный JAR:** `synaxis_patchpack-1.0.0.jar`.

## Назначение и особенности

Код использует generic peripherals и Mixin для дополнительных методов камер и моторов NeoPeripheral. Таблица текущего состояния отличается от сохранённых настроек; не смешивайте getMotorRuntime и getMotorSettings. getCurrentAngleDegrees явно выражен в градусах, единицы getCurrentAngle необходимо проверять отдельно. Проверена установленная версия 1.0.0; точный публичный исходный репозиторий патчпака не подтверждён.

## Методы периферий и классов

| Java-периферия или группа API | Найденные методы-кандидаты |
| --- | --- |
| `SynaxisCameraScopePeripheral` | `getScopeSettings(), setScopeSettings(table), getScopeOffset(), setScopeOffset(x,y,z), getScopeYawLimits(), setScopeYawLimits(min,max), getScopePitchLimits(), setScopePitchLimits(min,max), getScopeMaxYawSpeed(), setScopeMaxYawSpeed(number), getScopeMaxPitchSpeed(), setScopeMaxPitchSpeed(number), setScopeMaxSpeed(yaw,pitch), getScopeZoomSpeed(), setScopeZoomSpeed(number), isScopeSlidingEnabled(), setScopeSlidingEnabled(boolean)` |
| `SynaxisDynamicMotorPeripheral` | `getMotorSettings(), getMotorConfig(), getMotorRuntime(), getMotorOffsets(), getCurrentAngle(), getCurrentAngleDegrees(), getCurrentSpeed(), getAppliedTorque(), isMotorConnected(), isMotorLockActive(), isMotorAutoLockActive()` |

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
