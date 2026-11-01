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
from .rocket_source_profile import audit_sources, shape_for_block
from .rocket_mass_registry import MassRegistry
from .rocket_mass_tracker import mass_properties

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


def forces(state,t,dt=DT,com=COM):
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
        offset=point-com
        world_offset=rot.apply(offset)
        vpoint=vel+np.cross(w,world_offset)
        vlocal=rot.inv().apply(vpoint)
        pressure=air_pressure(position[1]+world_offset[1])
        # Source: Sable BlockSubLevelLiftProvider, drag force subtracts (normal and directionless terms).
        drag=-(normal*np.dot(normal,vlocal)*PARALLEL+vlocal*DIRECTIONLESS)*pressure*dt
        impulse_local+=drag
        torque_local+=np.cross(offset,drag)
    return impulse_local,torque_local


def simulate(nbt:Path,jar:Path,*,max_seconds=180.,trace_every_seconds=2.5,
             source_jars:dict|None=None, strict_shapes:bool=False, ignite_at:float=0.0,
             mass_jars:dict|None=None):
    content=load(nbt)
    if len(content['constructs'])!=1:raise ValueError('requires exactly one sublevel')
    c=content['constructs'][0]
    if len(c['blocks'])!=6:raise ValueError('unexpected rocket geometry: expected six blocks')
    names=[c['palette'][b['state']]['name'] for b in c['blocks']]
    if names.count('createpropulsion:solid_fuel_thruster')!=1:
        raise ValueError('solid-fuel thruster not found')
    source=audit_sources(source_jars) if source_jars else None
    shape_records={}
    unresolved=[]
    for b in c['blocks']:
        state=c['palette'][b['state']]
        shape,origin=shape_for_block(state,source) if source else (None,'no_jar_audit')
        if shape is None:
            unresolved.append({'name':state['name'],'pos':b['pos'],'reason':origin})
            if strict_shapes:raise ValueError('Unverified native voxel shape '+state['name'])
            shape=[[0,0,0,1,1,1]]
        shape_records[tuple(b['pos'])]=(state['name'],state.get('properties',{}),shape,origin)
    # Validate the saved fuel and reference mass; do not invent server-side state.
    thruster=next(b for b in c['blocks'] if c['palette'][b['state']]['name']=='createpropulsion:solid_fuel_thruster')
    thruster_nbt=thruster.get('block_entity') or {}
    fuel_items=(thruster_nbt.get('Inventory') or {}).get('Items',[])
    if len(fuel_items)!=1 or fuel_items[0].get('id')!='minecraft:coal_block':
        raise ValueError('Saved thruster does not contain one coal block')
    if thruster_nbt.get('BurnTime')!=16000:
        raise ValueError('Saved fuel burn ticks differ from requested 13m20s')
    chunk_loader=next((b.get('block_entity') or {} for b in c['blocks']
        if c['palette'][b['state']]['name']=='sable_autonomous_chunk_loader:autonomous_chunk_loader'), {})
    measured_mass=chunk_loader.get('IntactReferenceMass')
    if measured_mass is not None and abs(float(measured_mass)-MASS)>1e-6:
        raise ValueError('Reference mass differs; update mass properties before running')
    # Source-derived state mass is used when modpack JAR resources are supplied.
    mass_audit=None
    if mass_jars:
        registry=MassRegistry(mass_jars)
        mass_audit=registry.report(c)
        if measured_mass is not None and abs(mass_audit['total_mass']-measured_mass)>1e-5:
            raise ValueError('Sable tag mass does not match saved reference mass')
        masses=[]
        for b,record in zip(c['blocks'],mass_audit['blocks']):
            xyz=tuple(b['pos'])
            shape=shape_records[xyz][2]
            # Sable MassTracker BLOCK_CENTER_OF_MASS uses the collision shape
            # bounding box center, clipped to unit block bounds.
            mins=[min(box[i] for box in shape) for i in range(3)]
            maxs=[max(box[i+3] for box in shape) for i in range(3)]
            center=tuple((max(0.,mins[i])+min(1.,maxs[i]))/2 for i in range(3))
            masses.append({'pos':xyz,'mass':record['mass'],'local_center':center})
        source_mass_properties=mass_properties(masses)
        mass=source_mass_properties['mass']
        com=np.array(source_mass_properties['center_of_mass'])
        inertia=tuple(source_mass_properties['inertia_diagonal'])
        if source_mass_properties['off_diagonal_present']:
            raise ValueError('Native ship bridge currently needs diagonal inertia; full tensor required')
    else:
        source_mass_properties=None
        mass=MASS
        com=COM.copy()
        inertia=(13.875,13.875,.75)
    q=Rotation.from_euler('x',-45,degrees=True)
    # Lowest collision point uses per-state bytecode-derived voxel boxes, not
    # a fictitious full 1x1x6 prism. Unresolved blocks are clearly reported.
    local_corners=[]
    for b in c['blocks']:
        boxes=shape_records[tuple(b['pos'])][2]
        for x0,y0,z0,x1,y1,z1 in boxes:
            for x in (x0,x1):
                for y in (y0,y1):
                    for z in (z0,z1):
                        local_corners.append((b['pos'][0]+x-com[0],b['pos'][1]+y-com[1],b['pos'][2]+z-com[2]))
    local_corners=np.array(local_corners)
    minimum=np.min(q.apply(local_corners)[:,1])
    pos=np.array([0.,SURFACE+6.-minimum,0.])
    trace=[];flight_result=None;loaded_center=None
    with NativeScene(jar) as scene:
        scene.init()
        ground_material=scene.material('world_grass',shapes=((0,0,0,1,1,1),))
        scene.ground(SURFACE,0,0,radius=3,material=ground_material)
        blocks=[]
        for b in c['blocks']:
            pblock=tuple(b['pos'])
            name,properties,shape,provenance=shape_records[pblock]
            key=name+':'+','.join(f'{k}={v}' for k,v in sorted(properties.items()))
            mat=scene.material(key,shapes=tuple(map(tuple,shape)))
            blocks.append((*pblock,mat))
        scene.ship(1,pos.tolist(),q.as_quat().tolist(),mass,com,inertia,(0,0,0,0,0,5),blocks)
        limit=int(max_seconds/DT)
        prev=None
        for i in range(limit):
            now=i*DT
            state=scene.state(1)
            px,py,pz=state['position']
            vy=state['velocity'][1]
            rot=Rotation.from_quat(state['quat'])
            btm=float(np.min(rot.apply(local_corners)[:,1])+py)
            # Only stream terrain where first contact becomes plausible.
            if py<250 and (i==0 or vy<0):
                center=(math.floor(px/16),math.floor(pz/16))
                if center!=loaded_center:
                    scene.ground(SURFACE,px,pz,radius=3)
                    loaded_center=center
            # A user-requested ignition at t=0 overrides the OFF state in NBT.
            # The game-side redstone/CC event is not runnable outside Minecraft.
            impulse,torque=forces(state,now,com=com) if now>=ignite_at else (np.zeros(3),np.zeros(3))
            if not np.isfinite(impulse).all() or not np.isfinite(torque).all():
                raise ArithmeticError(f'non-finite force at {now}')
            if max(np.linalg.norm(impulse),np.linalg.norm(torque))>0:
                scene.impulse(1,impulse,torque)
            scene.step(DT)
            contacts=scene.collisions()
            state_after=scene.state(1)
            after_bottom=float(np.min(Rotation.from_quat(state_after['quat']).apply(local_corners)[:,1])+state_after['position'][1])
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
            'geometry':'six schematic voxels; per-state geometry from JAR where verified; fallback explicitly marked',
            'source_facts':source,
            'unresolved_voxel_shapes':unresolved,
            'reference_mass_from_nbt':measured_mass,
            'ignition_override_seconds':ignite_at,
            'strict_shape_validation':strict_shapes,
            'surface_y':SURFACE,'initial_position':pos.tolist(),
            'burn_seconds':BURN,'mass_used':mass,'mass_source':('jar_tags_and_sable_mass_tracker' if mass_jars else 'saved_reference_plus_uniform_inertia_approximation'),
            'mass_audit':mass_audit,'mass_properties':source_mass_properties,
            'impact':flight_result,'trace':trace,
            'fidelity_notes':['native Rapier solver, CCD, contacts, quaternion dynamics',
                              'approximate sail orientations/drag forces',
                              'per-block VoxelShapes verified only for recorded JAR states; unknowns declared',
                              'fuel startup logic and chunk loader not executed in Minecraft VM']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('nbt',type=Path)
    parser.add_argument('--jar',required=True,type=Path)
    parser.add_argument('--max-seconds',type=float,default=180)
    parser.add_argument('--propulsion-jar',type=Path)
    parser.add_argument('--sail-jar',type=Path)
    parser.add_argument('--cbc-jar',type=Path)
    parser.add_argument('--simulated-jar',type=Path,help='Simulated nested JAR for mass tags')
    parser.add_argument('--cc-jar',type=Path,help='CC:Tweaked JAR for mass tags')
    parser.add_argument('--chunk-loader-jar',type=Path,help='Autonomous loader JAR for mass tags')
    parser.add_argument('--strict-shapes',action='store_true')
    parser.add_argument('--ignite-at',type=float,default=0.0)
    parser.add_argument('--out',type=Path,required=True)
    a=parser.parse_args()
    specified=(a.propulsion_jar,a.sail_jar,a.cbc_jar)
    if any(specified) and not all(specified):parser.error('all three source JARs required')
    source_jars=dict(zip(('propulsion','sail','cbc'),specified)) if all(specified) else None
    mass_jars=None
    extras=(a.simulated_jar,a.cc_jar,a.chunk_loader_jar)
    if any(extras):
        if not all(extras) or not source_jars:
            parser.error('mass auditing requires --propulsion-jar, --sail-jar, --cbc-jar, --simulated-jar, --cc-jar, --chunk-loader-jar')
        mass_jars={'sable':a.jar,'simulated':a.simulated_jar,
                   'propulsion':a.propulsion_jar,'cbc':a.cbc_jar,
                   'cc':a.cc_jar,'chunk_loader':a.chunk_loader_jar}
    result=simulate(a.nbt,a.jar,max_seconds=a.max_seconds,source_jars=source_jars,
                    strict_shapes=a.strict_shapes,ignite_at=a.ignite_at,mass_jars=mass_jars)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'impact':result['impact'],'engine':result['engine']},ensure_ascii=False))

if __name__=='__main__':main()
