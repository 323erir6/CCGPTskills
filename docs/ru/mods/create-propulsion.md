# Create Propulsion — интеграция с CC

**Проверенный JAR:** `createpropulsion-1.1.5.jar`.

## Назначение и особенности

Методы отдельно возвращают физическую тягу, отображаемую тягу, поток воздуха и запас топлива/энергии. PN и KN названы отдельными единицами в исходниках и не должны смешиваться без приведения. Нормализованную мощность нельзя приравнивать к целому raw power. Вектор цели и фактическое отклонение двигателя могут различаться; не предполагайте мгновенной реакции. Работа с жидкостями и инвентарями зависит от соответствующих capability.

## Методы периферий и классов

| Java-периферия или группа API | Найденные методы-кандидаты |
| --- | --- |
| `ThrusterPeripheral` | `getObstruction(), setPower(int), setPowerNormalized(number), getPower(), getCurrentThrustPN(), getCurrentThrustKN(), getDisplayedThrustPN(), getDisplayedThrustKN(), getAirflowMs(), getFuelAmountMb(), getFuelCapacityMb(), tanks(), pushFluid(...), pullFluid(...)` |
| `CreativeThrusterPeripheral` | `getObstruction(), setPower(int), setPowerNormalized(number), getPower(), setThrustConfig(int), getThrustConfig(), getTargetThrustPN(), getTargetThrustKN(), getCurrentThrustPN(), getCurrentThrustKN(), getDisplayedThrustPN(), getDisplayedThrustKN(), getAirflowMs()` |
| `IonThrusterPeripheral` | `getObstruction(), setPower(int), setPowerNormalized(number), getPower(), getCurrentThrustPN(), getCurrentThrustKN(), getDisplayedThrustPN(), getDisplayedThrustKN(), getAirflowMs(), getEnergyAmountFe(), getEnergyCapacityFe()` |
| `SolidFuelThrusterPeripheral` | `getObstruction(), setPower(int), setPowerNormalized(number), getPower(), getCurrentThrustPN(), getCurrentThrustKN(), getDisplayedThrustPN(), getDisplayedThrustKN(), getAirflowMs(), getFuelAmount(), getFuelCapacity(), getBurnTimeRemaining(), isBurning(), list(), pushItems(...), pullItems(...)` |
| `VectorThrusterPeripheral` | `getVectorX(), getVectorY(), getTargetVectorX(), getTargetVectorY(), setVectorX(number), setVectorY(number), setVector(x,y), setThrust(number), setThrustNormalized(number), setPower(int), setPowerNormalized(number), getThrust(), getPower()` |
| `LiquidVectorThrusterPeripheral` | `all VectorThruster methods plus tanks(), pushFluid(...), pullFluid(...)` |
| `CreativeVectorThrusterPeripheral` | `setThrustOutput(number), clearThrustOutput(), getMaxThrustOutputPn(), isCustomThrustOutputActive()` |
| `TiltAdapterPeripheral` | `getLeftSignal(), getRightSignal(), setTargetAngle(number)` |
| `RedstoneTransmissionPeripheral` | `getTransmissionMode(), setTransmissionMode(...), getShiftLevel(), setShiftLevel(...)` |
| `StirlingEnginePeripheral` | `getRpm(), setSpeed(number), setActive(boolean)` |
| `CoralGeneratorPeripheral` | `getCoralAmountMb(), getCoralCapacityMb(), getEnergyAmountFe(), getEnergyCapacityFe()` |

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
