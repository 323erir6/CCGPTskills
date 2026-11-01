"""Audit exact installed rocket-mod JAR bytecode, resources and NBT.

Outputs source-derived geometry, fuel, provenance and explicitly unresolved facts.
This is static inspection, not execution of Minecraft mod BlockEntity logic.
"""
from __future__ import annotations
import argparse
import json
import hashlib
from pathlib import Path
from agent.sim.schematics import load
from agent.sim.rocket_source_profile import audit_sources, shape_for_block, save_audit


def inspect(nbt, jars):
    info = load(Path(nbt))
    profile = audit_sources(jars)
    sublevels = []
    for sub in info['constructs']:
        blocks = []
        for rec in sub['blocks']:
            state = sub['palette'][rec['state']]
            shape, confidence = shape_for_block(state, profile)
            be = rec.get('block_entity') or {}
            block={'pos':rec['pos'],'block':state['name'],
                   'properties':state.get('properties',{}),'shape':shape,
                   'shape_confidence':confidence,'source':'installed jar bytecode'}
            if state['name']=='createpropulsion:solid_fuel_thruster':
                block['fuel']={
                    'inventory':be.get('Inventory'),
                    'burn_ticks_saved':be.get('BurnTime'),
                    'control_mode_saved':be.get('ControlMode'),
                    'redstone_saved':be.get('RedstoneInput'),
                    'digital_input_saved':be.get('DigitalInput'),
                    'thrust_saved':be.get('Thrust'),
                    'startup_ticks_saved':be.get('StartupTicks'),
                    'obstruction_clearance_saved':be.get('emptyBlocks')}
            if 'IntactReferenceMass' in be:
                block['intact_reference_mass_saved']=be['IntactReferenceMass']
            blocks.append(block)
        sublevels.append({'id':sub.get('id'),'block_count':len(blocks),
                          'blocks':blocks,'relative_pose':sub.get('relative_pose')})
    return {'source_facts':profile,'schematic':str(Path(nbt).name),
            'schematic_sha256':hashlib.sha256(Path(nbt).read_bytes()).hexdigest(),
            'sublevels':sublevels,
            'not_reproduced':['runtime blockstate collision overrides','all active datapack overrides',
                              'exact mass per state from active tags','in-game computer code and redstone events',
                              'fuze and explosion','server-loaded chunk scheduling']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('nbt',type=Path)
    parser.add_argument('--propulsion-jar',required=True,type=Path)
    parser.add_argument('--sail-jar',required=True,type=Path,
                        help='Nested simulated JAR in bundled Create Aeronautics')
    parser.add_argument('--cbc-jar',required=True,type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    report=inspect(args.nbt,{
        'propulsion':args.propulsion_jar,
        'sail':args.sail_jar,
        'cbc':args.cbc_jar})
    save_audit(report,args.out)
    print(json.dumps({'verified_voxel_shapes':sum(b['shape'] is not None for c in report['sublevels'] for b in c['blocks']),
                      'total_blocks':sum(c['block_count'] for c in report['sublevels']),
                      'unverified_voxel_shapes':[b['block'] for c in report['sublevels'] for b in c['blocks'] if b['shape'] is None],
                      'output':str(args.out)},ensure_ascii=False))

if __name__=='__main__':main()
