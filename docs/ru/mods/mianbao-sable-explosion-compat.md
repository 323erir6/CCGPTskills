# Mianbao Sable Explosion Compat 1.2.9 — периферия CC

**Источник:** [MianbaoSableExplosionCompat](https://github.com/323erir6/MianbaoSableExplosionCompat), коммит `2335b47b2fb4cf9cee9375424d8b22b5f83ae401`. Проверены `ExplosivePeripheral.java` и `ExplosivePeripheralCapabilities.java`.

## Поддерживаемые блоки

Тип периферии — **`explosive`**. Регистрация CC:Tweaked предусмотрена только для:

1. `mianbaos_modernwarfare:tnt` — TNT из Mianbao Modern Warfare.
2. `mianbaos_modernwarfare:nuclearbomb` — ядерный блок Mianbao.
3. CBC `FuzedProjectileBlock`, в котором установлен **Wired Fuze**.

Само название «взрывчатка» не гарантирует поддержку: блок должен пройти Java-проверку `supports(state,blockEntity)`.

## Lua API

**`detonate() -> boolean`** — единственный экспортированный Lua-метод. Выполняется в серверной очереди (`@LuaFunction(mainThread=true)`). Возвращает `true` после обработки поддерживаемого блока, `false`, если он уже заменён или более не соответствует условиям; вне сервера возможен `LuaException`.

Метод вызывает процедуру TNT/ядерного заряда Mianbao или штатную немедленную детонацию CBC-проекта. Это **не искусственный импульс Redstone** и не функция изменения скорости снаряда.

## Безопасное обнаружение

```lua
for _,name in ipairs(peripheral.getNames()) do
  if peripheral.hasType(name,"explosive") then
    print(name,textutils.serialize(peripheral.getMethods(name)))
  end
end
```

Не вызывайте `detonate` автоматически в бесконечном цикле. Вызов изменяет игровой мир и должен выполняться только в рамках правил сервера и намеренного действия пользователя.

## Прочие функции мода

Мод транслирует эффекты взрывов Mianbao на пересекающиеся физические конструкции Sable, использует кэширование, ограниченную очередь и временную загрузку чанков. Эти функции относятся к реализации NeoForge и **не добавляют дополнительных Lua-методов** в проверенном исходном коде.

## Ошибки

- Устройства нет: неподдерживаемый блок, нет Wired Fuze, модема или регистрации capability.
- `detonate()` возвращает `false`: блок успел измениться.
- При ускоренных компьютерах серверный вызов может ожидать физического подшага.
- Перед работой с другой сборкой сверяйте `peripheral.getMethods(name)`.

**Версия:** `gradle.properties` содержит **1.2.9**, хотя в README могут остаться исторические номера выпусков.

Исходники: [ExplosivePeripheral.java](https://github.com/323erir6/MianbaoSableExplosionCompat/blob/main/src/main/java/dev/mianbaosablecompat/peripheral/ExplosivePeripheral.java), [ExplosivePeripheralCapabilities.java](https://github.com/323erir6/MianbaoSableExplosionCompat/blob/main/src/main/java/dev/mianbaosablecompat/peripheral/ExplosivePeripheralCapabilities.java).