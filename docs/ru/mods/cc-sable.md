# CC:Sable: API sublevel и aero (автономный справочник)

**Статус:** Имена функций сверены с официальной документацией CC:Sable от 13.05.2026. Структура некоторых вложенных полей pose основана на работающем примере и подлежит проверке на установленной версии.

**Среда:** CC:Tweaked + CC:Sable + Sable, Minecraft 1.21.1. Глобальный модуль `sublevel` добавляется модом; большинство методов требуют размещения компьютера на физическом Sub-Level.

## 1. Полный перечень опубликованных методов sublevel

| Метод | Аргументы | Возвращает | Значение |
| --- | --- | --- | --- |
| `isInPlotGrid()` | нет | boolean | Компьютер находится на Sub-Level |
| `getUniqueId()` | нет | UUID string | Уникальный ID конструкции |
| `getName()` | нет | string | Имя конструкции |
| `setName(newName)` | string | не указано | Изменить имя |
| `getLogicalPose()` | нет | pose table | Текущее преобразование |
| `getLastPose()` | нет | pose table | Предыдущее преобразование |
| `getVelocity()` | нет | vector | Глобальная скорость |
| `getLinearVelocity()` | нет | vector | Последняя линейная скорость |
| `getAngularVelocity()` | нет | vector | Последняя угловая скорость |
| `getCenterOfMass()` | нет | vector | Центр масс |
| `getMass()` | нет | number | Масса |
| `getInverseMass()` | нет | number | Обратная масса |
| `getInertiaTensor()` | нет | matrix | Тензор инерции |
| `getInverseInertiaTensor()` | нет | matrix | Обратный тензор инерции |

Почти все методы, кроме `isInPlotGrid`, могут завершиться ошибкой без привязанного Sub-Level. Не путайте методы `sublevel` с `ship` из CC:VS: это разные моды.

## 2. Структура pose

```lua
pose.position = {x=100,y=80,z=-20}   -- Глобальный перенос
pose.rotationPoint = {x=5,y=6,z=7}  -- Центр вращения
pose.scale = {x=1,y=1,z=1}          -- Масштаб по осям
pose.orientation = {
  a=1,                                -- Скалярная часть кватерниона
  v={x=0,y=0,z=0}                    -- Векторная часть кватерниона
}
```

Числа здесь условные. `pose.position` не обязательно совпадает с мировой координатой конкретного блока. Кватернион имеет компоненты `w=a`, `x=v.x`, `y=v.y`, `z=v.z`.

## 3. Перевод локальной точки в мировые координаты

```text
L = (sx,sy,sz)
R = pose.rotationPoint
S = pose.scale
T = pose.position
Q = нормализованный кватернион
offset = (L - R) * S  (покомпонентное умножение)
world = T + rotate(Q,offset)
```

Для `Q=(w,x,y,z)` матрица вращения:

```text
R00=1-2(y*y+z*z)    R01=2(x*y-z*w)    R02=2(x*z+y*w)
R10=2(x*y+z*w)      R11=1-2(x*x+z*z)  R12=2(y*z-x*w)
R20=2(x*z-y*w)      R21=2(y*z+x*w)    R22=1-2(x*x+y*y)
```

Готовая реализация: [`lib/sublevel_pose.lua`](../../../lib/sublevel_pose.lua), функция `localToWorld(localPos, pose)`. Полная программа: [`examples/sublevel_world_position.lua`](../../../examples/sublevel_world_position.lua).

Частые ошибки: пропуск `rotationPoint`, преобразование уже мировых координат как локальных, неправильный порядок умножений, неединичный кватернион и путаница с интерфейсом CC:VS.

### 3.1 Обратное преобразование

```text
offset = inverse(R(Q)) * (world-T)
local = rotationPoint + offset/S
```

Для единичного кватерниона обратный поворот задаётся сопряжением `(w,-x,-y,-z)`. При нулевом масштабе оси обратное преобразование невозможно.

### 3.2 Точка и направление

Точка включает масштаб, поворот и перенос; направление только вращается. Для вычисления вектора вперёд используйте `localDirectionToWorld({x=0,y=0,z=1}, pose)`.

## 4. Yaw / Pitch / Roll из кватерниона

Соглашение: +Y вверх, +Z вперёд, +X вправо. Это не универсальный стандарт для всех модов.

```text
forwardY=2*(y*z-x*w)
forwardX=2*(x*z+y*w)
forwardZ=1-2*(x*x+y*y)
rightY=2*(x*y+z*w)
upY=1-2*(x*x+z*z)

pitch=deg(asin(clamp(forwardY,-1,1)))
yaw=deg(atan2(forwardX,forwardZ))
roll=deg(atan2(rightY,upY))
```

В актуальном CC:Tweaked предпочтителен `math.atan(y,x)`: существование `math.atan2` не следует предполагать. Функция [`yawPitchRoll(pose)`](../../../lib/sublevel_pose.lua) использует проверяемый вариант.

При pitch около ±90° yaw и roll становятся неоднозначными (gimbal lock). Для стабилизации предпочтительнее кватернионы и векторы направления, а не разность углов Эйлера.

Контрольные случаи: единичная ориентация → все углы 0; +90° вокруг Y → yaw +90; +90° вокруг X → pitch -90; +90° вокруг Z → roll +90.

## 5. Скорость

`sublevel.getVelocity()` возвращает глобальную скорость, `getLinearVelocity()` — последнюю линейную скорость. Их временная синхронизация должна проверяться по конкретной сборке.

Полная скорость `sqrt(vx²+vy²+vz²)`; перевод блоков/с в км/ч — умножение на 3.6. Продольная скорость = `dot(worldVelocity, normalize(rotate(q,{0,0,1})))`; отрицательное значение означает движение назад.

Для произвольной точки вращающегося жёсткого тела возможна формула `v_point=v_origin+omega×r`, но необходимы подтверждённые единицы угловой скорости и точка отсчёта линейной скорости. Документация сама по себе этого не гарантирует.

Программа: [`sublevel_speedometer.lua`](../../../examples/sublevel_speedometer.lua).

## 6. API aero

| Метод | Аргументы | Возвращает |
| --- | --- | --- |
| `aero.getAirPressure(x,y,z)` | 3 numbers | number |
| `aero.getGravity()` | нет | vector |
| `aero.getMagneticNorth()` | нет | vector |
| `aero.getUniversalDrag()` | нет | number |
| `aero.getRaw()` | нет | table конфигурации |
| `aero.getDefault()` | нет | table стандартных значений |

Для позиции обычно используется `vector.new(x,y,z)`; проверьте установленную среду. Не предполагайте одинаковую гравитацию или сопротивление во всех измерениях.

## 7. Диагностика

```lua
assert(type(sublevel)=="table","CC:Sable API missing")
print("On sublevel:",sublevel.isInPlotGrid())
if sublevel.isInPlotGrid() then
  print(textutils.serialize(sublevel.getLogicalPose()))
  print("UUID:",sublevel.getUniqueId())
  print("Velocity:",tostring(sublevel.getVelocity()))
end
if type(aero)=="table" then print(tostring(aero.getGravity())) end
```

Источники:
- https://techtastic.github.io/CC-Sable/modules/sublevel.html
- https://techtastic.github.io/CC-Sable/modules/aero.html
- https://www.tweaked.cc/mc-1.21.x/reference/feature_compat.html

**Проверка:** имена API — официальная документация; поля и математические преобразования — практический образец плюс независимые тесты. Успешный математический тест не равен проверке в Minecraft.
