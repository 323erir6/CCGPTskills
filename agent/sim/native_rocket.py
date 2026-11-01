"""Best-effort no-render rocket replay with the REAL Sable 2.0.5 native solver.

The solver (rigid body, angular response, contacts, sleeping) is original Sable.
The Rocket/Sail mod forcing, server configuration, block VoxelShapes, payload
mass and chunk schedule are NOT yet authenticated against full Minecraft runtime.
Output remains a model estimate, never claim exact in-game impact.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation

from .native_rapier import NativeScene
from .schematics import load

DT=1/40
G=11.
BURN=800.
THRUST=230.
SURFACE=168.
MASS=4.5
PARALLEL=1.75
DIRECTIONLESS=.06888202261
COM=np.array([.5,.5,3.])
BLOCK_LOCAL=np.array([[.5,.5,float(z)+.5] for z in range(6)])
SAILS=((np.array([.5,.5,2.5]),np.array([0.,1.,0.])),
       (np.array([.5,.5,3.5]),np.array([1.,0.,0.])))


def air_pressure(y, sea_level=63, min_y=-64, max_y=320):
    """Version-matched Sable DimensionPhysics.createDefault Bezier evaluation."""
    slope=-.004
    maxp=1.5
    base=max(min_y,math.log(maxp)/slope+sea_level)
    smooth=max_y-40
    pts=[]
    alt=base
    while True:
        p=math.exp(slope*(alt-sea_level))
        pts.append((alt,p,p*slope))
        if alt<sea_level and alt+200>=sea_level: alt=sea_level
        elif alt<smooth and alt+200>=smooth:alt=smooth
        elif alt>=smooth:break
        else:alt+=200
    last=pts[-1][1]
    pts.append((max_y,0.,-2*last/(max_y-smooth)))
    if y<pts[0][0]:return pts[0][1]
    if y>=pts[-1][0]:return 0.
    for (x0,y0,s0),(x1,y1,s1) in zip(pts,pts[1:]):
        if x0<=y<x1:
            L=x1-x0;t=(y-x0)/L;delta=y1-y0
            a=(s0+s1)*L-2*delta
            b=3*delta-(2*s0+s1)*L
            return max(0.,((a*t+b)*t+L*s0)*t+y0)
    return 0.


def lowest_y(position,rotation):
    coords=np.array([[float(x)-.5,float(y)-.5,float(z)-3.]
                    for x in (0,1) for y in (0,1) for z in (0,6)])
    return float(position[1]+np.min(rotation.apply(coords)[:,1]))


def forces(state,t,dt=DT):
    q=np.array(state['quat'])
    rot=Rotation.from_quat(q)
    position=np.array(state['position'])
    vel=np.array(state['velocity'])
    w=np.array(state['omega'])
    # Launch at 45 degrees from +Z with engine pushing toward +Z.
    accel=THRUST*min(1.0,max(0.0,t)/.5) if t<BURN else 0.
    impulse_local=np.array([0.,0.,accel*dt])
    torque_local=np.zeros(3)
    for point,normal in SAILS:
        offset=point-COM
        world_offset=rot.apply(offset)
        vpoint=vel+np.cross(w,world_offset)
        vlocal=rot.inv().apply(vpoint)
        pressure=air_pressure(position[1]+world_offset[1])
        # Source: Sable BlockSubLevelLiftProvider, drag force subtracts (normal and directionless terms).
        drag=-(normal*np.dot(normal,vlocal)*PARALLEL+vlocal*DIRECTIONLESS)*pressure*dt
        impulse_local+=drag
        torque_local+=np.cross(offset,drag)
    return impulse_local,torque_local


def simulate(nbt:Path,jar:Path,*,max_seconds=180.,trace_every_seconds=2.5):
    content=load(nbt)
    if len(content['constructs'])!=1:raise ValueError('requires exactly one sublevel')
    c=content['constructs'][0]
    if len(c['blocks'])!=6:raise ValueError('unexpected rocket geometry: expected six blocks')
    names=[c['palette'][b['state']]['name'] for b in c['blocks']]
    if names.count('createpropulsion:solid_fuel_thruster')!=1:
        raise ValueError('solid-fuel thruster not found')
    q=Rotation.from_euler('x',-45,degrees=True)
    local_corners=np.array([[x-.5,y-.5,z-3] for x in (0.,1.) for y in (0.,1.) for z in (0.,6.)])
    minimum=np.min(q.apply(local_corners)[:,1])
    pos=np.array([0.,SURFACE+6.-minimum,0.])
    inertia=(13.875,13.875,.75) # uniform six cubes, MASS=4.5; assumption
    trace=[];flight_result=None;loaded_center=None
    with NativeScene(jar) as scene:
        scene.init()
        material=scene.material('full_block')
        scene.ground(SURFACE,0,0,radius=3)
        scene.ship(1,pos.tolist(),q.as_quat().tolist(),MASS,COM,inertia,(0,0,0,0,0,5),
                   [(int(b['pos'][0]),int(b['pos'][1]),int(b['pos'][2]),material)
                    for b in c['blocks']])
        limit=int(max_seconds/DT)
        prev=None
        for i in range(limit):
            now=i*DT
            state=scene.state(1)
            px,py,pz=state['position']
            vy=state['velocity'][1]
            rot=Rotation.from_quat(state['quat'])
            btm=lowest_y(np.array(state['position']),rot)
            # Only stream terrain where first contact becomes plausible.
            if py<250 and (i==0 or vy<0):
                center=(math.floor(px/16),math.floor(pz/16))
                if center!=loaded_center:
                    scene.ground(SURFACE,px,pz,radius=3)
                    loaded_center=center
            impulse,torque=forces(state,now)
            if not np.isfinite(impulse).all() or not np.isfinite(torque).all():
                raise ArithmeticError(f'non-finite force at {now}')
            if max(np.linalg.norm(impulse),np.linalg.norm(torque))>0:
                scene.impulse(1,impulse,torque)
            scene.step(DT)
            contacts=scene.collisions()
            state_after=scene.state(1)
            after_bottom=lowest_y(np.array(state_after['position']),Rotation.from_quat(state_after['quat']))
            if i%max(1,round(trace_every_seconds/DT))==0:
                trace.append({'t':round((i+1)*DT,3),
                              'position':[round(v,5) for v in state_after['position']],
                              'velocity':[round(v,5) for v in state_after['velocity']],
                              'omega':[round(v,5) for v in state_after['omega']],
                              'bottom_y':round(after_bottom,5)})
            impact_contacts=[item for item in contacts if set((item[0],item[1]))=={-1.,1.}]
            if impact_contacts:
                flight_result={'kind':'native_sable_contact_event', 't':round((i+1)*DT,4),
                               'state':state_after,'bottom_y':after_bottom,
                               'native_contact_count':len(impact_contacts),
                               'native_first_contact':impact_contacts[0]}
                break
            if i>4 and after_bottom<SURFACE-2.0 and vy<0:
                flight_result={'kind':'contact_missing_tunneled_through_terrain',
                               't':round((i+1)*DT,4),'state':state_after,
                               'bottom_y':after_bottom}
                break
        if flight_result is None:
            flight_result={'kind':'no_impact_within_limit','t':max_seconds,'state':state_after,
                           'bottom_y':after_bottom}
    return {'engine':'unmodified Sable 2.0.5 JNI native Rapier, custom voxel collider',
            'input':str(nbt),'native_solver':'verified','rocket_mod_force_model':'approximate',
            'geometry':'six full voxel cubes, schematic block coordinates exact; shapes unverified',
            'surface_y':SURFACE,'initial_position':pos.tolist(),
            'burn_seconds':BURN,'mass_assumed':MASS,
            'impact':flight_result,'trace':trace,
            'fidelity_notes':['native Rapier solver, CCD, contacts, quaternion dynamics',
                              'approximate sail orientations/drag forces',
                              'mod server config and all per-block VoxelShapes not verified',
                              'fuel startup logic and chunk loader not executed in Minecraft VM']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('nbt',type=Path)
    parser.add_argument('--jar',required=True,type=Path)
    parser.add_argument('--max-seconds',type=float,default=180)
    parser.add_argument('--out',type=Path,required=True)
    a=parser.parse_args()
    result=simulate(a.nbt,a.jar,max_seconds=a.max_seconds)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'impact':result['impact'],'engine':result['engine']},ensure_ascii=False))

if __name__=='__main__':main()
