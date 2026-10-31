# Complete JAR audit — modpack archive 6.9.3

**Archive:** `6.9.3_OneOne.rar`. Scanned all **143 JAR entries**, including **4 disabled** files.

## Method

Each JAR was extracted from the archive, opened as ZIP, and its `.class` content scanned for CC:Tweaked bytecode references such as `dan200/computercraft`, `LuaFunction`, `PeripheralCapability`, `ILuaAPI` and `IPeripheral`. Candidate peripheral classes were inspected with `javap`. This is a **static scan**, not a full dependency graph or in-game compatibility certification.

**Critical distinctions:**
- **CC bytecode reference found:** the JAR mentions CC API or a matching marker, but a class may not register a Lua method. Example: the Sable base library and Synaxis may contain library/embedded Lua markers.
- **No direct CC bytecode reference:** no such marker in its own classes; **does not prove** the mod cannot interact through a different provider or change CC hardware by Mixin.
- **Disabled:** the JAR ends in `.disabled` and should not contribute active mod APIs.
- Read-only inventory only: no original copyrighted JARs are mirrored in this repository.
- Custom modifications, nested JAR dependencies and Lua APIs exposed indirectly through external capability providers need additional source checks.

## Every archive entry

| # | Exact file name | Static CC marker result |
| ---: | --- | --- |
| 1 | `AdvancedPeripherals-1.21.1-0.7.61b.jar` | CC bytecode reference found |
| 2 | `AeroEngine-1.3.0.jar` | no direct CC bytecode reference |
| 3 | `aeronautics_translation-1.1.jar` | no direct CC bytecode reference |
| 4 | `aeroworks-1.5.0.jar` | no direct CC bytecode reference |
| 5 | `alltheleaks-1.1.12+1.21.1-neoforge.jar` | no direct CC bytecode reference |
| 6 | `architectury-13.0.11-neoforge.jar` | no direct CC bytecode reference |
| 7 | `arcon-1.05-prerelease-2.5.jar` | no direct CC bytecode reference |
| 8 | `azimuth-1.4.9.jar` | no direct CC bytecode reference |
| 9 | `bits_n_bobs-2.3.5.jar` | CC bytecode reference found |
| 10 | `bits_n_tracks-3.0.0-dev.e375a6a.jar` | no direct CC bytecode reference |
| 11 | `cbc_aero_velocity_fix-1.0.7.jar` | no direct CC bytecode reference |
| 12 | `cbc_at_Neoforge_1.21.1_0.1.4c.jar` | no direct CC bytecode reference |
| 13 | `cbc_compact_mount-1.2.2.jar` | no direct CC bytecode reference |
| 14 | `cbcatfix-1.1.4.jar.disabled` | disabled |
| 15 | `cbcatfix-1.21.1-neoforge-1.0.1.jar` | no direct CC bytecode reference |
| 16 | `CBC-Military-Supplement-1.21.1-3.0.7.jar` | no direct CC bytecode reference |
| 17 | `cbcmodernwarfare-0.0.6v+mc.1.21.1-neoforge.jar` | no direct CC bytecode reference |
| 18 | `CBCmoreshells-1.5.1.jar` | no direct CC bytecode reference |
| 19 | `cbcmsmwcompat-2.1.3.jar` | no direct CC bytecode reference |
| 20 | `cbc-programmable-fuzes-1.4.1.jar` | CC bytecode reference found |
| 21 | `cbc-realistic-ballistics-1.9.22.jar` | no direct CC bytecode reference |
| 22 | `cc_ar-0.2.1.jar` | CC bytecode reference found |
| 23 | `cc_sable-neoforge-1.3.4.jar` | CC bytecode reference found |
| 24 | `cc-tweaked-1.21.1-forge-1.120.0.jar` | CC bytecode reference found |
| 25 | `chat_heads-0.15.1-neoforge-1.21.jar` | no direct CC bytecode reference |
| 26 | `cloth-config-15.0.140-neoforge.jar` | no direct CC bytecode reference |
| 27 | `compactflap-neoforge-1.21.1-1.0.4.1.jar` | no direct CC bytecode reference |
| 28 | `Controlling-neoforge-1.21.1-19.0.5.jar` | no direct CC bytecode reference |
| 29 | `copycat_aeronautics_sails-0.1.18.jar` | no direct CC bytecode reference |
| 30 | `copycats-3.0.9+mc.1.21.1-neoforge.jar` | no direct CC bytecode reference |
| 31 | `crawlondemand-1.21-1.21.5-1.2.0+neoforge.jar` | no direct CC bytecode reference |
| 32 | `create_aeronautics_toolgun-0.3.6.jar` | no direct CC bytecode reference |
| 33 | `create_aeronautics_transmission_linkage-0.2.8.jar` | no direct CC bytecode reference |
| 34 | `create_connected-1.3.3-mc1.21.1.jar` | no direct CC bytecode reference |
| 35 | `create_radar_firearc-1.0.0.jar` | no direct CC bytecode reference |
| 36 | `create_radar_mobile_radars-1.0.0.jar` | no direct CC bytecode reference |
| 37 | `create_radar-0.4.4-1.21.1.jar` | CC bytecode reference found |
| 38 | `create_tweaked_controllers-1.21.1-1.2.7.jar` | CC bytecode reference found |
| 39 | `Create_Warnautics-1.1+mc.1.21.1.jar` | no direct CC bytecode reference |
| 40 | `create-1.21.1-6.0.10.jar` | CC bytecode reference found |
| 41 | `createaddition-1.7.0.jar` | CC bytecode reference found |
| 42 | `create-aeronautics-bundled-1.21.1-1.3.2.jar` | no direct CC bytecode reference |
| 43 | `CreateAeronauticsCopycatWing-1.21.1-1.0.4.jar` | no direct CC bytecode reference |
| 44 | `CreateAeronauticsVariableWeightBlock-1.21.1-1.0.0.jar` | no direct CC bytecode reference |
| 45 | `createarms-1.0.0.jar` | no direct CC bytecode reference |
| 46 | `createbetterfps-1.21.1-1.1.4.jar` | no direct CC bytecode reference |
| 47 | `createbigcannons-5.11.7+mc.1.21.1.jar` | no direct CC bytecode reference |
| 48 | `createdeco-2.1.3.jar` | no direct CC bytecode reference |
| 49 | `createdieselgenerators-1.21.1-1.3.15.jar` | CC bytecode reference found |
| 50 | `createendertransmission-2.1.1-1.21.1.jar` | no direct CC bytecode reference |
| 51 | `createpropulsion-1.1.5.jar` | CC bytecode reference found |
| 52 | `create-scalable-wheels-1.2.3.jar` | no direct CC bytecode reference |
| 53 | `CreativeCore_NEOFORGE_v2.13.46_mc1.21.1.jar` | no direct CC bytecode reference |
| 54 | `curios-neoforge-9.5.1+1.21.1.jar` | no direct CC bytecode reference |
| 55 | `CustomSkinLoader_Universal-14.28.jar` | no direct CC bytecode reference |
| 56 | `Design-n-Decor-1.21.1-2.2b.jar` | no direct CC bytecode reference |
| 57 | `drivebywire-0.3.0.jar` | no direct CC bytecode reference |
| 58 | `dynamic-fps-3.11.4+minecraft-1.21.0-neoforge.jar` | no direct CC bytecode reference |
| 59 | `enhanced-detector-radar-1.0.5.jar` | CC bytecode reference found |
| 60 | `entityculling-neoforge-1.10.5-mc1.21.1.jar` | no direct CC bytecode reference |
| 61 | `ferritecore-7.0.3-neoforge.jar` | no direct CC bytecode reference |
| 62 | `flerovium-neoforge-1.21.1-1.1.3-all.jar` | no direct CC bytecode reference |
| 63 | `forgified-fabric-api-0.116.14+2.3.0+1.21.1-optional-mod.jar` | no direct CC bytecode reference |
| 64 | `FramedBlocks-10.6.1.jar` | no direct CC bytecode reference |
| 65 | `geckolib-neoforge-1.21.1-4.8.4.jar` | no direct CC bytecode reference |
| 66 | `ImmediatelyFast-NeoForge-1.6.14+1.21.1.jar` | no direct CC bytecode reference |
| 67 | `interiors-1.21.1-neoforge-0.6.1.jar` | no direct CC bytecode reference |
| 68 | `iris-flywheel-compat-NeoForge-2.4.0.jar` | no direct CC bytecode reference |
| 69 | `iris-neoforge-1.8.14-beta.1+mc1.21.1.jar` | no direct CC bytecode reference |
| 70 | `Ixeris-4.6.5+1.21.1-neoforge.jar` | no direct CC bytecode reference |
| 71 | `Jade-1.21.1-NeoForge-15.10.5.jar` | no direct CC bytecode reference |
| 72 | `jei-1.21.1-neoforge-19.56.0.439.jar` | no direct CC bytecode reference |
| 73 | `justzoom_neoforge_2.1.0_MC_1.21.1.jar` | no direct CC bytecode reference |
| 74 | `konkrete_neoforge_1.9.9_MC_1.21.jar` | no direct CC bytecode reference |
| 75 | `kotlinforforge-5.12.0-all.jar` | no direct CC bytecode reference |
| 76 | `kubejs-neoforge-2101.7.2-build.368.jar` | no direct CC bytecode reference |
| 77 | `ldlib2-neoforge-1.21.1-2.2.29-all.jar` | no direct CC bytecode reference |
| 78 | `lithium-neoforge-0.15.4+mc1.21.1.jar` | no direct CC bytecode reference |
| 79 | `lmft-1.1.1+1.21.9-neoforge.jar` | no direct CC bytecode reference |
| 80 | `mianbaos_modernwarfare-2.6.4-neoforge.jar` | no direct CC bytecode reference |
| 81 | `mianbao-sable-explosion-compat-1.2.9.jar` | CC bytecode reference found |
| 82 | `modernfix-neoforge-5.27.26+mc1.21.1.jar` | no direct CC bytecode reference |
| 83 | `moonlight-1.21.1-3.4.0-neoforge.jar` | no direct CC bytecode reference |
| 84 | `moreculling-neoforge-1.21.1-1.0.10.jar` | no direct CC bytecode reference |
| 85 | `MouseTweaks-neoforge-mc1.21-2.26.1.jar` | no direct CC bytecode reference |
| 86 | `neoperipheral-1.4ve.jar` | CC bytecode reference found |
| 87 | `nowheel-2.0.0+1.21.1neoforge.jar` | no direct CC bytecode reference |
| 88 | `packetfixer-3.3.1-1.20.5-1.21.X-merged.jar` | no direct CC bytecode reference |
| 89 | `portable_engine_liquid_fuel-2.0.0-neoforge-1.21.1.jar` | no direct CC bytecode reference |
| 90 | `qmodeling-2.0.3rp.jar` | no direct CC bytecode reference |
| 91 | `railways-0.3.0-beta.2+neoforge-mc1.21.1.jar` | no direct CC bytecode reference |
| 92 | `reeses-sodium-options-neoforge-2.2.4+mc1.21.1.jar` | no direct CC bytecode reference |
| 93 | `rha_plus-1.0.4-1.21.1.jar` | no direct CC bytecode reference |
| 94 | `rha-1.0.3b.jar` | no direct CC bytecode reference |
| 95 | `rhino-2101.2.7-build.81.jar` | no direct CC bytecode reference |
| 96 | `ritchiesprojectilelib-2.1.2+mc.1.21.1-neoforge.jar` | no direct CC bytecode reference |
| 97 | `rolling-tones-0.2.2.jar` | no direct CC bytecode reference |
| 98 | `roxy-1.21.1-NeoForge-0.4.0-optional-mod.jar` | no direct CC bytecode reference |
| 99 | `s_a_b-1.4.3-neoforge-1.21.1.jar` | no direct CC bytecode reference |
| 100 | `sable_honey_welder_fix-1.0.0.jar` | no direct CC bytecode reference |
| 101 | `sable_nc-1.2.jar` | no direct CC bytecode reference |
| 102 | `sable-autonomous-chunk-loader-1.7.9.jar.disabled` | disabled |
| 103 | `sable-autonomous-chunk-loader-1.8.0.jar.disabled` | disabled |
| 104 | `sable-autonomous-chunk-loader-1.8.1.jar` | CC bytecode reference found |
| 105 | `sable-beyond-fluid-safety-1.0.0 (1).jar` | no direct CC bytecode reference |
| 106 | `sablebeyond-neoforge-1.21.1-v0.5.0.jar` | no direct CC bytecode reference |
| 107 | `sable-cc-tick-sync-1.6.4.jar` | CC bytecode reference found |
| 108 | `sable-high-altitude-transit-1.3.5.jar` | no direct CC bytecode reference |
| 109 | `sablemassview-1.0.0.jar` | no direct CC bytecode reference |
| 110 | `sable-neoforge-1.21.1-2.0.5.jar` | CC bytecode reference found |
| 111 | `sable-photomancy-1.0.1.jar` | no direct CC bytecode reference |
| 112 | `saturn-mc1.21.1-0.1.5.jar` | no direct CC bytecode reference |
| 113 | `Searchables-neoforge-1.21.1-1.0.2.jar` | no direct CC bytecode reference |
| 114 | `server_crash_guard-1.0.2.jar` | no direct CC bytecode reference |
| 115 | `shaolib_munitions-0.1.0.jar` | no direct CC bytecode reference |
| 116 | `shaolib-0.1.1.jar` | no direct CC bytecode reference |
| 117 | `skinrestorer-2.7.0+1.21-neoforge.jar` | no direct CC bytecode reference |
| 118 | `snassets_particles-1.0.1.jar` | no direct CC bytecode reference |
| 119 | `snassets-1.0.2.jar` | no direct CC bytecode reference |
| 120 | `sodium-extra-neoforge-0.9.4+mc1.21.1.jar` | no direct CC bytecode reference |
| 121 | `sodium-neoforge-0.8.13+mc1.21.1.jar` | no direct CC bytecode reference |
| 122 | `SSRD-1.8.6-1.21.1.jar` | no direct CC bytecode reference |
| 123 | `struts-1.3.1.jar` | no direct CC bytecode reference |
| 124 | `suspack-1.0.8.jar` | no direct CC bytecode reference |
| 125 | `synaxis_patchpack-1.0.0.jar` | CC bytecode reference found |
| 126 | `synaxis-1.5.0.jar` | CC bytecode reference found |
| 127 | `synaxisplus-1.0.5.jar` | no direct CC bytecode reference |
| 128 | `taov_core-0.1.0.jar` | no direct CC bytecode reference |
| 129 | `taov_weapons-0.1.1.jar.disabled` | disabled |
| 130 | `taov_weapons-0.1.1-compat.1.jar` | no direct CC bytecode reference |
| 131 | `tfmg-1.21.1-1.3.2a-community.jar` | no direct CC bytecode reference |
| 132 | `toms-peripherals-1.21-1.3.1.jar` | CC bytecode reference found |
| 133 | `touys-neoforge-1.21.1-1.1.0.jar` | no direct CC bytecode reference |
| 134 | `tracks_plus-1.0.6b7.jar` | no direct CC bytecode reference |
| 135 | `veil-neoforge-1.21.1-4.5.2.jar` | no direct CC bytecode reference |
| 136 | `vestalihy-2.5.6.jar` | no direct CC bytecode reference |
| 137 | `vista-1.21.1-5.5.7-neoforge (1).jar` | CC bytecode reference found |
| 138 | `voicechat-neoforge-1.21.1-2.6.17 (1).jar` | no direct CC bytecode reference |
| 139 | `voxy-0.2.16-beta+1.21.11-optional-mod.jar` | no direct CC bytecode reference |
| 140 | `xaerominimap-neoforge-1.21.1-26.5.0.jar` | no direct CC bytecode reference |
| 141 | `xaeroworldmap-neoforge-1.21.1-1.46.0.jar` | no direct CC bytecode reference |
| 142 | `yet_another_config_lib_v3-3.8.2+1.21.1-neoforge.jar` | no direct CC bytecode reference |
| 143 | `zfastnoise-1.0.13+1.21.1+neoforge.jar` | no direct CC bytecode reference |

## Important next step

Use the dedicated [peripheral catalog](mods/installed-peripherals.md) to separate actual CC methods from generic class references. An audit result alone must **never** be converted into an invented Lua API.
