"""Synthetic binary fixtures cover Create, Photomancy v1 and geometry CCD."""
import gzip
import json
import math
import struct
import tempfile
import unittest
from pathlib import Path
from agent.sim.nbt import loads, NBTError
from agent.sim.schematics import normalize, load, SchematicError
from agent.sim.geometry import Compound, ShapeRegistry, oriented_box, intersects, swept_collision


def tag(name, typ, payload):
    b=name.encode("utf-8")
    return bytes([typ])+struct.pack(">H",len(b))+b+payload


def compound(obj):
    return b"".join(tag(k,v[0],v[1]) for k,v in obj.items())+b"\x00"


def text(v):
    b=v.encode("utf-8")
    return struct.pack(">H",len(b))+b


def listtag(kind,payloads):
    return bytes([kind])+struct.pack(">i",len(payloads))+b"".join(payloads)


def p(x,y,z):
    return listtag(3,[struct.pack(">i",v) for v in (x,y,z)])


def make_create():
    palette=listtag(10,[compound({"Name":(8,text("minecraft:stone"))}),
                        compound({"Name":(8,text("minecraft:oak_slab")),
                                  "Properties":(10,compound({"type":(8,text("top"))}))})])
    blocks=listtag(10,[compound({"pos":(9,p(0,0,0)),"state":(3,struct.pack(">i",0))}),
                       compound({"pos":(9,p(2,0,0)),"state":(3,struct.pack(">i",1)),
                                 "nbt":(10,compound({"Text":(8,text("preserved"))}))})])
    root=compound({"DataVersion":(3,struct.pack(">i",3953)),
                   "size":(9,p(3,1,1)),"palette":(9,palette),"blocks":(9,blocks),
                   "entities":(9,listtag(10,[]))})
    return bytes([10,0,0])+root


def make_sable():
    palette=listtag(10,[compound({"Name":(8,text("minecraft:stone"))})])
    block=compound({"local_pos":(10,compound({"x":(3,struct.pack(">i",5)),
                 "y":(3,struct.pack(">i",2)),"z":(3,struct.pack(">i",-1))})),
                 "palette_id":(3,struct.pack(">i",0)),
                 "block_entity_data_id":(3,struct.pack(">i",0))})
    be=compound({"Custom":(8,text("kept"))})
    entry=compound({"id":(3,struct.pack(">i",1)),
                    "block_palette":(9,palette),"blocks":(9,listtag(10,[block])),
                    "block_entities":(9,listtag(10,[be])),
                    "entities":(9,listtag(10,[])),
                    "relative_pose":(10,compound({"position":(10,compound({"x":(6,struct.pack(">d",1.5))}))})),
                    "blocks_origin":(10,compound({"x":(3,struct.pack(">i",12))})),
                    "extra_data":(10,compound({"fixture":(8,text("extra"))}))})
    root=compound({"version":(3,struct.pack(">i",1)),
                   "sub_levels":(9,listtag(10,[entry])),
                   "global_extra_data":(10,compound({"preserve":(1,b"\x01")}))})
    return bytes([10,0,0])+root


class TestSchematicIO(unittest.TestCase):
    def test_create_gzip_nbt(self):
        fixture=make_create()
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"structure.nbt"
            path.write_bytes(gzip.compress(fixture))
            parsed=load(path)
        self.assertEqual("create_structure_nbt",parsed["format"])
        c=parsed["constructs"][0]
        self.assertEqual(2,len(c["blocks"]))
        self.assertEqual([2,0,0],c["blocks"][1]["pos"])
        self.assertEqual("preserved",c["blocks"][1]["block_entity"]["Text"])
        geom=Compound.from_construct(c)
        self.assertEqual(2,len(geom.primitives))
        self.assertEqual(((2,0.5,0),(3,1,1)),geom.primitives[1][0])

    def test_photomancy_v1_multiple_sublevel_fields(self):
        data=normalize(loads(make_sable()))
        self.assertEqual("sable_photomancy_v1",data["format"])
        sub=data["constructs"][0]
        self.assertEqual([5,2,-1],sub["blocks"][0]["pos"])
        self.assertEqual("kept",sub["blocks"][0]["block_entity"]["Custom"])
        self.assertEqual("extra",sub["sidecar"]["fixture"])
        self.assertEqual(1.5,sub["relative_pose"]["position"]["x"])

    def test_signed_byte_array_and_nbt_numeric_tags(self):
        raw=bytes([10,0,0])+compound({
            "data":(7,struct.pack(">i",4)+bytes([255,0,127,128])),
            "long":(4,struct.pack(">q",-123456789012345))})
        result=loads(raw)
        self.assertEqual([-1,0,127,-128],result["data"])
        self.assertEqual(-123456789012345,result["long"])

    def test_unknown_palette_state_rejected_in_strict_mode(self):
        construct={"palette":[{"name":"mod:missing","properties":{}}],
            "blocks":[{"pos":[0,0,0],"state":0,"unavailable":True}]}
        with self.assertRaisesRegex(ValueError,"unavailable palette state"):
            Compound.from_construct(construct,strict_shapes=True)

    def test_bad_palette_rejected(self):
        data=loads(make_create())
        data["blocks"][0]["state"]=20
        with self.assertRaises(SchematicError):normalize(data)

    def test_nbt_bombs_rejected(self):
        with self.assertRaises(NBTError):loads(gzip.compress(make_create()),max_output=5)
        with self.assertRaises(NBTError):loads(b"\x0a\x00\x00\x09\x00\x01x\x0a\x7f\xff\xff\xff")

    def test_gap_does_not_collide(self):
        a=Compound.from_construct({"palette":[{"name":"minecraft:stone","properties":{}}],
            "blocks":[{"pos":[0,0,0],"state":0},{"pos":[3,0,0],"state":0}]})
        b=Compound.from_construct({"palette":[{"name":"minecraft:stone","properties":{}}],
            "blocks":[{"pos":[0,0,0],"state":0}]})
        self.assertFalse(a.overlap(b,position_b=(1.5,0,0)))
        self.assertTrue(a.overlap(b,position_b=(3,0,0)))

    def test_high_speed_voxel_ccd(self):
        a=Compound.from_construct({"palette":[{"name":"minecraft:stone","properties":{}}],
            "blocks":[{"pos":[0,0,0],"state":0}]})
        b=Compound.from_construct({"palette":[{"name":"minecraft:stone","properties":{}}],
            "blocks":[{"pos":[0,0,0],"state":0}]})
        toi=a.sweep(b,(1000,0,0),0.1,position_b=(40,0,0))
        self.assertIsNotNone(toi)
        self.assertAlmostEqual(.039,toi[0],places=8)

    def test_versioned_shape_registry(self):
        state={"name":"example:thin_plate","properties":{"facing":"north"}}
        construct={"palette":[state],"blocks":[{"pos":[0,1,0],"state":0}]}
        with self.assertRaisesRegex(ValueError,"unresolved Minecraft VoxelShape"):
            Compound.from_construct(construct,strict_shapes=True)
        registry=ShapeRegistry({"schema_version":1,"target":{"minecraft":"1.21.1"},
            "shapes":{"example:thin_plate[facing=north]": [[0,0,0,1,0.125,1]]}})
        exact=Compound.from_construct(construct,registry=registry,strict_shapes=True)
        self.assertEqual([],exact.unresolved)
        self.assertEqual(((0,1,0),(1,1.125,1)),exact.primitives[0][0])

    def test_rotation_slab(self):
        a=oriented_box(((0,0,0),(1,.5,1)),orientation=(math.cos(math.pi/4),0,math.sin(math.pi/4),0))
        self.assertTrue(intersects(a,oriented_box(((0,0,0),(1,1,1)))))
        self.assertFalse(intersects(a,oriented_box(((0,0,0),(1,1,1)),position=(10,0,0))))

if __name__=="__main__":unittest.main()
