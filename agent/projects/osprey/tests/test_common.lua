local M=dofile('agent/projects/osprey/lua/common.lua')
local function eq(a,b) assert(a==b,tostring(a)..' != '..tostring(b)) end
eq(M.PROTOCOL,'osprey_v1')
assert(M.vec({x=1,y=2,z=3}))
assert(not M.vec({x='oops',y=2,z=3}))
assert(M.point({kind='marker',pos={x=0,y=100,z=0}}))
assert(M.point({kind='track',id='ship:test',pos={x=7,y=8,z=9}}))
assert(not M.point({kind='track',pos={x=7,y=8,z=9}}))
assert(not M.validPacket({ver=1,rocket='OSPREY-01',seq=0,secret='wrong',command='LAUNCH'},'OSPREY-01','key'))
assert(M.validPacket({ver=1,rocket='OSPREY-01',seq=0,secret='key',command='PING'},'OSPREY-01','key'))
local q={x=0,y=0,z=0,w=1}
local r=M.worldToLocal(q,{x=3,y=-4,z=5})
eq(r.x,3);eq(r.y,-4);eq(r.z,5)
local rot={x=0,y=math.sqrt(.5),z=0,w=math.sqrt(.5)}
local x=M.worldToLocal(rot,{x=1,y=0,z=0})
assert(math.abs(x.z-1)<1e-9)
eq(M.clamp(-2,-1,1),-1)
eq(M.clamp(5,-1,1),1)
print('OSPREY Lua common tests passed')
