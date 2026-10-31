"""Voxel-preserving, rotation-aware block geometry with swept OBB CCD.

Each schematic block is a distinct collision primitive; gaps are never filled by
an enclosing sphere. Collision shapes are exact for full cubic blocks and slabs,
other shapes are explicit approximations requiring a mod-aware shape registry.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import sqrt, floor, inf, isfinite
from itertools import product
from typing import Iterable
import json
from pathlib import Path

Vector=tuple[float,float,float]
Box=tuple[Vector,Vector]


def add(a:Vector,b:Vector)->Vector:return tuple(x+y for x,y in zip(a,b))
def sub(a:Vector,b:Vector)->Vector:return tuple(x-y for x,y in zip(a,b))
def mul(a:Vector,f:float)->Vector:return tuple(x*f for x in a)
def dot(a:Vector,b:Vector)->float:return sum(x*y for x,y in zip(a,b))
def cross(a:Vector,b:Vector)->Vector:return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(a:Vector)->float:return sqrt(dot(a,a))
def unit(a:Vector)->Vector:
    n=norm(a)
    return mul(a,1/n) if n>1e-12 else (0,0,0)


def quaternion_axes(q:tuple[float,float,float,float])->tuple[Vector,Vector,Vector]:
    """Quaternion (w,x,y,z); world axes of the body's local X/Y/Z."""
    w,x,y,z=q; n=sqrt(w*w+x*x+y*y+z*z)
    if n<=1e-12 or not isfinite(n): raise ValueError("invalid quaternion")
    w,x,y,z=w/n,x/n,y/n,z/n
    return ((1-2*(y*y+z*z),2*(x*y+w*z),2*(x*z-w*y)),
            (2*(x*y-w*z),1-2*(x*x+z*z),2*(y*z+w*x)),
            (2*(x*z+w*y),2*(y*z-w*x),1-2*(x*x+y*y)))

@dataclass(frozen=True)
class OBB:
    center: Vector
    axes: tuple[Vector,Vector,Vector]
    extent: Vector


def oriented_box(local:Box, position:Vector=(0,0,0),
                 orientation=(1,0,0,0), pivot:Vector=(0,0,0))->OBB:
    center=tuple((lo+hi)/2 for lo,hi in zip(*local))
    ext=tuple((hi-lo)/2 for lo,hi in zip(*local))
    axes=quaternion_axes(orientation)
    rel=sub(center,pivot)
    return OBB(add(position,tuple(dot(rel,tuple(axes[j][i] for j in range(3))) for i in range(3))),axes,ext)


def _project(box:OBB,axis:Vector)->tuple[float,float]:
    c=dot(box.center,axis)
    r=sum(abs(dot(axis,box.axes[i]))*box.extent[i] for i in range(3))
    return c-r,c+r


def separating_axes(a:OBB,b:OBB):
    for axis in (*a.axes,*b.axes): yield axis
    for x,y in product(a.axes,b.axes):
        c=cross(x,y)
        if dot(c,c)>1e-16: yield unit(c)


def intersects(a:OBB,b:OBB,epsilon:float=1e-9)->bool:
    for axis in separating_axes(a,b):
        alo,ahi=_project(a,axis); blo,bhi=_project(b,axis)
        if ahi < blo-epsilon or bhi < alo-epsilon:return False
    return True


def swept_collision(a:OBB,b:OBB,relative_velocity:Vector,seconds:float)->tuple[float,Vector]|None:
    """Continuous OBB translation with fixed orientations. First impact time+axis."""
    if seconds<0 or not isfinite(seconds):raise ValueError("invalid time")
    enter,leave=0.0,seconds
    normal=None
    for axis in separating_axes(a,b):
        loA,hiA=_project(a,axis); loB,hiB=_project(b,axis)
        v=dot(relative_velocity,axis)
        if abs(v)<1e-13:
            if hiA<loB-1e-9 or hiB<loA-1e-9:return None
            continue
        t0=(loB-hiA)/v;t1=(hiB-loA)/v
        impact_normal=mul(axis,-1 if v>0 else 1)
        if t0>t1:t0,t1=t1,t0
        if t0>enter:enter=t0;normal=impact_normal
        if t1<leave:leave=t1
        if enter>leave+1e-10:return None
    return (max(0,enter),normal or (0,0,0))


def state_key(block_name:str,properties:dict)->str:
    if not properties:return block_name
    return block_name+"["+",".join(f"{k}={properties[k]}" for k in sorted(properties))+"]"

class ShapeRegistry:
    """State-qualified, externally recorded Minecraft VoxelShape boxes.

    Source must be a version-qualified extraction of BlockState#getCollisionShape
    from the actual modpack, not an approximation from rendered models.
    """
    def __init__(self,records:dict):
        if records.get("schema_version")!=1 or not isinstance(records.get("shapes"),dict):
            raise ValueError("invalid collision shape registry")
        self.source=records.get("source", "unknown")
        self.target=records.get("target",{})
        self.shapes={}
        for key, boxes in records["shapes"].items():
            if not isinstance(key,str) or not isinstance(boxes,list):
                raise ValueError("invalid shape registry entry")
            parsed=[]
            for b in boxes:
                if not isinstance(b,list) or len(b)!=6 or not all(isinstance(v,(int,float)) and isfinite(v) for v in b):
                    raise ValueError("invalid shape box coordinates")
                lo,hi=tuple(b[:3]),tuple(b[3:])
                if not all(lo[i]<hi[i] for i in range(3)):
                    raise ValueError("invalid shape bounds")
                parsed.append((lo,hi))
            self.shapes[key]=parsed

    @classmethod
    def from_json(cls,path:Path):return cls(json.loads(Path(path).read_text("utf-8")))

    def lookup(self,name:str,props:dict)->list[Box]|None:
        key=state_key(name,props)
        if key in self.shapes:return self.shapes[key]
        return self.shapes.get(name)


def collision_shape(block_name:str, properties:dict,registry:ShapeRegistry|None=None)->tuple[list[Box],str]:
    """Return shapes plus accuracy: exact_known / conservative / noncollidable_known.

    Name/Properties data survives for every block; unsupported shapes use full
    cubes to avoid false negatives, and always report unresolved accuracy.
    """
    if registry is not None:
        registered=registry.lookup(block_name,properties)
        if registered is not None:return registered,"registry_verified"
    if block_name in ("minecraft:air","minecraft:cave_air","minecraft:void_air"):
        return [],"noncollidable_known"
    if block_name in ("minecraft:water","minecraft:lava"):
        return [],"noncollidable_known"
    if block_name.endswith("_slab") and block_name.startswith("minecraft:"):
        slab=properties.get("type","bottom")
        if slab=="double":return [((0,0,0),(1,1,1))],"exact_known"
        if slab=="top":return [((0,0.5,0),(1,1,1))],"exact_known"
        if slab=="bottom":return [((0,0,0),(1,0.5,1))],"exact_known"
    # Recognize only unambiguous full-block shapes. Others need Minecraft state VoxelShape registry.
    cubic={"minecraft:stone","minecraft:dirt","minecraft:grass_block","minecraft:bedrock",
           "minecraft:iron_block","minecraft:gold_block","minecraft:oak_planks",
           "minecraft:obsidian","minecraft:glass","minecraft:bricks","minecraft:deepslate"}
    if block_name in cubic:return [((0,0,0),(1,1,1))],"exact_known"
    return [((0,0,0),(1,1,1))],"conservative"

@dataclass
class Compound:
    """Exact saved block positions; collision shape per state, not a bounding sphere."""
    primitives:list[tuple[Box,int]]
    unresolved:list[str]
    blocks:int

    @classmethod
    def from_construct(cls, construct:dict,*,registry:ShapeRegistry|None=None,
                       strict_shapes:bool=False)->'Compound':
        primitives=[];unresolved=[]
        palette=construct["palette"]
        for record in construct["blocks"]:
            state=palette[record["state"]]
            name=state["name"]
            if record.get("unavailable"):
                unresolved.append(name+":unavailable_palette")
                if strict_shapes:raise ValueError("unavailable palette state: "+name)
                continue
            props=state.get("properties",{})
            shapes,accuracy=collision_shape(name,props,registry)
            if accuracy=="conservative":
                unresolved.append(state_key(name,props))
                if strict_shapes:
                    raise ValueError("unresolved Minecraft VoxelShape: "+state_key(name,props))
            xyz=record["pos"]
            for lo,hi in shapes:
                primitives.append(((add(tuple(xyz),lo),add(tuple(xyz),hi)),record["state"]))
        return cls(primitives,sorted(set(unresolved)),len(construct["blocks"]))

    def boxes(self, position:Vector=(0,0,0), orientation=(1,0,0,0),
              pivot:Vector=(0,0,0))->list[OBB]:
        return [oriented_box(box,position,orientation,pivot) for box,_ in self.primitives]

    def overlap(self,other:'Compound',position_a=(0,0,0),position_b=(0,0,0),
                orientation_a=(1,0,0,0),orientation_b=(1,0,0,0),
                pivot_a=(0,0,0),pivot_b=(0,0,0))->bool:
        for a in self.boxes(position_a,orientation_a,pivot_a):
            for b in other.boxes(position_b,orientation_b,pivot_b):
                if intersects(a,b):return True
        return False

    def sweep(self,other:'Compound',relative_velocity:Vector,duration:float,
              position_a=(0,0,0),position_b=(0,0,0),
              orientation_a=(1,0,0,0),orientation_b=(1,0,0,0),
              pivot_a=(0,0,0),pivot_b=(0,0,0))->tuple[float,Vector]|None:
        first=None
        for a in self.boxes(position_a,orientation_a,pivot_a):
            for b in other.boxes(position_b,orientation_b,pivot_b):
                collision=swept_collision(a,b,relative_velocity,duration)
                if collision and (first is None or collision[0]<first[0]): first=collision
        return first

    def summary(self)->dict:
        return {"blocks":self.blocks,"collision_boxes":len(self.primitives),
                "unresolved_block_shapes":self.unresolved,
                "geometry":"individual_voxel_collision_boxes_not_bounding_sphere"}
