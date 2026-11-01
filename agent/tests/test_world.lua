-- EN: Deterministic physical invariants and synthetic CC adapter contract checks.
-- RU: Проверки физических инвариантов и контрактов имитации CC.
local World=require("agent.sim.world")
local Engine=require("agent.sim.engine")
local CC=require("agent.sim.cc")
local JSON=require("agent.sim.text")
local function near(actual,expected,tolerance)
  assert(math.abs(actual-expected)<=tolerance,
    ("expected %.6f ~= %.6f"):format(actual,expected))
end

-- EN: Force/mass integration is independent of object mass for gravity.
-- RU: Ускорение свободного падения не зависит от массы объекта.
local w=World.new({physicsHz=100})
local a=w:addBody({position={x=0,y=10,z=0},mass=2,radius=0.25})
local b=w:addBody({position={x=0,y=20,z=0},mass=4,radius=0.25})
w:applyImpulse(a,{x=10,y=0,z=0})
near(w:getBody(a).velocity.x,5,1e-10)
w:step(0.1)
near(w:getBody(a).velocity.y,w:getBody(b).velocity.y,1e-10)
near(w:getBody(a).velocity.y,-0.981,1e-6)
assert(w:getBody(a).position.x>0)

-- EN: Swept voxel collision must prevent high-speed tunnelling.
-- RU: Непрерывные столкновения должны исключать пролёт сквозь блок.
local fastWorld=World.new({physicsHz=20,gravity={x=0,y=0,z=0}})
fastWorld:setBlock(10,0,0,true)
local fast=fastWorld:addBody({
  position={x=0,y=0.5,z=0.5},velocity={x=400,y=0,z=0},radius=0.2
})
fastWorld:step(0.05)
assert(fastWorld:getBody(fast).position.x<10,"voxel tunnelling")
assert(fastWorld.metrics.contacts==1)

-- EN: Resting body must stop on top of a solid voxel.
-- RU: Тело должно останавливаться на твёрдой поверхности.
local ground=World.new({physicsHz=200})
for x=-2,2 do for z=-2,2 do ground:setBlock(x,0,z,true) end end
local falling=ground:addBody({position={x=0,y=2,z=0},radius=0.2})
ground:step(1)
local settled=ground:getBody(falling)
assert(settled.position.y>=1.19 and settled.position.y<=1.22)
near(settled.velocity.y,0,1e-9)
assert(ground.metrics.contacts>0)

-- EN: Straight-line swept sphere contact between two fast constructions.
-- RU: Столкновение двух быстрых конструкций по непрерывной траектории.
local collide=World.new({physicsHz=20,gravity={x=0,y=0,z=0}})
local first=collide:addBody({
  position={x=-5,y=5,z=0},velocity={x=200,y=0,z=0},mass=1,radius=0.5
})
local second=collide:addBody({
  position={x=5,y=5,z=0},velocity={x=-200,y=0,z=0},mass=1,radius=0.5
})
collide:step(0.05)
near(collide:getBody(first).velocity.x,0,1e-9)
near(collide:getBody(second).velocity.x,0,1e-9)
assert(collide.metrics.contacts==1)

-- EN: Quaternions must remain normalized under angular motion.
-- RU: Кватернионы должны оставаться нормализованными при вращении.
local spin=World.new({gravity={x=0,y=0,z=0}})
local spinning=spin:addBody({angularVelocity={x=0,y=math.pi,z=0}})
spin:step(1)
local q=spin:getBody(spinning).orientation
near(math.sqrt(q.w*q.w+q.x*q.x+q.y*q.y+q.z*q.z),1,1e-9)

-- EN: Mod-shaped peripheral reads, impulses, scheduled tasks and tick domains.
-- RU: Имитация API периферии, импульсов, запланированных событий и частот.
local engine=Engine.new({physicsHz=120,gravity={x=0,y=0,z=0}})
local rigid=engine.world:addBody({position={x=1,y=2,z=3},mass=2})
local cc=CC.new(engine)
local computer=cc:addComputer(1,rigid)
local physics=computer:physics()
near(physics.getPhysicsState().mass,2,1e-9)
physics.applyControlImpulse(2,0,0,0,0,0)
near(physics.getPhysicsState().vx,1,1e-9)
engine:schedule(2,function(e) e:setRedstone("lever","north",15) end)
local substeps=0
engine:on("before_physics",function() substeps=substeps+1 end)
engine:stepTicks(3)
assert(substeps==18 and engine.tick==3 and engine.world.steps==18)
assert(engine:getRedstone("lever","north")==15)
local pose=computer:sublevel().getLogicalPose()
near(pose.position.x,1.15,1e-9)
assert(computer:sublevel().isInPlotGrid())
local report=JSON.encode(engine:snapshot())
assert(report:find('"tick":3',1,true))
assert(report:find('"physicsHz":120',1,true))
print("deterministic world tests passed")
