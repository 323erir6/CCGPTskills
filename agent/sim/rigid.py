"""No-graphics rigid-body harness backed by actual schematic voxel geometry.

Uses individual OBBs for occupied blocks, not sphere proxies. Translation CCD
is continuous for fixed orientation during each time step. Rotation/collisions
between simultaneous rotating bodies remain approximate, not Rapier-equivalent.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite, sqrt
from .sable205 import Sable205, damp
from .geometry import Compound, Vector, add, cross, dot, mul, quaternion_axes, sub


def qstep(q:tuple[float,float,float,float],w:Vector,dt:float):
    a,x,y,z=q;wx,wy,wz=w
    qq=(a-.5*dt*(wx*x+wy*y+wz*z),
        x+.5*dt*(wx*a+wy*z-wz*y),
        y+.5*dt*(-wx*z+wy*a+wz*x),
        z+.5*dt*(wx*y-wy*x+wz*a))
    length=sqrt(sum(v*v for v in qq))
    if length <= 1e-15 or not isfinite(length):
        raise ValueError("invalid quaternion integration result")
    return tuple(v/length for v in qq)


def _finite_vector(value, length, label):
    if not isinstance(value, (tuple, list)) or len(value) != length:
        raise ValueError(f"{label} must contain {length} finite numbers")
    if not all(type(item) in (int, float) and isfinite(item) for item in value):
        raise ValueError(f"{label} must contain {length} finite numbers")
    return tuple(float(item) for item in value)


def _unit_quaternion(value):
    quaternion = _finite_vector(value, 4, "orientation")
    magnitude = sqrt(sum(item * item for item in quaternion))
    if magnitude <= 1e-12:
        raise ValueError("orientation quaternion must be nonzero")
    return tuple(item / magnitude for item in quaternion)


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
    static:bool=False

    def snapshot(self):
        return {"id":self.id,"position":self.position,"velocity":self.velocity,
                "orientation":self.orientation,"angular_velocity":self.angular_velocity,
                "mass":self.mass,"inertia":self.inertia,"static":self.static,"voxel_blocks":self.geometry.blocks,
                "collision_boxes":len(self.geometry.primitives),
                "unresolved_shapes":self.geometry.unresolved}

class World:
    def __init__(self,physics_hz=None,gravity=None,max_pair_checks=100000,ground_y=None,
                 ground_friction=None,profile=None,max_events=50000):
        if profile is not None and profile != "sable-2.0.5":
            raise ValueError("unknown simulation profile")
        exact = Sable205() if profile else None
        physics_hz = physics_hz if physics_hz is not None else exact.physics_hz if exact else 120
        gravity = gravity if gravity is not None else exact.gravity if exact else (0.,-9.81,0.)
        ground_friction = ground_friction if ground_friction is not None else exact.contact_friction if exact else 0.5
        self.profile = profile
        self.default_damping = exact.universal_drag if exact else 0.0
        if type(physics_hz) is not int or physics_hz<20 or physics_hz>2000 or physics_hz%20:
            raise ValueError("physics_hz must be multiple of 20 between 20 and 2000")
        gravity = _finite_vector(gravity, 3, "gravity")
        if type(max_pair_checks) is not int or max_pair_checks < 1 or max_pair_checks > 100_000_000:
            raise ValueError("max_pair_checks must be between 1 and 100000000")
        self.physics_hz=physics_hz
        self.gravity=gravity
        self.max_pair_checks=max_pair_checks
        self.bodies:dict[int,Body]={}
        self.tick=0
        self.physics_step=0
        self.time=0.
        self.events=[]
        if type(max_events) is not int or max_events < 1 or max_events > 1_000_000:
            raise ValueError("max_events must be between 1 and 1000000")
        self.max_events=max_events
        self.events_dropped=0
        self.contact_checks=0
        self._contact_pairs=set()
        if ground_y is not None and (type(ground_y) not in (int, float) or not isfinite(ground_y)):
            raise ValueError("invalid ground height")
        if type(ground_friction) not in (int, float) or not isfinite(ground_friction) or ground_friction<0:
            raise ValueError("invalid ground friction")
        self.ground_y=None if ground_y is None else float(ground_y)
        self.ground_friction=float(ground_friction)
        self._grounded_ids=set()
        self.physics_callbacks=[]  # (world, dt) -> per-substep forces from mod actors
        self._transient_forces={}
        self._transient_torques={}
        self.force_log=[]

    def _record_event(self,event):
        if len(self.events) < self.max_events:
            self.events.append(event)
        else:
            self.events_dropped += 1

    def add(self,geometry:Compound,*,mass=1.,position=(0.,0.,0.),velocity=(0.,0.,0.),
            orientation=(1.,0.,0.,0.),angular_velocity=(0.,0.,0.),damping=None,restitution=0.,static=False):
        damping = self.default_damping if damping is None else damping
        if type(mass) not in (int, float) or not isfinite(mass) or mass<=0:
            raise ValueError("positive finite mass required")
        if type(damping) not in (int, float) or not isfinite(damping) or damping<0:
            raise ValueError("invalid damping")
        if type(restitution) not in (int, float) or not isfinite(restitution) or not 0<=restitution<=1:
            raise ValueError("invalid restitution")
        if type(static) is not bool:
            raise ValueError("static must be a boolean")
        position = _finite_vector(position, 3, "position")
        velocity = _finite_vector(velocity, 3, "velocity")
        orientation = _unit_quaternion(orientation)
        angular_velocity = _finite_vector(angular_velocity, 3, "angular_velocity")
        com,inertia=centroid_inertia(geometry,mass)
        id=max(self.bodies.keys(),default=0)+1
        b=Body(id,geometry,float(mass),position,velocity,orientation,
               angular_velocity,float(damping),float(restitution),com,inertia,
               static=static)
        self.bodies[id]=b
        return id

    def force(self,id:int,f:Vector):
        b=self.bodies[id]
        if b.static:raise ValueError("cannot accelerate static body")
        b.persistent_force=add(b.persistent_force,_finite_vector(f,3,"force"))

    def impulse(self,id:int,dp:Vector):
        b=self.bodies[id]
        if b.static:raise ValueError("cannot impulse static body")
        b.velocity=add(b.velocity,mul(_finite_vector(dp,3,"impulse"),1/b.mass))

    def step_force(self,id:int,f:Vector,*,world_point:Vector|None=None,source:str="mod"):
        """Queue a force for this physics substep, and torque about physical COM.

        World-frame force and world-frame application point; moments use
        the *rotated* schematic center of mass. Not a native Rapier solver.
        """
        body=self.bodies[id]
        if body.static:raise ValueError("cannot force a static body")
        force=_finite_vector(f,3,"force")
        self._transient_forces[id]=add(self._transient_forces.get(id,(0.,0.,0.)),force)
        if world_point is not None:
            world_point=_finite_vector(world_point,3,"application point")
            # Position is center of mass in this model; local geometry is
            # translated by -com to calculate point positions.
            torque=cross(sub(tuple(world_point),body.position),force)
            self._transient_torques[id]=add(self._transient_torques.get(id,(0.,0.,0.)),torque)
        if len(self.force_log)<50000:
            self.force_log.append({"tick":self.tick,"substep":self.physics_step,
                                   "body":id,"force":force,"point":world_point,
                                   "source":source})

    def step_torque(self,id:int,torque:Vector,*,source="mod"):
        body=self.bodies[id]
        if body.static:raise ValueError("cannot torque a static body")
        force=_finite_vector(torque,3,"torque")
        self._transient_torques[id]=add(self._transient_torques.get(id,(0.,0.,0.)),force)
        if len(self.force_log)<50000:
            self.force_log.append({"tick":self.tick,"substep":self.physics_step,
                                   "body":id,"torque":force,"source":source})

    def add_physics_callback(self,callback):
        if not callable(callback):raise TypeError("physics callback must be callable")
        self.physics_callbacks.append(callback)

    def advance(self,ticks=1):
        if not isinstance(ticks,int) or ticks<0 or ticks>100000:raise ValueError("invalid tick count")
        dt=1/self.physics_hz
        for _ in range(ticks):
            for substep in range(self.physics_hz//20):
                self._transient_forces={}
                self._transient_torques={}
                for callback in tuple(self.physics_callbacks):callback(self,dt)
                for id,b in self.bodies.items():
                    if b.static:continue
                    total_force=add(b.persistent_force,self._transient_forces.get(id,(0.,0.,0.)))
                    acceleration=add(self.gravity,mul(total_force,1/b.mass))
                    b.velocity=add(b.velocity,mul(acceleration,dt))
                    torque=self._transient_torques.get(id,(0.,0.,0.))
                    # Approximate diagonal inertia in the body's local frame.
                    axes=quaternion_axes(b.orientation)
                    local_torque=tuple(dot(torque,axis) for axis in axes)
                    local_alpha=tuple(local_torque[i]/b.inertia[i] if b.inertia[i]>1e-12 else 0.
                                      for i in range(3))
                    alpha=tuple(sum(axes[j][i]*local_alpha[j] for j in range(3)) for i in range(3))
                    b.angular_velocity=add(b.angular_velocity,mul(alpha,dt))
                self._move(dt)
                self._resolve_flat_ground(dt)
                for b in self.bodies.values():
                    if b.static:continue
                    b.velocity=tuple(damp(v,b.damping,dt) for v in b.velocity)
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
                if a.static and b.static:continue
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
            self._contact_pairs.clear()
            for b in self.bodies.values():
                if not b.static:b.position=add(b.position,mul(b.velocity,dt))
            return
        time,a_id,b_id,n=earliest
        for b in self.bodies.values():
            if not b.static:b.position=add(b.position,mul(b.velocity,time))
        a=self.bodies[a_id];b=self.bodies[b_id]
        rv=dot(sub(a.velocity,b.velocity),n)
        if rv<0:
            inv_a=0. if a.static else 1./a.mass
            inv_b=0. if b.static else 1./b.mass
            impulse=-(1+min(a.restitution,b.restitution))*rv/(inv_a+inv_b)
            if not a.static:a.velocity=add(a.velocity,mul(n,impulse*inv_a))
            if not b.static:b.velocity=sub(b.velocity,mul(n,impulse*inv_b))
        # Not a full iterative contact manifold solver; one contact in a substep.
        remaining=dt-time
        for body in self.bodies.values():
            if not body.static:body.position=add(body.position,mul(body.velocity,remaining))
        pair=(a_id,b_id)
        if pair not in self._contact_pairs:
            self._record_event({"event":"body_contact","a":a_id,"b":b_id,
                                "normal":n,"time":self.time+time})
        self._contact_pairs={pair}

    def _resolve_flat_ground(self,dt):
        """Approximate infinite superflat surface using each body's rotated voxel shape.

        Ground collision is exact for a stationary full-cube contact plane, but
        tangential Coulomb friction is an engineering approximation, not Rapier.
        """
        if self.ground_y is None:return
        grounded=set()
        for body in self.bodies.values():
            if body.static:continue
            boxes=body.geometry.boxes(body.position,body.orientation,pivot=body.com)
            if not boxes:continue
            bottom=min(box.center[1]-sum(abs(box.axes[j][1])*box.extent[j]
                        for j in range(3)) for box in boxes)
            if bottom>self.ground_y+1e-8:continue
            body.position=(body.position[0],body.position[1]+max(0,self.ground_y-bottom),body.position[2])
            if body.velocity[1]<0:
                body.velocity=(body.velocity[0],0.,body.velocity[2])
            # Dry friction: tangential speed is reduced by mu * normal_acceleration * dt.
            # The actual Sable/Rapier manifold solver includes angular impulses and sleep.
            vx,vy,vz=body.velocity
            horizontal=sqrt(vx*vx+vz*vz)
            normal_acceleration=max(0.,-self.gravity[1])
            reduction=self.ground_friction*normal_acceleration*dt
            if horizontal>0 and reduction>0:
                scale=max(0.,horizontal-reduction)/horizontal
                body.velocity=(vx*scale,vy,vz*scale)
            grounded.add(body.id)
            if body.id not in self._grounded_ids:
                self._record_event({"event":"terrain_contact","body":body.id,
                                    "ground_y":self.ground_y,"time":self.time+dt})
        self._grounded_ids=grounded

    def snapshot(self):
        return {"status":"ok","tick":self.tick,"substep":self.physics_step,
                "time":self.time,"contact_checks":self.contact_checks,
                "events":[dict(event) for event in self.events],
                "events_dropped":self.events_dropped,
                "bodies":[self.bodies[k].snapshot() for k in sorted(self.bodies)]}
