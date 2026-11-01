"""Generate a Minecraft Create structure-template NBT, *not* an assembled Sable ship.

All construction blocks are copied from installed 1.21.1 mod registry names.
No modded block-entity NBT or loaded fuel is fabricated. Mod-side assembly,
computer startup and physical commissioning must be performed in Minecraft.
"""
from __future__ import annotations
import argparse
import gzip
import json
import struct
from pathlib import Path

# Big-endian named-tag NBT (Java), tag type numbers: Compound=10, List=9,
# String=8, Int=3, IntArray=11. No dependencies.
def name_bytes(name):
    data=name.encode('utf-8')
    if len(data)>65535:raise ValueError('name too long')
    return struct.pack('>H',len(data))+data

def tag(t,name,body):return bytes([t])+name_bytes(name)+body

def t_int(name,n):return tag(3,name,struct.pack('>i',n))
def t_str(name,s):return tag(8,name,name_bytes(s))
def t_arr(name,vals):return tag(11,name,struct.pack('>i',len(vals))+b''.join(struct.pack('>i',v) for v in vals))
def t_comp(name,contents):return tag(10,name,b''.join(contents)+b'\0')
def t_list_comp(name,items):return tag(9,name,b'\x0a'+struct.pack('>i',len(items))+b''.join(b''.join(t)+b'\0' for t in items))


def create_layout():
    """Inert flight-test airframe, forward axis +Z, four symmetric thrusters."""
    blocks=[]
    def put(x,y,z,name,props=None):
        if any(b['pos']==[x,y,z] for b in blocks):raise ValueError('duplicate block')
        blocks.append({'pos':[x,y,z],'name':name,'properties':props or {}})
    for z in range(1,15):put(2,2,z,'create:andesite_casing')
    for x,y in [(1,1),(1,3),(3,1),(3,3)]:
        put(x,y,0,'createpropulsion:solid_fuel_thruster',{'facing':'south'})
    for x,y,facing in [(0,2,"west"),(4,2,"east"),(2,0,"down"),(2,4,"up")]:
        put(x,y,2,'synaxis:compact_flap',{"facing":facing,"axis_along_first":"false","invisible":"false","offset_mode":"0"})
    put(2,2,15,'create:andesite_casing')
    # One CC computer for onboard Lua; peripheral wiring and a radio modem
    # require in-game configuration, not speculative saved block entity NBT.
    # Replace center casing, preserving non-overlap.
    blocks=[b for b in blocks if b['pos']!=[2,2,7]]
    put(2,2,7,'computercraft:computer_advanced',{'state':'off','facing':'south'})
    blocks=[b for b in blocks if b['pos']!=[2,2,6]]
    put(2,2,6,'sable_autonomous_chunk_loader:autonomous_chunk_loader',{'active':'false'})
    return blocks


def build_nbt(blocks):
    size=(5,5,16)
    palette=[];mapping={}
    block_entries=[]
    for b in sorted(blocks,key=lambda x:(x['pos'][2],x['pos'][1],x['pos'][0])):
        state=(b['name'],tuple(sorted(b['properties'].items())))
        if state not in mapping:
            mapping[state]=len(palette);palette.append(state)
        block_entries.append([t_arr('pos',b['pos']),t_int('state',mapping[state])])
    palette_entries=[]
    for name,properties in palette:
        tags=[t_str('Name',name)]
        if properties:tags.append(t_comp('Properties',[t_str(k,v) for k,v in properties]))
        palette_entries.append(tags)
    # Based on the exact Create structure NBT schema (size/palette/blocks).
    root=[t_arr('size',size),t_list_comp('palette',palette_entries),t_list_comp('blocks',block_entries),t_list_comp('entities',[]),t_int('DataVersion',3955)]
    return gzip.compress(t_comp('',root),mtime=0)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',default='agent/projects/osprey/schematics/OSPREY_Create.nbt')
    parser.add_argument('--layout',default='agent/projects/osprey/schematics/layout.json')
    args=parser.parse_args()
    blocks=create_layout()
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(build_nbt(blocks))
    layout=Path(args.layout);layout.parent.mkdir(parents=True,exist_ok=True)
    layout.write_text(json.dumps({'name':'OSPREY Flight Test','forward_local':'+Z','blocks':blocks,'size':[5,5,16], 'notes':['requires Sable physics assembly in-game','thruster fuel is not populated by NBT','fin physical assembly and orientation need calibration','no payload or detonation']},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'path':str(out),'blocks':len(blocks),'bytes':out.stat().st_size}))
if __name__=='__main__':main()
