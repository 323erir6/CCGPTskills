-- EN: Pure mathematical regression tests with synthetic poses.
-- RU: Регрессионные математические тесты с искусственными позами.
local M = require("lib.sublevel_pose")
local function near(a,b,tolerance)
  assert(math.abs(a-b) <= (tolerance or 1e-8),
    ("expected %f, actual %f"):format(b,a))
end
local function vecNear(actual,expected)
  near(actual.x,expected.x);near(actual.y,expected.y);near(actual.z,expected.z)
end
local function pose(p,q,scale,rp)
  return {position=p or {x=0,y=0,z=0},
    orientation=q or {a=1,v={x=0,y=0,z=0}},
    scale=scale or {x=1,y=1,z=1},
    rotationPoint=rp or {x=0,y=0,z=0}}
end

-- EN: No rotation, explicit translation, scale and pivot.
-- RU: Без вращения; заданный перенос, масштаб и центр.
local p = pose({x=100,y=50,z=-20},nil,{x=2,y=3,z=4},{x=5,y=6,z=7})
local w = M.localToWorld({x=6,y=8,z=9},p)
vecNear(w,{x=102,y=56,z=-12})
vecNear(M.worldToLocal(w,p),{x=6,y=8,z=9})

-- EN: +90 degree world Y rotation maps body +Z to world +X.
-- RU: Поворот на +90 градусов вокруг Y переводит +Z в +X.
local half = math.sqrt(0.5)
local yaw90 = pose(nil,{a=half,v={x=0,y=half,z=0}})
vecNear(M.localToWorld({x=0,y=0,z=1},yaw90),{x=1,y=0,z=0})
local yaw,pitch,roll = M.yawPitchRoll(yaw90)
near(yaw,90); near(pitch,0); near(roll,0)
near(M.speedAlongLocalAxis({x=10,y=0,z=0},{x=0,y=0,z=1},yaw90),10)

-- EN: Quaternion +90 around X gives negative 90 pitch in this convention.
-- RU: +90 вокруг X даёт отрицательный pitch в данном соглашении.
local pitchNeg90 = pose(nil,{a=half,v={x=half,y=0,z=0}})
local _,pi = M.yawPitchRoll(pitchNeg90)
near(pi,-90)

-- EN: Rotation by +90 around Z yields positive roll.
-- RU: Поворот +90 вокруг Z даёт положительный roll.
local roll90 = pose(nil,{a=half,v={x=0,y=0,z=half}})
local _,_,r = M.yawPitchRoll(roll90)
near(r,90)

-- EN: Quaternion norm is corrected if components were scaled uniformly.
-- RU: Норма кватерниона исправляется после общего масштабирования.
local qScaled = pose(nil,{a=half*3,v={x=0,y=half*3,z=0}})
vecNear(M.localToWorld({x=0,y=0,z=1},qScaled),{x=1,y=0,z=0})
print("sublevel_pose tests passed")
