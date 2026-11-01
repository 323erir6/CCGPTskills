"""Version-specific, JAR-verified source facts for a six-block Photomancy rocket.

Contains extracted numerical/voxel facts, NOT a replacement for Minecraft's
BlockState runtime or Sable/Rapier. Never silently upgrade source assumptions.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
import hashlib
import json
import math
import re
import subprocess
import zipfile

# Shape bounds copied from Block.box(double[6]) operands in installed JAR's
# `ThrusterShapes.<clinit>`; verified each run against its bytecode constants.
# Units in JAR are sixteenths of a block.
SOLID_THRUSTER_BASE_NORTH = (
    (4, 4, 0, 12, 12, 1),
    (0, 0, 0, 16, 16, 8),
    (2, 2, 8, 14, 14, 10),
    (0, 0, 10, 16, 16, 13),
    (0, 0, 13, 16, 16, 16),
)
# Important: actually FIVE boxes, not four. `ShapeBuilder.add` calls 5 times.
# Y-axis default for SimBlockShapes.SYMMETRIC_SAIL.
SAIL_BASE_Y = ((0, 6, 0, 16, 10, 16),)
# ProjectileBlock.makeShapes() baseline Y (AllShapes.Builder.forDirectional).
HE_SHELL_BASE_Y = ((3, 0, 3, 13, 16, 13),)

# Bytecode class with expected jar identity and class names.
SOURCE_CLASSES = {
    'propulsion': ('dev.propulsionteam.propulsionsimulated.content.thruster.ThrusterShapes',
                   'dev.propulsionteam.propulsionsimulated.content.thruster.solid_fuel_thruster.SolidFuelThrusterBlockEntity',
                   'dev.propulsionteam.propulsionsimulated.content.thruster.ThrusterForceProvider'),
    'sail': ('dev.simulated_team.simulated.index.SimBlockShapes',
             'dev.simulated_team.simulated.content.blocks.symmetric_sail.SymmetricSailBlock'),
    'cbc': ('rbasamoyai.createbigcannons.munitions.big_cannon.ProjectileBlock',),
}


def _javap(jar: Path, cls: str) -> str:
    return subprocess.run(['javap', '-classpath', str(jar), '-p', '-c', cls],
                          text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          check=True, timeout=40).stdout


def _between(label: str, text: str, start: str, end: str) -> str:
    a=text.find(start)
    b=text.find(end,a+len(start))
    if a<0 or b<0:raise ValueError(f'JAR did not match expected bytecode section: {label}')
    return text[a:b]


def _parse_shape_boxes(fragment: str, method_marker: str) -> list[list[float]]:
    """Reads the 6 numeric load operands immediately preceding shape() or Block.box()."""
    stack=[]; boxes=[]
    for line in fragment.splitlines():
        # Only constant loads affect the short operand windows.
        m=re.search(r':\s+(?:ldc2_w\s+#\d+\s+//\s+double\s+(-?\d+(?:\.\d+)?)(?:[dD])?|dconst_([01])|iconst_([0-5]))', line)
        if m:
            value=next(v for v in m.groups() if v is not None)
            stack.append(float(value));continue
        if method_marker in line:
            if len(stack)<6:raise ValueError('Not enough operands for Block.box')
            box=stack[-6:];stack=[]
            if not all(0<=n<=16 for n in box) or not all(box[i]<box[i+3] for i in range(3)):
                raise ValueError(f'Invalid static box {box!r}')
            boxes.append(box)
        elif 'putstatic' in line:
            stack=[]
    return boxes


def _shape_from_sail(jar: Path):
    s=_javap(jar,SOURCE_CLASSES['sail'][0]); section=_between('sail',s,'  static {};','putstatic     #57')
    # Isolate only final shape before SYMMETRIC_SAIL assignment: dconst_0,6,0,16,10,16
    section=section[section.rfind('69: dconst_0'):]
    b=_parse_shape_boxes(section,'Method shape:(DDDDDD)')
    if not b or tuple(b[-1])!=SAIL_BASE_Y[0]:raise ValueError('Sail shape differs from pinned version')
    return b[-1:]


def _shape_from_thruster(jar: Path):
    s=_javap(jar,SOURCE_CLASSES['propulsion'][0]);section=_between('thruster',s,'252: invokestatic','360: putstatic')
    boxes=_parse_shape_boxes(section,'Method net/minecraft/world/level/block/Block.box:')
    expected=[list(map(float,box)) for box in SOLID_THRUSTER_BASE_NORTH]
    if boxes!=expected:raise ValueError(f'Thruster shape changed: {boxes}')
    return boxes


def _shape_from_shell(jar: Path):
    s=_javap(jar,SOURCE_CLASSES['cbc'][0]);section=_between('shell',s,'  protected net.createmod.catnip.math.VoxelShaper makeShapes();','  public net.minecraft.world.level.block.state.BlockState getStateForPlacement')
    b=_parse_shape_boxes(section,'Method box:(DDDDDD)')
    if b!=[list(map(float,HE_SHELL_BASE_Y[0]))]:raise ValueError(f'Shell shape changed: {b}')
    return b


def orient_box(box, kind:str, orientation:str):
    """Rotate box to a block axis/direction around (8,8,8) (Minecraft voxel units).

    For north-to-south rotation use X/Z reflection, y unchanged. For Y-axis
    slab to X/Z-axis, swap thickness axis with X/Z. CBC orientation maps Y to
    +/-horizontal; boxes are symmetric, so sign does not matter for this shape.
    """
    x0,y0,z0,x1,y1,z1=box
    if kind=='thruster':
        if orientation=='north':return list(box)
        if orientation=='south':return [16-x1,y0,16-z1,16-x0,y1,16-z0]
        if orientation=='east':return [16-z1,y0,x0,16-z0,y1,x1]
        if orientation=='west':return [z0,y0,16-x1,z1,y1,16-x0]
        if orientation=='up':return [x0,z0,16-y1,x1,z1,16-y0]
        if orientation=='down':return [x0,16-z1,y0,x1,16-z0,y1]
    if kind=='sail':
        if orientation=='y':return list(box)
        if orientation=='x':return [y0,x0,z0,y1,x1,z1]
        if orientation=='z':return [x0,z0,y0,x1,z1,y1]
    if kind=='shell':
        if orientation in ('up','down'):return list(box)
        if orientation in ('north','south'):return [x0,z0,y0,x1,z1,y1]
        if orientation in ('east','west'):return [z0,y0,x0,z1,y1,x1]
    raise ValueError('Unsupported orientation '+kind+'='+orientation)


def shape_for_block(block:dict, source:dict) -> tuple[list[list[float]]|None,str]:
    """Returns state-specific boxes normalized to block space, or unknown.

    Actual Minecraft getCollisionShape dynamic overrides must still be verified;
    returns explicitly 'bytecode_voxel_outline' for source-backed static cases.
    """
    name=block['name'];props=block.get('properties',{})
    if name=='createpropulsion:solid_fuel_thruster':
        return [[v/16 for v in orient_box(b,'thruster',props['facing'])]
                for b in source['shapes']['thruster_north']], 'bytecode_voxel_outline'
    if name.endswith('_symmetric_sail') and name.startswith('simulated:'):
        return [[v/16 for v in orient_box(b,'sail',props['axis'])]
                for b in source['shapes']['sail_y']], 'bytecode_voxel_outline'
    if name=='createbigcannons:he_shell':
        return [[v/16 for v in orient_box(b,'shell',props['facing'])]
                for b in source['shapes']['shell_up']], 'bytecode_voxel_outline'
    return None,'unverified'


def audit_sources(jars:Mapping[str,Path])->dict:
    for name in SOURCE_CLASSES:
        if name not in jars or not Path(jars[name]).is_file():
            raise FileNotFoundError('Missing source JAR: '+name)
    read_paths={k:Path(v) for k,v in jars.items()}
    ident={k:{'name':v.name,'sha256':hashlib.sha256(v.read_bytes()).hexdigest()}
           for k,v in read_paths.items()}
    with zipfile.ZipFile(read_paths['propulsion']) as archive:
        fuel=json.loads(archive.read('data/createpropulsion/solid_thruster_fuels/minecraft/coal_block.json'))
    if fuel.get('burn_ticks') != 16000 or fuel.get('thrust_multiplier') != 1.15:
        raise ValueError('Installed fuel settings differ from expected')
    solid=_javap(read_paths['propulsion'],SOURCE_CLASSES['propulsion'][1]);force=_javap(read_paths['propulsion'],SOURCE_CLASSES['propulsion'][2])
    for marker in ('Method getEffectiveThrustPercentage:()F','Method calculateAtmosphericFactor:()D','Method getThrustUnitsPerKn:()D'):
        if marker not in solid:raise ValueError('Missing thrust logic: '+marker)
    if 'Method dev/propulsionteam/propulsionsimulated/content/thruster/AbstractThrusterBlockEntity.getCurrentThrust:()F' not in force:
        raise ValueError('Unexpected thrust force sample bytecode')
    return {'schema_version':1,'provenance':'JAR + javap bytecode, version-specific',
            'jars':ident,'shapes':{'thruster_north':_shape_from_thruster(read_paths['propulsion']),
                                'sail_y':_shape_from_sail(read_paths['sail']),
                                'shell_up':_shape_from_shell(read_paths['cbc'])},
            'fuel':fuel,
            'constants':{'solid_base_thrust':200,'startup_ticks':10,'thrust_units_per_kn':1000,
                         'nozzle_offset_applied_by_force_provider':0.45,
                         'solid_nozzle_offset_for_particle_placement':0.75,
                         'unobstructed_scan_blocks_in_schematic':10,
                         'use_atmospheric_pressure_default':False,
                         'sail_parallel_drag':1.75,'sail_directionless_drag':0.068882026,
                         'sail_lift':0.0,
                         'sable_gravity':-11,'sable_universal_drag':0.09,
                         'sable_physics_hz':40},
            'limitations':['getCollisionShape vs outline may differ for runtime state',
                           'additional shell fuze, autonomous chunk loading and CC logic not executed',
                           'MassTracker needs all active datapacks + tags + registered blocks',
                           'JAR values can be overridden by world/server configs and datapacks']}


def save_audit(report:dict,path:Path):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
