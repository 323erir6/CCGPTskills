# Полный аудит JAR — архив модов 6.9.3

**Архив:** `6.9.3_OneOne.rar`. Проверены все **143 JAR**, включая **4 отключённых**.

## Методика

Каждый JAR был прочитан из архива как ZIP, его `.class` проверены на ссылки на CC:Tweaked: `dan200/computercraft`, `LuaFunction`, `PeripheralCapability`, `ILuaAPI`, `IPeripheral`. Для кандидатов проверены Java-классы инструментом `javap`. Это **статический анализ**, а не гарантия совместимости во время игры.

**Различия:**
- **Есть ссылка на CC:** JAR содержит байткод/маркер CC, но это ещё не означает регистрацию Lua-функции. Базовая Sable и Synaxis могут содержать встроенные маркеры библиотек.
- **Прямых ссылок нет:** в проверенных классах нет маркеров; это **не исключает** косвенного взаимодействия через другой мод, capability или Mixin.
- **Выключен:** файл `.jar.disabled` не создаёт активную периферию.
- Оригинальные сторонние бинарники не публикуются в библиотеке.
- Вложенные зависимости, нестандартные системы вызовов и косвенные интеграции требуют дополнительного изучения исходников.

## Все файлы архива

| № | Имя файла | Результат статической проверки |
| ---: | --- | --- |
| 1 | `AdvancedPeripherals-1.21.1-0.7.61b.jar` | есть ссылка на CC в байткоде |
| 2 | `AeroEngine-1.3.0.jar` | прямые ссылки на CC не обнаружены |
| 3 | `aeronautics_translation-1.1.jar` | прямые ссылки на CC не обнаружены |
| 4 | `aeroworks-1.5.0.jar` | прямые ссылки на CC не обнаружены |
| 5 | `alltheleaks-1.1.12+1.21.1-neoforge.jar` | прямые ссылки на CC не обнаружены |
| 6 | `architectury-13.0.11-neoforge.jar` | прямые ссылки на CC не обнаружены |
| 7 | `arcon-1.05-prerelease-2.5.jar` | прямые ссылки на CC не обнаружены |
| 8 | `azimuth-1.4.9.jar` | прямые ссылки на CC не обнаружены |
| 9 | `bits_n_bobs-2.3.5.jar` | есть ссылка на CC в байткоде |
| 10 | `bits_n_tracks-3.0.0-dev.e375a6a.jar` | прямые ссылки на CC не обнаружены |
| 11 | `cbc_aero_velocity_fix-1.0.7.jar` | прямые ссылки на CC не обнаружены |
| 12 | `cbc_at_Neoforge_1.21.1_0.1.4c.jar` | прямые ссылки на CC не обнаружены |
| 13 | `cbc_compact_mount-1.2.2.jar` | прямые ссылки на CC не обнаружены |
| 14 | `cbcatfix-1.1.4.jar.disabled` | выключен |
| 15 | `cbcatfix-1.21.1-neoforge-1.0.1.jar` | прямые ссылки на CC не обнаружены |
| 16 | `CBC-Military-Supplement-1.21.1-3.0.7.jar` | прямые ссылки на CC не обнаружены |
| 17 | `cbcmodernwarfare-0.0.6v+mc.1.21.1-neoforge.jar` | прямые ссылки на CC не обнаружены |
| 18 | `CBCmoreshells-1.5.1.jar` | прямые ссылки на CC не обнаружены |
| 19 | `cbcmsmwcompat-2.1.3.jar` | прямые ссылки на CC не обнаружены |
| 20 | `cbc-programmable-fuzes-1.4.1.jar` | есть ссылка на CC в байткоде |
| 21 | `cbc-realistic-ballistics-1.9.22.jar` | прямые ссылки на CC не обнаружены |
| 22 | `cc_ar-0.2.1.jar` | есть ссылка на CC в байткоде |
| 23 | `cc_sable-neoforge-1.3.4.jar` | есть ссылка на CC в байткоде |
| 24 | `cc-tweaked-1.21.1-forge-1.120.0.jar` | есть ссылка на CC в байткоде |
| 25 | `chat_heads-0.15.1-neoforge-1.21.jar` | прямые ссылки на CC не обнаружены |
| 26 | `cloth-config-15.0.140-neoforge.jar` | прямые ссылки на CC не обнаружены |
| 27 | `compactflap-neoforge-1.21.1-1.0.4.1.jar` | прямые ссылки на CC не обнаружены |
| 28 | `Controlling-neoforge-1.21.1-19.0.5.jar` | прямые ссылки на CC не обнаружены |
| 29 | `copycat_aeronautics_sails-0.1.18.jar` | прямые ссылки на CC не обнаружены |
| 30 | `copycats-3.0.9+mc.1.21.1-neoforge.jar` | прямые ссылки на CC не обнаружены |
| 31 | `crawlondemand-1.21-1.21.5-1.2.0+neoforge.jar` | прямые ссылки на CC не обнаружены |
| 32 | `create_aeronautics_toolgun-0.3.6.jar` | прямые ссылки на CC не обнаружены |
| 33 | `create_aeronautics_transmission_linkage-0.2.8.jar` | прямые ссылки на CC не обнаружены |
| 34 | `create_connected-1.3.3-mc1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 35 | `create_radar_firearc-1.0.0.jar` | прямые ссылки на CC не обнаружены |
| 36 | `create_radar_mobile_radars-1.0.0.jar` | прямые ссылки на CC не обнаружены |
| 37 | `create_radar-0.4.4-1.21.1.jar` | есть ссылка на CC в байткоде |
| 38 | `create_tweaked_controllers-1.21.1-1.2.7.jar` | есть ссылка на CC в байткоде |
| 39 | `Create_Warnautics-1.1+mc.1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 40 | `create-1.21.1-6.0.10.jar` | есть ссылка на CC в байткоде |
| 41 | `createaddition-1.7.0.jar` | есть ссылка на CC в байткоде |
| 42 | `create-aeronautics-bundled-1.21.1-1.3.2.jar` | прямые ссылки на CC не обнаружены |
| 43 | `CreateAeronauticsCopycatWing-1.21.1-1.0.4.jar` | прямые ссылки на CC не обнаружены |
| 44 | `CreateAeronauticsVariableWeightBlock-1.21.1-1.0.0.jar` | прямые ссылки на CC не обнаружены |
| 45 | `createarms-1.0.0.jar` | прямые ссылки на CC не обнаружены |
| 46 | `createbetterfps-1.21.1-1.1.4.jar` | прямые ссылки на CC не обнаружены |
| 47 | `createbigcannons-5.11.7+mc.1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 48 | `createdeco-2.1.3.jar` | прямые ссылки на CC не обнаружены |
| 49 | `createdieselgenerators-1.21.1-1.3.15.jar` | есть ссылка на CC в байткоде |
| 50 | `createendertransmission-2.1.1-1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 51 | `createpropulsion-1.1.5.jar` | есть ссылка на CC в байткоде |
| 52 | `create-scalable-wheels-1.2.3.jar` | прямые ссылки на CC не обнаружены |
| 53 | `CreativeCore_NEOFORGE_v2.13.46_mc1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 54 | `curios-neoforge-9.5.1+1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 55 | `CustomSkinLoader_Universal-14.28.jar` | прямые ссылки на CC не обнаружены |
| 56 | `Design-n-Decor-1.21.1-2.2b.jar` | прямые ссылки на CC не обнаружены |
| 57 | `drivebywire-0.3.0.jar` | прямые ссылки на CC не обнаружены |
| 58 | `dynamic-fps-3.11.4+minecraft-1.21.0-neoforge.jar` | прямые ссылки на CC не обнаружены |
| 59 | `enhanced-detector-radar-1.0.5.jar` | есть ссылка на CC в байткоде |
| 60 | `entityculling-neoforge-1.10.5-mc1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 61 | `ferritecore-7.0.3-neoforge.jar` | прямые ссылки на CC не обнаружены |
| 62 | `flerovium-neoforge-1.21.1-1.1.3-all.jar` | прямые ссылки на CC не обнаружены |
| 63 | `forgified-fabric-api-0.116.14+2.3.0+1.21.1-optional-mod.jar` | прямые ссылки на CC не обнаружены |
| 64 | `FramedBlocks-10.6.1.jar` | прямые ссылки на CC не обнаружены |
| 65 | `geckolib-neoforge-1.21.1-4.8.4.jar` | прямые ссылки на CC не обнаружены |
| 66 | `ImmediatelyFast-NeoForge-1.6.14+1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 67 | `interiors-1.21.1-neoforge-0.6.1.jar` | прямые ссылки на CC не обнаружены |
| 68 | `iris-flywheel-compat-NeoForge-2.4.0.jar` | прямые ссылки на CC не обнаружены |
| 69 | `iris-neoforge-1.8.14-beta.1+mc1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 70 | `Ixeris-4.6.5+1.21.1-neoforge.jar` | прямые ссылки на CC не обнаружены |
| 71 | `Jade-1.21.1-NeoForge-15.10.5.jar` | прямые ссылки на CC не обнаружены |
| 72 | `jei-1.21.1-neoforge-19.56.0.439.jar` | прямые ссылки на CC не обнаружены |
| 73 | `justzoom_neoforge_2.1.0_MC_1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 74 | `konkrete_neoforge_1.9.9_MC_1.21.jar` | прямые ссылки на CC не обнаружены |
| 75 | `kotlinforforge-5.12.0-all.jar` | прямые ссылки на CC не обнаружены |
| 76 | `kubejs-neoforge-2101.7.2-build.368.jar` | прямые ссылки на CC не обнаружены |
| 77 | `ldlib2-neoforge-1.21.1-2.2.29-all.jar` | прямые ссылки на CC не обнаружены |
| 78 | `lithium-neoforge-0.15.4+mc1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 79 | `lmft-1.1.1+1.21.9-neoforge.jar` | прямые ссылки на CC не обнаружены |
| 80 | `mianbaos_modernwarfare-2.6.4-neoforge.jar` | прямые ссылки на CC не обнаружены |
| 81 | `mianbao-sable-explosion-compat-1.2.9.jar` | есть ссылка на CC в байткоде |
| 82 | `modernfix-neoforge-5.27.26+mc1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 83 | `moonlight-1.21.1-3.4.0-neoforge.jar` | прямые ссылки на CC не обнаружены |
| 84 | `moreculling-neoforge-1.21.1-1.0.10.jar` | прямые ссылки на CC не обнаружены |
| 85 | `MouseTweaks-neoforge-mc1.21-2.26.1.jar` | прямые ссылки на CC не обнаружены |
| 86 | `neoperipheral-1.4ve.jar` | есть ссылка на CC в байткоде |
| 87 | `nowheel-2.0.0+1.21.1neoforge.jar` | прямые ссылки на CC не обнаружены |
| 88 | `packetfixer-3.3.1-1.20.5-1.21.X-merged.jar` | прямые ссылки на CC не обнаружены |
| 89 | `portable_engine_liquid_fuel-2.0.0-neoforge-1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 90 | `qmodeling-2.0.3rp.jar` | прямые ссылки на CC не обнаружены |
| 91 | `railways-0.3.0-beta.2+neoforge-mc1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 92 | `reeses-sodium-options-neoforge-2.2.4+mc1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 93 | `rha_plus-1.0.4-1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 94 | `rha-1.0.3b.jar` | прямые ссылки на CC не обнаружены |
| 95 | `rhino-2101.2.7-build.81.jar` | прямые ссылки на CC не обнаружены |
| 96 | `ritchiesprojectilelib-2.1.2+mc.1.21.1-neoforge.jar` | прямые ссылки на CC не обнаружены |
| 97 | `rolling-tones-0.2.2.jar` | прямые ссылки на CC не обнаружены |
| 98 | `roxy-1.21.1-NeoForge-0.4.0-optional-mod.jar` | прямые ссылки на CC не обнаружены |
| 99 | `s_a_b-1.4.3-neoforge-1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 100 | `sable_honey_welder_fix-1.0.0.jar` | прямые ссылки на CC не обнаружены |
| 101 | `sable_nc-1.2.jar` | прямые ссылки на CC не обнаружены |
| 102 | `sable-autonomous-chunk-loader-1.7.9.jar.disabled` | выключен |
| 103 | `sable-autonomous-chunk-loader-1.8.0.jar.disabled` | выключен |
| 104 | `sable-autonomous-chunk-loader-1.8.1.jar` | есть ссылка на CC в байткоде |
| 105 | `sable-beyond-fluid-safety-1.0.0 (1).jar` | прямые ссылки на CC не обнаружены |
| 106 | `sablebeyond-neoforge-1.21.1-v0.5.0.jar` | прямые ссылки на CC не обнаружены |
| 107 | `sable-cc-tick-sync-1.6.4.jar` | есть ссылка на CC в байткоде |
| 108 | `sable-high-altitude-transit-1.3.5.jar` | прямые ссылки на CC не обнаружены |
| 109 | `sablemassview-1.0.0.jar` | прямые ссылки на CC не обнаружены |
| 110 | `sable-neoforge-1.21.1-2.0.5.jar` | есть ссылка на CC в байткоде |
| 111 | `sable-photomancy-1.0.1.jar` | прямые ссылки на CC не обнаружены |
| 112 | `saturn-mc1.21.1-0.1.5.jar` | прямые ссылки на CC не обнаружены |
| 113 | `Searchables-neoforge-1.21.1-1.0.2.jar` | прямые ссылки на CC не обнаружены |
| 114 | `server_crash_guard-1.0.2.jar` | прямые ссылки на CC не обнаружены |
| 115 | `shaolib_munitions-0.1.0.jar` | прямые ссылки на CC не обнаружены |
| 116 | `shaolib-0.1.1.jar` | прямые ссылки на CC не обнаружены |
| 117 | `skinrestorer-2.7.0+1.21-neoforge.jar` | прямые ссылки на CC не обнаружены |
| 118 | `snassets_particles-1.0.1.jar` | прямые ссылки на CC не обнаружены |
| 119 | `snassets-1.0.2.jar` | прямые ссылки на CC не обнаружены |
| 120 | `sodium-extra-neoforge-0.9.4+mc1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 121 | `sodium-neoforge-0.8.13+mc1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 122 | `SSRD-1.8.6-1.21.1.jar` | прямые ссылки на CC не обнаружены |
| 123 | `struts-1.3.1.jar` | прямые ссылки на CC не обнаружены |
| 124 | `suspack-1.0.8.jar` | прямые ссылки на CC не обнаружены |
| 125 | `synaxis_patchpack-1.0.0.jar` | есть ссылка на CC в байткоде |
| 126 | `synaxis-1.5.0.jar` | есть ссылка на CC в байткоде |
| 127 | `synaxisplus-1.0.5.jar` | прямые ссылки на CC не обнаружены |
| 128 | `taov_core-0.1.0.jar` | прямые ссылки на CC не обнаружены |
| 129 | `taov_weapons-0.1.1.jar.disabled` | выключен |
| 130 | `taov_weapons-0.1.1-compat.1.jar` | прямые ссылки на CC не обнаружены |
| 131 | `tfmg-1.21.1-1.3.2a-community.jar` | прямые ссылки на CC не обнаружены |
| 132 | `toms-peripherals-1.21-1.3.1.jar` | есть ссылка на CC в байткоде |
| 133 | `touys-neoforge-1.21.1-1.1.0.jar` | прямые ссылки на CC не обнаружены |
| 134 | `tracks_plus-1.0.6b7.jar` | прямые ссылки на CC не обнаружены |
| 135 | `veil-neoforge-1.21.1-4.5.2.jar` | прямые ссылки на CC не обнаружены |
| 136 | `vestalihy-2.5.6.jar` | прямые ссылки на CC не обнаружены |
| 137 | `vista-1.21.1-5.5.7-neoforge (1).jar` | есть ссылка на CC в байткоде |
| 138 | `voicechat-neoforge-1.21.1-2.6.17 (1).jar` | прямые ссылки на CC не обнаружены |
| 139 | `voxy-0.2.16-beta+1.21.11-optional-mod.jar` | прямые ссылки на CC не обнаружены |
| 140 | `xaerominimap-neoforge-1.21.1-26.5.0.jar` | прямые ссылки на CC не обнаружены |
| 141 | `xaeroworldmap-neoforge-1.21.1-1.46.0.jar` | прямые ссылки на CC не обнаружены |
| 142 | `yet_another_config_lib_v3-3.8.2+1.21.1-neoforge.jar` | прямые ссылки на CC не обнаружены |
| 143 | `zfastnoise-1.0.13+1.21.1+neoforge.jar` | прямые ссылки на CC не обнаружены |

## Дальнейшая проверка

См. [каталог периферии](mods/installed-peripherals.md), где настоящие методы CC отделены от общих Java-ссылок. Один результат сканирования **не даёт оснований** выдумывать Lua API.
