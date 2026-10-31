"""No-graphics rigid-body harness backed by actual schematic voxel geometry.

Uses individual OBBs for occupied blocks, not sphere proxies. Translation CCD
is continuous for fixed orientation during each time step. Rotation/collisions
between simultaneous rotating bodies remain approximate, not Rapier-equivalent.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from math import ceil, sqrt, exp, isfinite
from .geometry import Compound, Vector, add, sub, mul, dot, norm


def qstep(q:tuple[float,float,float,float],w:Vector,dt:float):
    a,x,y,z=q;wx,wy,wz=w
    qq=(a-.5*dt*(wx*x+wy*y+wz*z),
        x+.5*dt*(wx*a+wy*z-wz*y),
        y+.5*dt*(-wx*z+wy*a+wz*x),
        z+.5*dt*(wx*y-wy*x+wz*a))
    length=sqrt(sum(v*v for v in qq))
    return tuple(v/length for v in qq)


def centroid_inertia(comp:Compound,mass:float):
    """Mass properties of union of collision boxes, uniform density approximation.

    Overlapping blocks within one construct double-count; normal Minecraft
    distinct block locations do not overlap. Modded complex collision geometry
    can overlap and requires a dedicated exact integration step.
    """
    boxes=[b for b,_ in comp.primitives]
    volumes=[(hi[0]-lo[0])*(hi[1]-lo[1])*(hi[2]-lo[2]) for lo,hi in boxes]
    volume=sum(volumes)
    if volume<=0:raise ValueError("no collidable volume; explicit mass geometry required")
    com=tuple(sum(v*(lo[i]+hi[i])*.5 for v,(lo,hi) in zip(volumes,boxes))/volume for i in range(3))
    I=[0.,0.,0.]
    for v,(lo,hi) in zip(volumes,boxes):
        m=mass*v/volume
        dx,dy,dz=(hi[k]-lo[k] for k in range(3))
        cx,cy,cz=((lo[k]+hi[k])*.5-com[k] for k in range(3))
        I[0]+=m*(dy*dy+dz*dz)/12+m*(cy*cy+cz*cz)
        I[1]+=m*(dx*dx+dz*dz)/12+m*(cx*cx+cz*cz)
        I[2]+=m*(dx*dx+dy*dy)/12+m*(cx*cx+cy*cy)
    return com,tuple(I)

@dataclass
class Body:
    id:int
    geometry:Compound
    mass:float
    position:Vector
    velocity:Vector=(0.,0.,0.)
    orientation:tuple=(1.,0.,0.,0.)
    angular_velocity:Vector=(0.,0.,0.)
    damping:float=0.
    restitution:float=0.
    com:Vector=(0.,0.,0.)
    inertia:Vector=(0.,0.,0.)
    persistent_force:Vector=(0.,0.,0.)

    def snapshot(self):
        return {"id":self.id,"position":self.position,"velocity":self.velocity,
                "orientation":self.orientation,"angular_velocity":self.angular_velocity,
                "mass":self.mass,"inertia":self.inertia,"voxel_blocks":self.geometry.blocks,
                "collision_boxes":len(self.geometry.primitives),
                "unresolved_shapes":self.geometry.unresolved}

class World:
    def __init__(self,physics_hz=120,gravity=(0.,-9.81,0.),max_pair_checks=100000):
        if not isinstance(physics_hz,int) or physics_hz<20 or physics_hz>2000 or physics_hz%20:
            raise ValueError("physics_hz must be multiple of 20 between 20 and 2000")
        self.physics_hz=physics_hz
        self.gravity=tuple(gravity)
        self.max_pair_checks=max_pair_checks
        self.bodies:dict[int,Body]={}
        self.tick=0
        self.physics_step=0
        self.time=0.
        self.events=[]
        self.contact_checks=0

    def add(self,geometry:Compound,*,mass=1.,position=(0.,0.,0.),velocity=(0.,0.,0.),
            orientation=(1.,0.,0.,0.),angular_velocity=(0.,0.,0.),damping=0.,restitution=0.):
        if not isfinite(mass) or mass<=0:raise ValueError("positive finite mass required")
        if not isfinite(damping) or damping<0:raise ValueError("invalid damping")
        if not 0<=restitution<=1:raise ValueError("invalid restitution")
        com,inertia=centroid_inertia(geometry,mass)
        id=max(self.bodies.keys(),default=0)+1
        b=Body(id,geometry,mass,tuple(position),tuple(velocity),tuple(orientation),
               tuple(angular_velocity),damping,restitution,com,inertia)
        self.bodies[id]=b
        return id

    def force(self,id:int,f:Vector):
        b=self.bodies[id];b.persistent_force=add(b.persistent_force,tuple(f))

    def impulse(self,id:int,dp:Vector):
        b=self.bodies[id];b.velocity=add(b.velocity,mul(tuple(dp),1/b.mass))

    def advance(self,ticks=1):
        if not isinstance(ticks,int) or ticks<0 or ticks>100000:raise ValueError("invalid tick count")
        dt=1/self.physics_hz
        for _ in range(ticks):
            for substep in range(self.physics_hz//20):
                old_positions={id:b.position for id,b in self.bodies.items()}
                for id,b in self.bodies.items():
                    acceleration=add(self.gravity,mul(b.persistent_force,1/b.mass))
                    velocity=mul(add(b.velocity,mul(acceleration,dt)),exp(-b.damping*dt))
                    b.velocity=velocity
                self._move(dt)
                for b in self.bodies.values():
                    b.orientation=qstep(b.orientation,b.angular_velocity,dt)
                self.time+=dt;self.physics_step+=1
            self.tick+=1
        return self.snapshot()

    def _move(self,dt):
        # EN: Find earliest pairwise translation contact; stop at that time of impact.
        # RU: Ищем первый контакт при поступательном движении, используем время удара.
        ids=sorted(self.bodies)
        checks=0
        earliest=None
        for i in range(len(ids)):
            a=self.bodies[ids[i]]
            for j in range(i+1,len(ids)):
                b=self.bodies[ids[j]]
                checks+=len(a.geometry.primitives)*len(b.geometry.primitives)
                if checks>self.max_pair_checks:
                    raise RuntimeError("collision pair budget exceeded: partition geometry or increase limit")
                relative=sub(a.velocity,b.velocity)
                hit=a.geometry.sweep(b.geometry,relative,dt,
                    position_a=a.position,position_b=b.position,
                    orientation_a=a.orientation,orientation_b=b.orientation,
                    pivot_a=a.com,pivot_b=b.com)
                if hit is not None and (earliest is None or hit[0]<earliest[0]):
                    earliest=(hit[0],a.id,b.id,hit[1])
        self.contact_checks+=checks
        if earliest is None:
            for b in self.bodies.values():b.position=add(b.position,mul(b.velocity,dt))
            return
        time,a_id,b_id,n=earliest
        for b in self.bodies.values():b.position=add(b.position,mul(b.velocity,time))
        a=self.bodies[a_id];b=self.bodies[b_id]
        rv=dot(sub(a.velocity,b.velocity),n)
        if rv<0:
            impulse=-(1+min(a.restitution,b.restitution))*rv/(1/a.mass+1/b.mass)
            a.velocity=add(a.velocity,mul(n,impulse/a.mass))
            b.velocity=sub(b.velocity,mul(n,impulse/b.mass))
        # Not a full iterative contact manifold solver; one contact in a substep.
        remaining=dt-time
        for body in self.bodies.values():body.position=add(body.position,mul(body.velocity,remaining))
        self.events.append({"event":"body_contact","a":a_id,"b":b_id,
                            "normal":n,"time":self.time+time})

    def snapshot(self):
        return {"status":"ok","tick":self.tick,"substep":self.physics_step,
                "time":self.time,"contact_checks":self.contact_checks,
                "events":self.events,"bodies":[self.bodies[k].snapshot() for k in sorted(self.bodies)]}
