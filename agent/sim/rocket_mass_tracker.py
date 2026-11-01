"""Exact scalar/tensor aggregation from Sable 2.0.5 MassTracker.build.

Block mass, per-state center of mass and optional per-block inertia must come
from the registered Minecraft blockstate/datapack. Missing data is an error;
we do not invent block masses and call the answer source-exact.
"""
from __future__ import annotations
import math


def mass_properties(items: list[dict]) -> dict:
    """Each item: pos [3], mass, local_center [3], optional inertia [3].

    Sable logic: each body inertia = diag(m/6), or diag(m * inertias),
    then tensor sum += m * ((r.r) * I - outer(r,r)).
    """
    if not items:raise ValueError('no mass-bearing blocks')
    m_total=0.0; weighted=[0.0]*3; normalized=[]
    for i,item in enumerate(items):
        pos=item['pos'];m=float(item['mass']);center=item['local_center']
        if not math.isfinite(m) or m<0 or not all(math.isfinite(float(x)) for x in (*pos,*center)):
            raise ValueError('non-finite mass block '+str(i))
        xyz=tuple(float(pos[k])+float(center[k]) for k in range(3))
        normalized.append((xyz,m,item.get('inertia')))
        m_total+=m
        for k in range(3):weighted[k]+=m*xyz[k]
    if m_total<=0:raise ValueError('zero total mass')
    com=tuple(x/m_total for x in weighted)
    tensor=[[0.0]*3 for _ in range(3)]
    for pos,m,inertia in normalized:
        internal=[m/6]*3 if inertia is None else [m*float(v) for v in inertia]
        r=[pos[k]-com[k] for k in range(3)]
        r2=sum(v*v for v in r)
        for k in range(3):
            for j in range(3):
                tensor[k][j]+=(internal[k] if j==k else 0)+(m*((r2 if j==k else 0)-r[k]*r[j]))
    return {'mass':m_total,'center_of_mass':com,'inertia_tensor':tensor,
            'inertia_diagonal':tuple(tensor[i][i] for i in range(3)),
            'off_diagonal_present':any(abs(tensor[i][j])>1e-10 for i in range(3) for j in range(3) if i!=j)}
