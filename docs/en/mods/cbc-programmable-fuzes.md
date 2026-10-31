# CBC Programmable Fuzes 1.4.1 — CC:Tweaked API

**Evidence:** Java sources in [CBC-Programmable-Fuzes](https://github.com/323erir6/CBC-Programmable-Fuzes), especially [FuzePeripheralMethods.java](https://github.com/323erir6/CBC-Programmable-Fuzes/blob/main/src/main/java/ua/ivan/cbcprogrammablefuzes/peripheral/FuzePeripheralMethods.java), [FuzeCapabilities.java](https://github.com/323erir6/CBC-Programmable-Fuzes/blob/main/src/main/java/ua/ivan/cbcprogrammablefuzes/peripheral/FuzeCapabilities.java), the two telemetry registries, and `FuzeConfig.java`. GitHub `gradle.properties` identifies version **1.4.1**, Minecraft 1.21.1. This file records the **published source-code API**, not a measured in-game test.

## Installation and integration

The mod registers a generic CC:Tweaked peripheral whose additional types are `programmable_fuze` and `cbc_programmable_fuze`. Access is provided on compatible **placed fuzed projectile blocks** and **assembled cannon mounts** with supported loaded projectiles, including compatible add-on mounts. It does not remove the mount's existing methods. Attach a wired modem to a compatible block, open the network and identify the peripheral using `peripheral.getNames()` and `peripheral.getType(name)`.

### Discovery

```lua
local found = {}
for _, name in ipairs(peripheral.getNames()) do
  local ty = {peripheral.getType(name)}
  for _, value in ipairs(ty) do
    if value == "programmable_fuze" or value == "cbc_programmable_fuze" then
      found[#found + 1] = name
      break
    end
  end
end
assert(#found > 0, "No programmable fuze peripheral found")
for _, name in ipairs(found) do
  print(name, table.concat(peripheral.getMethods(name) or {}, ", "))
end
```

`peripheral.find("programmable_fuze")` is the short form if the peripheral is unique. A compatible device may expose other peripheral types simultaneously, so resolve the actual device before selecting it.

## Complete Lua method index

The Java `ProgrammableFuzeAccess target` argument is **injected by GenericPeripheral**; it is *not* a Lua argument.

| Lua method | Arguments | Returns / behavior |
| --- | --- | --- |
| `hasProgrammableFuze()` | none | boolean: a compatible loaded programmable fuze is present |
| `setProximity(radius, active)` | number, boolean | true or Lua error; configure proximity mode |
| `setTimer(seconds, active)` | number, boolean | true or Lua error; configure timed mode |
| `setPersistent(active)` | boolean | true or Lua error; configure projectile persistence |
| `setFuzeChannel(channel)` | string | true or Lua error; store communication channel |
| `listFuzeProjectiles(channel)` | string | array of live in-flight fuze summaries |
| `getFuzeTelemetry(channel, id)` | string, UUID string | `true, table` if found; `false` if absent |
| `setFuzeProjectileTimer(channel,id,seconds,active)` | string, string, number, boolean | boolean: update in-flight timer |
| `setFuzeProjectileProximity(channel,id,radius,active)` | string, string, number, boolean | boolean: update in-flight proximity |
| `setFuzeProjectilePersistent(channel,id,active)` | string, string, boolean | boolean: update in-flight persistence |
| `setFuzeProjectileChannel(channel,id,newChannel)` | 3 strings | boolean: move in-flight projectile's channel |
| `setFuzeProjectileSettings(channel,id,timerSeconds,timerActive,proximityRadius,proximityActive,persistent)` | strings, numbers, booleans in stated order | boolean: replace all settings atomically |
| `hasTrajectoryCorrectionModule()` | none | boolean: installed correction tail module present |
| `setCorrectionChannel(channel)` | string | true or Lua error |
| `setCorrectionPersistent(active)` | boolean | true or Lua error |
| `setImpactCoordinates(x,y,z)` | 3 numbers | true or Lua error; configure installed module's world-coordinate target |
| `listCorrectionProjectiles(channel)` | string | array of flying correction-module summaries |
| `getCorrectionTelemetry(channel,id)` | string, UUID string | `true, table` or `false` |
| `setCorrectionProjectileTarget(channel,id,x,y,z)` | string, string, 3 numbers | boolean: change target in-flight |
| `getLoadedProjectileInfo()` | none | `true, table` or `false` |
| `getLoadedPropellantInfo()` | none | `true, table` or `false` |
| `getCannonInfo()` | none | `true, table` or `false` |

**Boolean vs errors:** `set...()` methods may throw `LuaException` if disabled in server config, the device has no supported item or a numeric argument is out of range. Use `pcall` for expected failures. `false` from an in-flight method may mean that the UUID/channel pair is not registered.

## Numerical limits, timing and configuration

`FuzeConfig.java` defines defaults `proximityRadius=2.0` blocks, `timerSeconds=15.0` seconds, minimum proximity radius 0, maximum 64, minimum timer 0, maximum 86,400 seconds; hard upper bounds are radius **1,024** and timer **31,536,000 seconds**. Server configuration may narrow these ranges or disable modes. A requested timer is rounded *up* to a 20 Hz step using `ceil(seconds * 20) / 20`. Non-finite coordinates/radii/delays are rejected. The default correction range multiplier is **1.10** and default turn authority **6 degrees per kilometre**; both are server-adjustable and not a guarantee of exact trajectory.

Functions annotated `@LuaFunction(mainThread=true)` use the server/main-thread continuation. Several in-flight methods are intentionally *not* main-thread methods and instead update a latest-state mailbox, reducing backlog with Sable tick acceleration. There can still be a short delay between a successful update and the projectile applying it.

## In-flight fuze telemetry schema

`listFuzeProjectiles(channel)` returns summary rows containing `id`, `type`, `ageTicks`, `timerSecondsRemaining`. Detailed `getFuzeTelemetry(channel,id)` includes:
`id`, `channel`, `dimension`, `type`,
`x`, `y`, `z`, `velocityX`, `velocityY`, `velocityZ`,
`speed`, `ageTicks`, `timerTicksRemaining`, `timerSecondsRemaining`,
`armed`, `updatePending`.
Additional settings may be merged from `FuzeSettings`; inspect returned keys if relying on any field not explicitly listed here. A missing target gives `false` rather than a telemetry table.

## Correction telemetry schema

`listCorrectionProjectiles(channel)` summary rows: `id`, `type`, `ageTicks`.

Detailed `getCorrectionTelemetry(channel,id)` fields:
`id`, `channel`, `dimension`, `type`, `x`, `y`, `z`,
`velocityX`, `velocityY`, `velocityZ`, `speed`, `ageTicks`,
`hasTarget`, optional `targetX`, `targetY`, `targetZ`,
`targetDistance`, `correctionDegreesRemaining`,
`correctionDistanceRemaining`, `guidanceActive`, `targetForward`,
`rangeMultiplierApplied`.

Do not read optional target coordinates without checking `hasTarget`.

## Cannon inspection result tables

`getCannonInfo()`: if assembled, may provide `assembled`, `cannonClass`, `lengthBlocks`, `muzzleDistanceBlocks`, `weight`, `initialOrientation`, `axis`, `startPosition`, `cannonType`, `ballisticProfile` and cannon material properties. Big-cannon properties: `material`, `weightPerBlock`, `minimumVelocityPerBarrel`, `maxSafePropellantStress`, `failureMode`, `weldable`, `weldDamage`, `weldStressPenalty`, `minimumSpread`, `spreadReductionPerBarrel`, `maxSafeCharges`. Autocannon properties can include `maximumBarrelLength`, `baseSpeedBlocksPerTick`, `baseSpeedMetersPerSecond`, `speedIncreasePerBarrelBlocksPerTick`, `maximumSpeedIncreases`, `projectileLifetimeTicks` and recoil fields. Unknown add-ons can return only generic fields.

`getLoadedProjectileInfo()`: conditional fields include `id`, `name`, `blockCount`, `positions`, `complete`, `projectileEntity`, `projectileMass`, `addedChargePower`, `minimumChargePower`, `physicalDiameterMetres`, `hasFuze`, `hasProgrammableFuze`, `hasTracer`, `hasTrajectoryCorrectionModule`. Not all projectiles have all fields.

`getLoadedPropellantInfo()`: `count`, `segments`, `usesSeparateCharges`, `totalChargePower`, `totalStress`, `totalSpread`, `effectiveRecoil`, possibly `maxSafeCharges`, `overloaded`. Segment rows may include `id`, `name`, `position`, `chargePower`, `stress`, `spread`, `recoil`, `damp`, `waterlogged`. Autocannon ammunition has no separate charges.

**Important:** `physicalDiameterMetres` is the projectile *hitbox* used for inspection, not necessarily the ballistic solver's nominal calibre.

## Safe read-only Lua example

```lua
local fuze = assert(peripheral.find("programmable_fuze"), "Fuze peripheral missing")
local success, info = fuze.getLoadedProjectileInfo()
if success then
  print("Loaded projectile:")
  print(textutils.serialize(info))
else
  print("No accessible projectile")
end

local channel = "unsecured"
for _, item in ipairs(fuze.listFuzeProjectiles(channel) or {}) do
  local ok, telemetry = fuze.getFuzeTelemetry(channel, item.id)
  if ok and type(telemetry) == "table" then
    print(item.id, telemetry.speed, telemetry.timerSecondsRemaining)
  end
end
```

This example intentionally **does not** modify live ammunition.

## Failure cases

1. No peripheral: modem absent, mount not assembled, unsupported block, or add-on disabled.
2. Missing method: installed version differs; print `peripheral.getMethods(name)`.
3. Programming disabled: server config `enableComputerProgramming` or feature switches.
4. Invalid range: check runtime configured limits, do not hardcode defaults as guarantees.
5. `get...Telemetry` returns false: no entry in channel, stale (>30 seconds), or removed entity.
6. World/dimension mismatch: telemetry includes dimension; compare before using coordinates.
7. A mod changes how cannon blocks are exposed: inspect the exact mounted cannon peripheral.

**Reference source:** repository commit `d3ba2fd8cd0a74facd71c7f9c3718bdb66cc0282` inspected, 2026-10-31.