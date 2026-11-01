#!/usr/bin/env python3
"""Build a deterministic, self-contained archive for ordinary ChatGPT chats."""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = (
    "chatgpt/en/PROJECT_INSTRUCTIONS.md",
    "chatgpt/uk/QUICKSTART.md",
    "chatgpt/examples/drop_test.json",
    "skills/sable-simulator/references/scenario-schema.md",
    "agent/sim/chat_runner.py",
    "agent/sim/geometry.py",
    "agent/sim/rigid.py",
    "agent/sim/sable205.py",
    "agent/sim/coverage.json",
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
