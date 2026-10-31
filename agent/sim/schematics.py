"""Create structure and Photomancy v1 NBT -> conservative lossless geometry JSON.

Preserves block states, entities, BE NBT, and Photomancy per-sublevel metadata.
Geometry positions are block-local, not world-local Sable plot indices.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from .nbt import loads, NBTError

class SchematicError(ValueError): pass


def _pos(value: Any, label: str) -> list[int]:
    if isinstance(value, dict):
        xyz = [value.get(k) for k in ("x","y","z")]
    elif isinstance(value, list) and len(value)==3:
        xyz = value
    else: raise SchematicError(f"{label} is not a 3-coordinate vector")
    if not all(type(v) is int and -30_000_000 <= v <= 30_000_000 for v in xyz):
        raise SchematicError(f"{label} contains invalid block coordinate")
    return xyz


def _palette(raw: Any) -> list[dict]:
    if not isinstance(raw,list): raise SchematicError("missing NBT palette")
    result=[]
    for i, entry in enumerate(raw):
        if not isinstance(entry,dict) or not isinstance(entry.get("Name"),str):
            raise SchematicError(f"invalid palette entry #{i}")
        props=entry.get("Properties",{})
        if not isinstance(props,dict): raise SchematicError("palette Properties not compound")
        result.append({"name":entry["Name"],"properties":props})
    return result


def _blocks(blocks: Any, palette: list[dict], style: str,
            block_entities: list[dict] | None = None, unavailable: set[int] | None = None) -> list[dict]:
    if not isinstance(blocks,list): raise SchematicError("missing NBT blocks list")
    result=[];seen=set(); unavailable=unavailable or set()
    for i, record in enumerate(blocks):
        if not isinstance(record,dict): raise SchematicError("block record not compound")
        loc=_pos(record.get("pos") if style=="create" else record.get("local_pos"), f"block #{i}")
        idx=record.get("state" if style=="create" else "palette_id")
        if type(idx) is not int or not 0<=idx<len(palette):
            raise SchematicError(f"palette index out of range in block #{i}")
        if tuple(loc) in seen: raise SchematicError("duplicate schematic block position")
        seen.add(tuple(loc))
        nbt=record.get("nbt") if style=="create" else None
        if style=="sable":
            be=record.get("block_entity_data_id",-1)
            if type(be) is not int or be < -1 or be >= len(block_entities or []):
                raise SchematicError(f"invalid block entity reference in block #{i}")
            if be>=0: nbt=block_entities[be]
        if nbt is not None and not isinstance(nbt,dict):
            raise SchematicError("block entity NBT not compound")
        result.append({"pos":loc,"state":idx, "block_entity":nbt,
                       "unavailable":idx in unavailable})
    return result


def _aabb_from_blocks(blocks: list[dict]) -> dict:
    if not blocks: return {"min":[0,0,0],"max":[0,0,0]}
    return {"min":[min(b["pos"][i] for b in blocks) for i in range(3)],
            "max":[max(b["pos"][i] for b in blocks)+1 for i in range(3)]}


def normalize(root: dict) -> dict:
    # EN: File extensions do not identify format. Use root NBT keys.
    # RU: Расширение не определяет формат. Проверяем ключи NBT.
    if "sub_levels" in root and "version" in root:
        if root.get("version") != 1:
            raise SchematicError("unsupported Photomancy blueprint version")
        sublevels=root.get("sub_levels")
        if not isinstance(sublevels,list): raise SchematicError("sub_levels must be list")
        constructs=[]
        for i,sub in enumerate(sublevels):
            if not isinstance(sub,dict): raise SchematicError("sublevel is not a compound")
            if "plot" in sub: raise SchematicError("legacy plot payload unsupported by Photomancy v1")
            palette=_palette(sub.get("block_palette"))
            be=sub.get("block_entities",[])
            if not isinstance(be,list): raise SchematicError("block_entities must be list")
            unavailable=set(sub.get("unavailable_palette_ids",[]))
            blocks=_blocks(sub.get("blocks"),palette,"sable",be,unavailable)
            constructs.append({"id":sub.get("id",i),"name":sub.get("name"),
                "palette":palette,"blocks":blocks,"aabb":_aabb_from_blocks(blocks),
                "local_bounds":sub.get("local_bounds"),"anchor_bounds":sub.get("anchor_bounds"),
                "blocks_origin":sub.get("blocks_origin"),
                "relative_pose":sub.get("relative_pose"),
                "source_uuid":sub.get("source_uuid"),"entities":sub.get("entities",[]),
                "sidecar":sub.get("extra_data",{}),
                "unknown_shapes":[]})
        return {"schema_version":1,"format":"sable_photomancy_v1",
            "constructs":constructs,"origin":root.get("origin"),
            "bounds":root.get("canonical_bound",root.get("root_bounds")),
            "global_extra_data":root.get("global_extra_data",{}),"preview":root.get("preview")}
    if "size" in root and "palette" in root and "blocks" in root:
        size=_pos(root["size"],"size")
        if not all(v>0 for v in size): raise SchematicError("size must be positive")
        pal=_palette(root["palette"])
        blocks=_blocks(root["blocks"],pal,"create")
        for b in blocks:
            if not all(0<=b["pos"][i]<size[i] for i in range(3)):
                raise SchematicError("block position outside schematic size")
        return {"schema_version":1,"format":"create_structure_nbt",
            "data_version":root.get("DataVersion"),"size":size,
            "constructs":[{"id":0,"name":None,"palette":pal,"blocks":blocks,
                           "aabb":_aabb_from_blocks(blocks),"entities":root.get("entities",[]),
                           "sidecar":{},"unknown_shapes":[]}]}
    raise SchematicError("unsupported schematic: expected Create structure palette/blocks or Photomancy v1 sub_levels")


def load(path: Path, *, max_bytes: int = 64*1024*1024) -> dict:
    path=Path(path)
    if path.stat().st_size > max_bytes: raise SchematicError("schematic file exceeds configured limit")
    try: return normalize(loads(path.read_bytes(),max_output=max_bytes))
    except NBTError as exc: raise SchematicError(str(exc)) from exc


def convert(source: Path,target:Path) -> dict:
    data=load(source)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
    return data
