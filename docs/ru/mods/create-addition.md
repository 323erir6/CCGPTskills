# Create Addition — интеграция с CC

**Проверенный JAR:** `createaddition-1.7.0.jar`.

## Назначение и особенности

Обнаружены прямые периферии для электромоторов, сервоприводов, цифровых адаптеров, накопителей и энергетических интерфейсов. Целевой угол сервопривода не равен скорости; команды могут зависеть от состояния механизма. Digital Adapter взаимодействует с конкретными блоками Create, а не с любой конструкцией. Проверяйте значения и границы до отправки команд; единицы угла следует подтвердить на тестовом механизме.

## Методы периферий и классов

| Java-периферия или группа API | Найденные методы-кандидаты |
| --- | --- |
| `ElectricMotorPeripheral` | `setSpeed(number), stop(), getSpeed(), getStressCapacity(), getEnergyConsumption(), getMaxInsert(), getMaxExtract()` |
| `ServoMotorPeripheral` | `getSpeed(), setSpeed(number), getAngle(), getTargetAngle(), setTargetAngle(number), getMinAngle(), setMinAngle(number), getMaxAngle(), setMaxAngle(number), isAssembled(), assemble(), disassemble(), getEnergyConsumption()` |
| `DigitalAdapterPeripheral` | `clearLine(), clear(), print(string), getLine(), setLine(number), getMaxLines(), setTargetSpeed(name,number), getTargetSpeed(), getKineticStress(), getKineticCapacity(), getKineticSpeed(), getKineticTopSpeed(), getPulleyDistance(), getPistonDistance(), getBearingAngle(), getElevatorContraption(), getElevatorFloor(), hasElevatorArrived(), getElevatorFloors(), getElevatorFloorName(), gotoElevatorFloor(), getDurationAngle(), getDurationDistance()` |
| `ModularAccumulatorPeripheral` | `getEnergy(), getCapacity(), getPercent(), getMaxInsert(), getMaxExtract(), getHeight(), getWidth()` |
| `PortableEnergyInterfacePeripheral` | `getEnergy(), getCapacity(), isConnected(), getMaxInsert(), getMaxExtract()` |
| `RedstoneRelayPeripheral` | `getMaxInsert(), getMaxExtract(), getThroughput(), isPowered()` |

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
