-- EN: Synthetic sublevel snapshots for math/control tests, NOT a Sable physics engine.
-- RU: Синтетические состояния sublevel, НЕ физический движок Sable.
local Mock = {}
Mock.__index = Mock

local function copy(t)
  if type(t) ~= 'table' then return t end
  local v = {}
  for k, val in pairs(t) do v[k] = copy(val) end
  return v
end

function Mock.new(pose, velocity)
  local identity = {
    position = {x=0,y=0,z=0}, rotationPoint = {x=0,y=0,z=0},
    scale = {x=1,y=1,z=1}, orientation = {a=1,v={x=0,y=0,z=0}}
  }
  return setmetatable({pose = copy(pose or identity),
    velocity = copy(velocity or {x=0,y=0,z=0}), attached = true}, Mock)
end

function Mock:api()
  local this = self
  return {
    isInPlotGrid = function() return this.attached end,
    getLogicalPose = function()
      assert(this.attached, 'Computer not on a sublevel')
      return copy(this.pose)
    end,
    getVelocity = function()
      assert(this.attached, 'Computer not on a sublevel')
      return copy(this.velocity)
    end
  }
end

function Mock:setPose(pose) self.pose = copy(pose) end
function Mock:setVelocity(value) self.velocity = copy(value) end
return Mock
