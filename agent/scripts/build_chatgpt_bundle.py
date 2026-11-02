#!/usr/bin/env python3
"""Build a deterministic, self-contained archive for ordinary ChatGPT chats."""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = (
    "AGENTS.md",
    "agent/AGENTS.md",
    "chatgpt/en/PROJECT_INSTRUCTIONS.md",
    "chatgpt/uk/QUICKSTART.md",
    "chatgpt/examples/drop_test.json",
    "skills/autonomous-minecraft-project/SKILL.md",
    "skills/autonomous-minecraft-project/agents/openai.yaml",
    "skills/autonomous-minecraft-project/references/execution-loop.md",
    "skills/autonomous-minecraft-project/references/schematic-contract.md",
    "skills/autonomous-minecraft-project/references/live-runtime.md",
    "skills/sable-simulator/references/scenario-schema.md",
    "agent/autonomy/project.template.json",
    "agent/autonomy/connections.template.json",
    "agent/scripts/autonomous_project.py",
    "agent/scripts/run_headless_sable.py",
    "agent/sim/schematic_preflight.py",
    "agent/sim/schematics.py",
    "agent/sim/nbt.py",
    "agent/sim/chat_runner.py",
    "agent/sim/geometry.py",
    "agent/sim/rigid.py",
    "agent/sim/sable205.py",
    "agent/sim/coverage.json",
    "agent/headless/build.gradle.kts",
    "agent/headless/gradle.properties",
    "agent/headless/settings.gradle.kts",
    "agent/headless/gradlew",
    "agent/headless/gradlew.bat",
    "agent/headless/gradle/wrapper/gradle-wrapper.jar",
    "agent/headless/gradle/wrapper/gradle-wrapper.properties",
    "agent/headless/server-excluded-mods.txt",
    "agent/headless/scenarios/stone_drop.json",
    "agent/headless/scenarios/computer_probe.json",
    "agent/headless/scenarios/record_existing_world.json",
    "agent/headless/src/main/java/dev/sableheadless/SableHeadlessTelemetry.java",
    "agent/headless/src/main/resources/META-INF/neoforge.mods.toml",
    "agent/docs/en/headless-sable-server.md",
)


def build(output: Path) -> Path:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=9) as archive:
        for relative in FILES:
            source = ROOT / relative
            if not source.is_file():
                raise FileNotFoundError(source)
            info = zipfile.ZipInfo(relative, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes())
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "dist/sable-chatgpt-bundle.zip")
    args = parser.parse_args(argv)
    result = build(args.output)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
