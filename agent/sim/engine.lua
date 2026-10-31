-- EN: Deterministic server clock: 20 Minecraft ticks/s, configurable physics substeps.
-- RU: Часы сервера: 20 игровых тиков/с и настраиваемые физические подшаги.
local World=require("agent.sim.world")
local Clock=require("agent.mocks.clock")
local Engine={}; Engine.__index=Engine
function Engine.new(options)
  options=options or {}
  local hz=options.physicsHz or 120
  assert(type(hz)=="number" and hz%20==0,
    "physicsHz must be divisible by 20")
  return setmetatable({
    world=World.new(options),clock=Clock.new(),tick=0,physicsHz=hz,
    redstone={},redstoneEvents={},handlers={},scheduled={},sequence=0
  },Engine)
end
function Engine:on(event,callback)
  assert(type(event)=="string" and type(callback)=="function","invalid listener")
  local listeners=self.handlers[event] or {}
  listeners[#listeners+1]=callback; self.handlers[event]=listeners
end
function Engine:emit(event,data)
  for _,listener in ipairs(self.handlers[event] or {}) do listener(self,data) end
end
function Engine:schedule(ticks,callback)
  assert(type(ticks)=="number" and ticks%1==0 and ticks>=1 and type(callback)=="function",
    "schedule needs a positive tick count and callback")
  self.sequence=self.sequence+1
  self.scheduled[#self.scheduled+1]={at=self.tick+ticks,id=self.sequence,callback=callback}
end
function Engine:setRedstone(name,side,signal)
  assert(type(name)=="string" and type(side)=="string","invalid redstone endpoint")
  assert(type(signal)=="number" and signal%1==0 and signal>=0 and signal<=15,
    "redstone signal must be 0..15")
  local node=self.redstone[name] or {}
  self.redstone[name]=node
  local previous=node[side] or 0
  node[side]=signal
  if previous~=signal then
    local e={name=name,side=side,signal=signal,tick=self.tick}
    self.redstoneEvents[#self.redstoneEvents+1]=e
    self.clock:queueEvent("redstone",name,side,signal)
    self:emit("redstone",e)
  end
end
function Engine:getRedstone(name,side)
  return (self.redstone[name] or {})[side] or 0
end
function Engine:stepTicks(count)
  assert(type(count)=="number" and count%1==0 and count>=0 and count<=100000,
    "invalid tick count")
  for _=1,count do
    self.tick=self.tick+1
    self:emit("before_tick",{tick=self.tick})
    table.sort(self.scheduled,function(a,b)
      if a.at==b.at then return a.id<b.id end
      return a.at<b.at
    end)
    local ready={}
    while self.scheduled[1] and self.scheduled[1].at<=self.tick do
      ready[#ready+1]=table.remove(self.scheduled,1)
    end
    for _,e in ipairs(ready) do e.callback(self) end
    for _=1,self.physicsHz/20 do
      self:emit("before_physics",{tick=self.tick,substep=self.world.steps+1})
      self.world:step(1/self.physicsHz)
      self:emit("after_physics",{tick=self.tick,substep=self.world.steps})
    end
    self.clock:advance(0.05)
    self:emit("after_tick",{tick=self.tick})
  end
end
function Engine:snapshot()
  return {tick=self.tick,world=self.world:snapshot(),
    redstone=self.redstone,redstoneEvents=self.redstoneEvents}
end
return Engine
