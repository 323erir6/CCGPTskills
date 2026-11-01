"""Run a bounded scenario on the real NeoForge/Sable dedicated-server stack."""
from __future__ import annotations

import argparse
import configparser
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[2]
HEADLESS_PROJECT = ROOT / "agent/headless"
SERVER_EXCLUSIONS = HEADLESS_PROJECT / "server-excluded-mods.txt"
EXPECTED_COMPONENTS = {
    "net.minecraft": "1.21.1",
    "net.neoforged": "21.1.248",
}
EXPECTED_INSTANCE_NAME = "6.9.3"


def load_scenario(path: Path) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise ValueError("headless scenario schema_version must be 1")
    duration = value.get("duration_ticks", 200)
    sample_every = value.get("sample_every", 1)
    commands = value.get("commands", [])
    if type(duration) is not int or not 1 <= duration <= 12_000:
        raise ValueError("duration_ticks must be between 1 and 12000")
    if type(sample_every) is not int or not 1 <= sample_every <= duration:
        raise ValueError("sample_every must be between 1 and duration_ticks")
    if not isinstance(commands, list) or len(commands) > 100:
        raise ValueError("commands must be a list with at most 100 entries")
    for command in commands:
        if not isinstance(command, dict) or type(command.get("tick")) is not int:
            raise ValueError("every command needs an integer tick")
        text = command.get("command")
        if not isinstance(text, str) or not text or len(text) > 2048 or text.startswith("/"):
            raise ValueError("invalid server command")
        if not 0 <= command["tick"] < duration:
            raise ValueError("command tick must be inside the scenario")
    return value


def read_instance(instance: Path) -> dict:
    instance = Path(instance).resolve()
    metadata_path = instance / "mmc-pack.json"
    instance_config_path = instance / "instance.cfg"
    mods = instance / "minecraft/mods"
    if not metadata_path.is_file() or not instance_config_path.is_file() or not mods.is_dir():
        raise FileNotFoundError("instance must contain instance.cfg, mmc-pack.json and minecraft/mods")
    config = configparser.ConfigParser()
    config.read(instance_config_path, encoding="utf-8")
    instance_name = config.get("General", "name", fallback="")
    if instance_name != EXPECTED_INSTANCE_NAME:
        raise ValueError(f"expected base instance {EXPECTED_INSTANCE_NAME}, found {instance_name!r}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    actual = {item.get("uid"): item.get("version") for item in metadata.get("components", [])}
    for component, expected in EXPECTED_COMPONENTS.items():
        if actual.get(component) != expected:
            raise ValueError(f"expected {component} {expected}, found {actual.get(component)!r}")
    sable = mods / "sable-neoforge-1.21.1-2.0.5.jar"
    if not sable.is_file():
        raise FileNotFoundError(f"missing exact Sable 2.0.5 JAR: {sable}")
    return {"instance": instance, "instance_name": instance_name,
            "minecraft": instance / "minecraft", "mods": mods,
            "components": actual}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mod_manifest(mods: Path, mode: str) -> list[dict]:
    jars = sorted(Path(mods).glob("*.jar"), key=lambda path: path.name.casefold())
    if mode == "minimal":
        jars = [path for path in jars if path.name == "sable-neoforge-1.21.1-2.0.5.jar"]
    else:
        excluded = {line.strip() for line in SERVER_EXCLUSIONS.read_text(encoding="utf-8").splitlines()
                    if line.strip() and not line.lstrip().startswith("#")}
        jars = [path for path in jars if path.name not in excluded]
    return [{"name": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in jars]


def prepare_run(instance: dict, run_dir: Path, *, reuse: bool, world: Path | None = None) -> None:
    run_dir = Path(run_dir).resolve()
    if run_dir.exists() and not reuse:
        raise FileExistsError(f"run directory already exists; pass --reuse-run to keep it: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=True)
    minecraft = instance["minecraft"]
    for name in ("config", "defaultconfigs", "kubejs", "coremods"):
        source = minecraft / name
        target = run_dir / name
        if source.is_dir() and not target.exists():
            shutil.copytree(source, target)
    if world is not None:
        source_world = Path(world).resolve()
        target_world = (run_dir / "sable-headless-world").resolve()
        if not (source_world / "level.dat").is_file():
            raise FileNotFoundError(f"world must contain level.dat: {source_world}")
        if source_world == target_world:
            raise ValueError("source world and isolated target world must be different")
        if target_world.exists() and not reuse:
            raise FileExistsError(f"isolated target world already exists: {target_world}")
        if not target_world.exists():
            shutil.copytree(source_world, target_world)
    (run_dir / "eula.txt").write_text("eula=true\n", encoding="utf-8")
    properties = """allow-flight=true
enable-command-block=true
enable-rcon=false
force-gamemode=true
gamemode=creative
generate-structures=false
level-name=sable-headless-world
level-seed=1
max-players=1
max-tick-time=-1
motd=Sable headless simulation
online-mode=false
server-ip=127.0.0.1
server-port=0
simulation-distance=5
spawn-protection=0
sync-chunk-writes=true
view-distance=5
"""
    (run_dir / "server.properties").write_text(properties, encoding="utf-8")


def tail(path: Path, count: int = 120) -> str:
    if not path.is_file():
        return ""
    return "".join(path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)[-count:])


def run_server(args) -> tuple[int, dict | None, Path]:
    scenario_path = args.scenario.resolve()
    load_scenario(scenario_path)
    instance = read_instance(args.instance)
    run_dir = args.run_dir.resolve()
    prepare_run(instance, run_dir, reuse=args.reuse_run, world=args.world)
    results = run_dir / "agent-results"
    results.mkdir(parents=True, exist_ok=True)
    report_path = results / "headless-report.json"
    if report_path.exists():
        archived = results / f"headless-report-{time.time_ns()}.previous.json"
        report_path.replace(archived)
    manifest = mod_manifest(instance["mods"], args.mode)
    (results / "mod-manifest.json").write_text(
        json.dumps({"schema_version": 1, "mode": args.mode, "mods": manifest}, indent=2) + "\n",
        encoding="utf-8",
    )

    environment = os.environ.copy()
    environment.update({
        "SABLE_MODPACK_DIR": str(instance["mods"]),
        "SABLE_MODS_MODE": args.mode,
        "SABLE_HEADLESS_RUN_DIR": str(run_dir),
        "SABLE_SIM_SCENARIO": str(scenario_path),
        "SABLE_SIM_OUTPUT": str(report_path),
    })
    if args.java_home:
        environment["JAVA_HOME"] = str(args.java_home.resolve())
        environment["PATH"] = str(args.java_home.resolve() / "bin") + os.pathsep + environment.get("PATH", "")

    command = [str(args.gradlew.resolve()), "-p", str(HEADLESS_PROJECT),
               "runServer", "--no-daemon", "--console=plain"]
    log_path = results / "server.log"
    started = time.monotonic()
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        process = subprocess.Popen(command, cwd=ROOT, env=environment, stdout=log,
                                   stderr=subprocess.STDOUT, text=True)
        while process.poll() is None:
            if time.monotonic() - started > args.timeout:
                process.terminate()
                try:
                    process.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
                raise TimeoutError(f"headless server exceeded {args.timeout} seconds; see {log_path}")
            time.sleep(0.25)
    print(tail(log_path), file=sys.stderr)
    log_lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    runtime_errors = [line for line in log_lines if "/ERROR]" in line or "[ERROR]" in line]
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else None
    if report is not None:
        loaded = {item.get("id"): item.get("version") for item in report.get("loaded_mods", [])}
        if loaded.get("sable") != "2.0.5" or loaded.get("neoforge") != "21.1.248":
            raise RuntimeError(f"unexpected loaded runtime versions: {loaded.get('sable')}, {loaded.get('neoforge')}")
    summary = {
        "schema_version": 1,
        "server_exit_code": process.returncode,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "mode": args.mode,
        "mod_jars": len(manifest),
        "report": str(report_path),
        "log": str(log_path),
        "status": report.get("status") if report else "missing_report",
        "runtime_error_count": len(runtime_errors),
        "runtime_errors": runtime_errors[-100:],
    }
    (results / "run-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return process.returncode, report, report_path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path)
    parser.add_argument("--instance", type=Path, required=True,
                        help="ElyPrism instance containing mmc-pack.json and minecraft/mods")
    parser.add_argument("--gradlew", type=Path, required=True,
                        help="an existing Gradle wrapper compatible with this project")
    parser.add_argument("--java-home", type=Path)
    parser.add_argument("--run-dir", type=Path, default=ROOT / "agent-results/headless-run")
    parser.add_argument("--world", type=Path,
                        help="optional existing world save to copy into the isolated server")
    parser.add_argument("--mode", choices=("full", "minimal"), default="full")
    parser.add_argument("--timeout", type=float, default=900)
    parser.add_argument("--reuse-run", action="store_true")
    args = parser.parse_args(argv)
    if args.timeout < 30 or args.timeout > 3600:
        parser.error("--timeout must be between 30 and 3600 seconds")
    try:
        exit_code, report, report_path = run_server(args)
    except Exception as error:
        print(f"HEADLESS SABLE ERROR: {error}", file=sys.stderr)
        return 1
    if exit_code != 0 or report is None:
        print(f"No successful report; expected {report_path}", file=sys.stderr)
        return 1
    print(json.dumps({"status": report.get("status"), "engine": report.get("engine"),
                      "ticks": report.get("ticks_executed"),
                      "maximum_sublevels": report.get("maximum_sublevels"),
                      "report": str(report_path)}, indent=2))
    return 0 if report.get("status") == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
