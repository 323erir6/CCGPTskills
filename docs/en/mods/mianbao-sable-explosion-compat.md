# Mianbao Sable Explosion Compat 1.2.9 — CC peripheral

**Source:** [MianbaoSableExplosionCompat](https://github.com/323erir6/MianbaoSableExplosionCompat), commit `2335b47b2fb4cf9cee9375424d8b22b5f83ae401`. Specifically verified `peripheral/ExplosivePeripheral.java` and `ExplosivePeripheralCapabilities.java`.

## Exposed peripheral

Type: **`explosive`**. The NeoForge CC:Tweaked peripheral capability is registered only for:

1. Mianbao Modern Warfare `mianbaos_modernwarfare:tnt` block.
2. Mianbao Modern Warfare `mianbaos_modernwarfare:nuclearbomb` block.
3. CBC `FuzedProjectileBlock` with a **Wired Fuze** item installed.

An eligible block must satisfy the runtime `supports(state, blockEntity)` check. Not every explosive-looking block has the peripheral.

## Exact Lua signature

`explosive.detonate() -> boolean`: a server-thread `@LuaFunction(mainThread=true)`. It returns `true` if a supported block was processed and `false` if its current block/entity state was no longer eligible. It throws a Lua error if not running on a server.

The call delegates to underlying Mianbao TNT or nuclear bomb procedures, or to CBC's on-the-spot fuzed projectile detonation. **It does not fake a Redstone pulse or change projectile velocity**.

## Safe inspection

```lua
for _,name in ipairs(peripheral.getNames()) do
  if peripheral.hasType(name,"explosive") then
    print("Compatible explosive peripheral:",name)
    print(textutils.serialize(peripheral.getMethods(name)))
  end
end
```

Avoid calling `detonate` from a background loop. Peripheral access should be guarded by deliberate user authorization and server rules; its effects modify the world.

## Other behavior

The same mod maps Mianbao blast effects onto intersecting Sable constructions; it implements direct and queued explosions, caching, bounded per-tick work, and temporary chunk residency. These mechanisms are Minecraft/NeoForge code and **do not add additional Lua functions** in this inspected source version.

**Version note:** README may contain historical release descriptions; `gradle.properties` is **1.2.9**. Do not mistake changelog headings for the deployed version.

## Failure conditions

- `peripheral.find("explosive")` returns nil: unsupported block, no suitable fuze, missing modem, or capability not registered.
- `detonate()` returns false: block changed since discovery.
- Scheduling under Sable high-frequency execution can still yield for server-side continuation.
- Check `peripheral.getMethods` before depending on a method in a different build.

Sources: [ExplosivePeripheral.java](https://github.com/323erir6/MianbaoSableExplosionCompat/blob/main/src/main/java/dev/mianbaosablecompat/peripheral/ExplosivePeripheral.java) and [ExplosivePeripheralCapabilities.java](https://github.com/323erir6/MianbaoSableExplosionCompat/blob/main/src/main/java/dev/mianbaosablecompat/peripheral/ExplosivePeripheralCapabilities.java).