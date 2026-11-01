-- EN: Synthetic CC:Tweaked computer with Sable/NeoPeripheral-shaped adapters.
-- RU: Имитация компьютера CC:Tweaked с адаптерами Sable/NeoPeripheral.
local Registry=require("agent.mocks.peripheral")
local Network=require("agent.mocks.rednet")
local CC={}; CC.__index=CC
function CC.new(engine)
  return setmetatable({
    engine=engine,peripherals=Registry.new(),network=Network.new(),nodes={}
  },CC)
end
function CC:addComputer(id,bodyId)
  assert(type(id)=="number" and id>=0 and id%1==0,"invalid computer ID")
  assert(not self.nodes[id],"duplicate computer ID")
  local engine=self.engine
  local node={
    id=id,bodyId=bodyId,events={},
    peripheral=self.peripherals:api(),rednet=self.network:node(id)
  }
  function node:sublevel()
    return {
      isInPlotGrid=function()
        return bodyId~=nil and engine.world.bodies[bodyId]~=nil
      end,
      getLogicalPose=function()
        local b=engine.world:getBody(assert(bodyId,"not on construction"))
        return {
          position=b.position,rotationPoint={x=0,y=0,z=0},
          scale={x=1,y=1,z=1},
          orientation={a=b.orientation.w,v={
            x=b.orientation.x,y=b.orientation.y,z=b.orientation.z}}
        }
      end,
      getVelocity=function()
        return engine.world:getBody(assert(bodyId,"not on construction")).velocity
      end
    }
  end
  function node:physics()
    return {
      getPhysicsState=function()
        local b=engine.world:getBody(assert(bodyId,"not on construction"))
        return {
          x=b.position.x,y=b.position.y,z=b.position.z,
          qx=b.orientation.x,qy=b.orientation.y,qz=b.orientation.z,qw=b.orientation.w,
          vx=b.velocity.x,vy=b.velocity.y,vz=b.velocity.z,
          wx=b.angularVelocity.x,wy=b.angularVelocity.y,wz=b.angularVelocity.z,
          mass=b.mass
        }
      end,
      applyControlImpulse=function(lx,ly,lz,ax,ay,az)
        local body=assert(bodyId,"not on construction")
        engine.world:applyImpulse(body,{x=lx,y=ly,z=lz})
        local b=engine.world.bodies[body]
        local inertia=0.4*b.mass*b.radius*b.radius
        b.angularVelocity.x=b.angularVelocity.x+ax/inertia
        b.angularVelocity.y=b.angularVelocity.y+ay/inertia
        b.angularVelocity.z=b.angularVelocity.z+az/inertia
        return true
      end
    }
  end
  function node:os() return engine.clock:api() end
  function node:redstone()
    local output={}
    return {
      setOutput=function(side,value)
        assert(type(value)=="boolean","expected boolean")
        output[side]=value
        engine:setRedstone("computer:"..id,side,value and 15 or 0)
      end,
      getOutput=function(side) return output[side] or false end,
      setAnalogOutput=function(side,value)
        engine:setRedstone("computer:"..id,side,value)
      end,
      getAnalogOutput=function(side)
        return engine:getRedstone("computer:"..id,side)
      end
    }
  end
  self.nodes[id]=node
  return node
end
return CC
