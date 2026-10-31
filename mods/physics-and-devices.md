# Modded physics, rotation and GPU devices

## English

Physical contraptions, rotational speed controllers, radar-like peripherals and external GPU displays are **third-party integrations**, not built-in CC:Tweaked modules.

A reliable integration starts with an on-device capability inventory:

```lua
for _, name in ipairs(peripheral.getNames()) do
  print("Device", name, "type", peripheral.getType(name))
  print(textutils.serialize(peripheral.getMethods(name)))
end
```

Check the documentation of the actual mod version before calling any method. Potential device families include:

- Ship or sublevel interfaces: world-space positions, velocity, local/world transforms.
- Rotation speed controllers and servomotors: actual range, sign conventions and units.
- Radar peripherals: scan results, coordinate frames, entity classification and update rate.
- GPU peripherals: width, height, draw calls, synchronization and input-event semantics.

**Do not assume** a method named `getWorldspacePosition`, `getTransformationMatrix`, `setTarget`, `scanForShips`, `setSize` or `sync` exists on a particular installation. These names are examples of capabilities that require validation, not a guaranteed API.

Transform verification: identify matrix storage order (row/column major), handedness, axis directions, units and whether coordinates are in local or global space. Test with a known axis-aligned construction before computing local velocity or orientation.

## Русский

Физические конструкции, регуляторы вращения, радары и GPU-дисплеи относятся к **сторонним интеграциям**, а не базовому CC:Tweaked.

Перед разработкой считайте доступные типы и методы с реальных устройств. Записывайте версию каждого мода.

Возможные категории: интерфейсы кораблей и подуровней, сервоприводы, скоростные регуляторы, радары, GPU. Названия вроде `getWorldspacePosition`, `getTransformationMatrix`, `setTarget`, `scanForShips`, `setSize`, `sync` приведены только как примеры для проверки; их наличие **не гарантируется**.

При использовании матриц обязательно определите порядок хранения, ориентацию осей, единицы измерения и глобальную/локальную систему координат. Проверяйте преобразования на известном тестовом объекте.
