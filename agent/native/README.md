# Sable 2.0.5 native JNI bridge for GOCODE

This package is an **overlay** for the existing GOCODE branch. Extract it at
its repository root (keeping `agent/native`, `agent/sim`, `agent/tests`, and
`agent/docs`). No original Sable binary is redistributed.

## Requirements

- Minecraft 1.21.1 NeoForge: `sable-neoforge-1.21.1-2.0.5.jar`
- JDK 21 (`java` and `javac` on PATH)
- Python 3.11+ with packages from `agent/native/requirements.txt`
- Python simulator's existing `agent/sim/schematics.py` and `agent/sim/nbt.py`

## Usage (Windows PowerShell)

```powershell
py -m pip install -r agent/native/requirements.txt
py -m agent.sim.native_rapier --jar "C:\Minecraft\mods\sable-neoforge-1.21.1-2.0.5.jar" --smoke --output agent-results/native-smoke.json
py -m agent.sim.native_rocket "rszo_rocket_v0.nbt" --jar "C:\Minecraft\mods\sable-neoforge-1.21.1-2.0.5.jar" --max-seconds 60 --out agent-results/native-rocket.json
```

The bridge extracts the correct native library automatically. Output is JSON.
It runs **the actual unmodified Sable native solver**, but the rocket's force
providers and VoxelShape/state loading still need live-game verification.
See `agent/docs/en/native-sable-rapier.md` and the Russian counterpart.

The library is only loaded from a mod JAR you trust. Do not execute unknown
NBT-supplied Lua or Java code.
