"""Connect real NBT functional block states to the deterministic physics solver.

No graphics, no native Minecraft class loading, strict unsupported-feature reporting.
"""
from __future__ import annotations
from dataclasses import dataclass,field
from math import isfinite
from .rigid import World
from .geometry import Compound
from .mod_devices import DEVICE_FACTORIES, FunctionalDevice, PropulsionThruster, AeronauticsPropeller


class DeviceError(RuntimeError):pass


class ModRuntime:
    def __init__(self, world: World | None = None, *, air_pressure=1.0):
        self.world = world or World(profile="sable-2.0.5")
        if not isinstance(air_pressure,(float,int)) or not isfinite(air_pressure) or air_pressure<0:
            raise ValueError("invalid air pressure")
        self.air_pressure=float(air_pressure)
        self.devices:dict[str,FunctionalDevice] = {}
        self.unresolved:set[str] = set()
        self.events:list[dict] = []
        self.world.add_physics_callback(self._physics_step)

    def add_device(self, key: str, block_id: str, body_id: int,
                   block_pos=(0,0,0), properties=None, config=None):
        if key in self.devices:raise ValueError("duplicate device key: "+key)
        if body_id not in self.world.bodies:raise ValueError("invalid rigid body reference")
        if block_id not in DEVICE_FACTORIES:
            self.unresolved.add(f"{key}: unsupported functional block {block_id}")
            return None
        cls,defaults=DEVICE_FACTORIES[block_id]
        opts={**defaults,**(config or {})}
        device=cls(key=key,block_id=block_id,body_id=body_id,
                   block_pos=tuple(block_pos),properties=dict(properties or {}),**opts)
        self.devices[key]=device
        self.events.append({"event":"device_attach","key":key,"block":block_id})
        return device

    def load_construct(self,construct:dict,*,mass=None,position=(0.,0.,0.),
                       velocity=(0.,0.,0.),device_config=None,strict_shapes=False,
                       registry=None)->int:
        geo=Compound.from_construct(construct,strict_shapes=strict_shapes,registry=registry)
        if not geo.primitives:raise DeviceError("construction has no collision geometry")
        if geo.unresolved:self.unresolved.add(f"geometry unresolved: {','.join(geo.unresolved)}")
        if mass is None:
            mass=float(max(1,geo.blocks))
            self.unresolved.add("mass inferred from block count; load actual Sable block mass properties")
        body_id=self.world.add(geo,mass=mass,position=position,velocity=velocity)
        counts={}
        for block in construct["blocks"]:
            entry=construct["palette"][block["state"]]
            name=entry["name"]
            if name in DEVICE_FACTORIES:
                base=f"body{body_id}:{name}@{','.join(map(str,block['pos']))}"
                n=counts.get(base,0);counts[base]=n+1
                key=base if n==0 else base+f"#{n}"
                config=(device_config or {}).get(key,(device_config or {}).get(name,{}))
                device=self.add_device(key,name,body_id,block["pos"],
                                        entry.get("properties"),config)
                if block.get("block_entity"):
                    self.unresolved.add(key+": raw BlockEntity NBT preserved, mod-specific decode not implemented")
            elif ":" in name and not name.startswith("minecraft:"):
                self.unresolved.add(f"block {name}: collision supported if shape known; behavior not implemented")
        return body_id

    def load_schematic(self,data:dict,*,masses=None,origins=None,device_config=None,
                       strict_shapes=False,registry=None):
        if not isinstance(data.get("constructs"),list):raise ValueError("normalized schematic required")
        result=[]
        for i,entry in enumerate(data["constructs"]):
            id=self.load_construct(entry,
                mass=(masses or {}).get(str(i)),
                position=(origins or {}).get(str(i),(0.,0.,0.)),
                device_config=device_config,strict_shapes=strict_shapes,registry=registry)
            result.append(id)
        return result

    def _physics_step(self,world,dt):
        for key in sorted(self.devices):
            device=self.devices[key]
            device.physics_step(self,dt)

    def advance(self,ticks=1):
        if not isinstance(ticks,int) or ticks<0 or ticks>100000:
            raise ValueError("tick count outside supported range")
        for _ in range(ticks):
            for key in sorted(self.devices):self.devices[key].tick(self)
            self.world.advance(1)
        return self.snapshot()

    def call(self,key,method,*args):
        device=self.devices.get(key)
        if device is None:raise DeviceError("unknown device: "+str(key))
        response=device.call(method,*args)
        self.events.append({"event":"peripheral_call","tick":self.world.tick,
                            "key":key,"method":method,"args":list(args),"result":response})
        return response

    def attach_computer(self,key):
        device=self.devices[key]
        if not isinstance(device,PropulsionThruster):raise DeviceError("not a propulsion thruster")
        device.attach()
        self.events.append({"event":"computer_attach","key":key,"tick":self.world.tick})

    def detach_computer(self,key):
        device=self.devices[key]
        if not isinstance(device,PropulsionThruster):raise DeviceError("not a propulsion thruster")
        device.detach()
        self.events.append({"event":"computer_detach","key":key,"tick":self.world.tick})

    def redstone(self,key,signal):
        dev=self.devices[key]
        if not isinstance(dev,PropulsionThruster):raise DeviceError("redstone throttle not simulated for this device")
        dev.set_redstone(signal)
        self.events.append({"event":"redstone","key":key,"level":signal,"tick":self.world.tick})

    def set_kinetic_rpm(self,key,rpm):
        dev=self.devices[key]
        if not isinstance(dev,AeronauticsPropeller):raise DeviceError("not an Aeronautics propeller")
        dev.set_rpm(rpm)
        self.events.append({"event":"kinetic_rpm","key":key,"rpm":rpm,"tick":self.world.tick})

    def snapshot(self):
        return {"schema_version":1,"runner":"gocode-mod-devices",
                "world":self.world.snapshot(),
                "devices":[self.devices[k].snapshot() for k in sorted(self.devices)],
                "unresolved":sorted(self.unresolved),"events":list(self.events),
                "integrations":{"physics":"sable_2.0.5_scalar+approximate_contact",
                                "blocks":"source_checked_peripheral_methods_and_selected_force_models"}}
