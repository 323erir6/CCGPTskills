"""Text-only JNI bridge to the ACTUAL Sable 2.0.5 packaged Rapier native binary.

Only trusted local schematics/scripts. The Java scene runs Rapier's native
rigid-body AND custom voxel-contact solver; module behaviors are modeled by
Python adapters, so this is not full Minecraft engine equivalence.

Do not ship upstream native libraries in this repository. Extract from the
user-owned Sable JAR at runtime, honoring original notices/licensing.
"""
from __future__ import annotations
import argparse
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile
from dataclasses import dataclass
from typing import Iterable

SABLE_NAME = 'sable-neoforge-1.21.1-2.0.5.jar'
NESTED_JAR = 'META-INF/jarjar/dev.ryanhcode.sable.sable-sable_rapier-1.21.1-2.0.5.jar'
BINARIES_NAME = 'natives/sable_rapier/sable_rapier_binaries.zip.l4z'
NATIVE_NAME = 'sable_rapier_x86_64_linux.so'


def extract_native(jar: Path, dest: Path) -> Path:
    """Extract only selected native binary; reject unexpected archive contents."""
    try:
        import lz4.frame
    except ImportError as exc:
        raise RuntimeError('lz4 is required: python -m pip install lz4') from exc
    jar = Path(jar)
    if not jar.is_file() or jar.name != SABLE_NAME:
        raise FileNotFoundError(f'expected modpack Sable jar {SABLE_NAME}: {jar}')
    with ZipFile(jar) as z:
        inner = z.read(NESTED_JAR)
    with ZipFile(io.BytesIO(inner)) as z:
        packed = z.read(BINARIES_NAME)
    # Maximum decompressed size to guard against corrupt / malicious files
    decompressed = lz4.frame.decompress(packed)
    if len(decompressed) > 100_000_000:
        raise ValueError('Native archive too large')
    import platform
    arch = platform.machine().lower()
    if arch not in ('x86_64', 'amd64'):
        raise OSError('Currently supported architecture: x86_64')
    platform_file = {'Linux': 'sable_rapier_x86_64_linux.so',
                     'Windows': 'sable_rapier_x86_64_windows.dll',
                     'Darwin': 'sable_rapier_x86_64_macos.dylib'}.get(platform.system())
    if platform_file is None:
        raise OSError('Unsupported operating system: ' + platform.system())
    with ZipFile(io.BytesIO(decompressed)) as z:
        entry = z.getinfo(platform_file)
        if entry.file_size > 20_000_000:
            raise ValueError('Native library too large')
        blob = z.read(entry)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(blob)
    return dest


class NativeScene:
    """One JNI process with line-oriented stdin/output, original Sable engine."""

    def __init__(self, jar: Path, workdir: Path | None = None):
        import platform
        if platform.machine().lower() not in ('x86_64', 'amd64'):
            raise OSError('Only x86_64 native binaries are supported')
        self.root = Path(__file__).resolve().parents[1]
        cache = Path(workdir or self.root / 'native' / 'build')
        cache.mkdir(parents=True, exist_ok=True)
        source = self.root / 'native' / 'src'
        java = sorted(str(x) for x in source.rglob('*.java'))
        if not java:
            raise RuntimeError(f'JNI bridge source missing in {source}')
        subprocess.run(['javac', '-encoding', 'UTF-8', '-d', str(cache), *java], check=True, timeout=60)
        import platform
        suffix = {'Linux': '.so', 'Windows': '.dll', 'Darwin': '.dylib'}[platform.system()]
        library = cache / ('libsable_rapier' + suffix)
        extract_native(jar, library)
        self.process = subprocess.Popen(
            ['java', '-Xmx512m', '-cp', str(cache), 'NativeHarness'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1, env={**os.environ, 'SABLE_NATIVE_LIB': str(library)},
        )
        self.materials = {}
        self.initialized = False

    def cmd(self, *args):
        if self.process.poll() is not None:
            raise RuntimeError(f'JNI runner stopped: {self.process.returncode}')
        self.process.stdin.write(' '.join(str(x) for x in args) + '\n')
        self.process.stdin.flush()
        for _ in range(30):
            line = self.process.stdout.readline()
            if not line:
                raise RuntimeError('JNI runner closed stdout unexpectedly')
            line = line.strip()
            if line.startswith('ERROR '):
                raise RuntimeError('JNI bridge: ' + line)
            if line.startswith(('OK ', 'STATE ', 'CONTACTS ')):
                return line
        raise RuntimeError('Too much unexpected native output')

    def init(self, gravity=(0.0, -11.0, 0.0), drag=0.09):
        self.cmd('INIT', *gravity, drag)
        self.initialized = True

    def material(self, name: str, mu=1.0, shapes=((0, 0, 0, 1, 1, 1),)):
        if name in self.materials:
            return self.materials[name]
        response = self.cmd('MATERIAL', mu)
        index = int(response.rsplit(' ', 1)[-1])
        for shape in shapes:
            self.cmd('SHAPE', index, *shape)
        self.materials[name] = index
        return index

    def ship(self, ship_id, position, quat, mass, com, inertia, bounds, blocks):
        self.cmd('SHIP', ship_id, *position, *quat, mass, *com, *inertia, *bounds)
        for x, y, z, matid in blocks:
            self.cmd('BLOCK', ship_id, x, y, z, matid)
        self.cmd('LOAD', ship_id)

    def box(self, id_, mass, half_extents, pose):
        self.cmd('BOX', id_, mass, *half_extents, *pose)

    def ground(self, surface_y, x, z, radius=2, material=None):
        cx = math.floor(x / 16)
        cz = math.floor(z / 16)
        if material is None:
            if not self.materials: raise ValueError('create the terrain material before ground')
            material = next(iter(self.materials.values()))
        self.cmd('GROUND', int(surface_y), cx, cz, radius, material)

    def impulse(self, ship_id, linear, angular=(0, 0, 0)):
        self.cmd('IMPULSE', ship_id, *linear, *angular)

    def step(self, dt):
        self.cmd('STEP', dt)

    def collisions(self):
        data = self.cmd('COLLISIONS').split()
        size = int(data[1])
        values = [float(x) for x in data[2:]]
        if len(values) != size:
            raise RuntimeError('Truncated native contact buffer')
        return [values[i:i + 15] for i in range(0, size, 15)]

    def state(self, ship_id):
        r = self.cmd('STATE', ship_id).split()
        if len(r) != 14:
            raise RuntimeError(f'Bad state: {r}')
        v = [float(x) for x in r[1:]]
        return {'position': v[:3], 'quat': v[3:7], 'velocity': v[7:10], 'omega': v[10:13]}

    def close(self):
        if self.process.poll() is None:
            try:
                self.cmd('CLOSE')
            finally:
                self.process.stdin.close()
                self.process.wait(timeout=10)
        errors = self.process.stderr.read()[-4000:] if self.process.returncode != 0 else ''
        self.process.stdout.close()
        self.process.stderr.close()
        if self.process.returncode != 0:
            raise RuntimeError(f'JNI bridge exited {self.process.returncode}: {errors}')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            self.close()
        except Exception:
            if exc_type is None:
                raise


def sublevel_box_regression(jar: Path) -> dict:
    """Actual Sable custom voxel body colliding with actual main-level voxel ground."""
    with NativeScene(jar) as scene:
        scene.init()
        box = scene.material('minecraft:grass_block')
        scene.ground(168, 0, 0, radius=1)
        scene.ship(1, (5.5, 175, 5.5), (0, 0, 0, 1), 4.5,
                   (0.5, 0.5, 0.5), (.75, .75, .75),
                   (0, 0, 0, 0, 0, 0), [(0, 0, 0, box)])
        for i in range(160):
            scene.step(1 / 40)
        state = scene.state(1)
        if abs(state['position'][1] - 168.5) > .03:
            raise AssertionError(f'Native voxel ground contact failed: {state}')
        return state


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--jar', type=Path, required=True, help='Sable 2.0.5 JAR from the modpack')
    p.add_argument('--smoke', action='store_true', help='Test actual native voxel collision')
    p.add_argument('--output', type=Path, help='JSON report path')
    args = p.parse_args(argv)
    if not args.smoke:
        p.error('Specify --smoke; exact rocket scenario integration is not yet validated')
    state = sublevel_box_regression(args.jar)
    report = {'engine': 'original Sable 2.0.5 Rapier binary via JNI',
              'test': 'one voxel sublevel against world voxel layer at Y=167',
              'native_contact': 'verified', 'state': state}
    content = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content + '\n', 'utf-8')
    print(content)


if __name__ == '__main__':
    main()
