-- EN: Deterministic voxel and rigid-body test model, NOT the Minecraft/Sable/Rapier engine.
-- RU: Детерминированная модель вокселей и тел, НЕ движок Minecraft/Sable/Rapier.
local World={}
World.__index=World
local sqrt,floor,abs,min,max,exp=math.sqrt,math.floor,math.abs,math.min,math.max,math.exp
local function finite(n) return type(n)=="number" and n==n and abs(n)<math.huge end
local function vec(x,y,z) return {x=x,y=y,z=z} end
local function copy(v)
  if type(v)~="table" then return v end
  local r={}
  for k,x in pairs(v) do r[k]=copy(x) end
  return r
end
local function vector(v)
  assert(type(v)=="table" and finite(v.x) and finite(v.y) and finite(v.z),"finite {x,y,z} required")
  return vec(v.x,v.y,v.z)
end
local function key(x,y,z) return x..":"..y..":"..z end
local function normalize(q)
  local s=sqrt(q.w*q.w+q.x*q.x+q.y*q.y+q.z*q.z)
  assert(s>1e-12,"zero quaternion")
  return {w=q.w/s,x=q.x/s,y=q.y/s,z=q.z/s}
end
local function rotate(q,w,dt)
  -- EN: World-frame angular velocity, qdot = 0.5 * omega_quaternion * q.
  -- RU: Угловая скорость в мировых осях, qdot = 0.5 * omega_quaternion * q.
  return normalize({
    w=q.w-0.5*dt*(w.x*q.x+w.y*q.y+w.z*q.z),
    x=q.x+0.5*dt*(w.x*q.w+w.y*q.z-w.z*q.y),
    y=q.y+0.5*dt*(-w.x*q.z+w.y*q.w+w.z*q.x),
    z=q.z+0.5*dt*(w.x*q.y-w.y*q.x+w.z*q.w)
  })
end
local function sweptVoxel(p,d,x,y,z,r)
  -- EN: Expanded AABB is conservative for a sphere; corners are approximated.
  -- RU: Расширенный AABB консервативен для сферы; углы приближённые.
  local lo={x=x-r,y=y-r,z=z-r}
  local hi={x=x+1+r,y=y+1+r,z=z+1+r}
  local entry,leave,normal=0,1,nil
  for _,axis in ipairs({"x","y","z"}) do
    local delta=d[axis]
    if abs(delta)<1e-12 then
      if p[axis]<lo[axis] or p[axis]>hi[axis] then return nil end
    else
      local t1=(lo[axis]-p[axis])/delta
      local t2=(hi[axis]-p[axis])/delta
      if t1>t2 then t1,t2=t2,t1 end
      if t1>entry then
        entry=t1; normal=vec(0,0,0); normal[axis]=delta>0 and -1 or 1
      end
      leave=min(leave,t2)
      if entry>leave then return nil end
    end
  end
  if normal then return entry,normal end
  return nil
end
function World.new(options)
  options=options or {}
  local hz=options.physicsHz or 120
  local cap=options.maxCells or 30000
  assert(finite(hz) and hz>=20 and hz<=2000,"physicsHz out of range")
  assert(finite(cap) and cap>=1 and cap<=1000000,"maxCells out of range")
  return setmetatable({
    physicsHz=hz,maxCells=cap,gravity=vector(options.gravity or vec(0,-9.81,0)),
    blocks={},bodies={},order={},nextId=0,time=0,steps=0,events={},
    metrics={cellChecks=0,contacts=0,substeps=0}
  },World)
end
function World:setBlock(x,y,z,value)
  assert(finite(x) and finite(y) and finite(z)
    and x==floor(x) and y==floor(y) and z==floor(z),"integer block coordinates required")
  local k=key(x,y,z)
  if value==nil or value==false or value=="air" then self.blocks[k]=nil
  elseif value==true then self.blocks[k]={id="minecraft:stone",solid=true}
  elseif type(value)=="table" then
    self.blocks[k]={id=value.id or "minecraft:stone",
      solid=value.solid~=false,fluid=value.fluid or false}
  else error("unsupported block") end
end
function World:getBlock(x,y,z)
  local block=self.blocks[key(floor(x),floor(y),floor(z))]
  return copy(block or {id="minecraft:air",solid=false,fluid=false})
end
function World:addBody(o)
  o=o or {}
  local mass,radius=o.mass or 1,o.radius or 0.4
  local drag,restitution,friction=o.drag or 0,o.restitution or 0,o.friction or 0.6
  assert(finite(mass) and mass>0,"invalid mass")
  assert(finite(radius) and radius>0 and radius<=64,"invalid radius")
  assert(finite(drag) and drag>=0,"invalid drag")
  assert(finite(restitution) and restitution>=0 and restitution<=1,"invalid restitution")
  assert(finite(friction) and friction>=0 and friction<=1,"invalid friction")
  local q=o.orientation or {w=1,x=0,y=0,z=0}
  assert(finite(q.w) and finite(q.x) and finite(q.y) and finite(q.z),"invalid quaternion")
  local pos=vector(o.position or vec(0,2,0))
  self.nextId=self.nextId+1
  local b={id=self.nextId,position=pos,previousPosition=copy(pos),
    velocity=vector(o.velocity or vec(0,0,0)),
    angularVelocity=vector(o.angularVelocity or vec(0,0,0)),
    orientation=normalize(q),mass=mass,radius=radius,drag=drag,
    restitution=restitution,friction=friction,
    gravityScale=o.gravityScale==nil and 1 or o.gravityScale,
    force=vec(0,0,0),torque=vec(0,0,0),active=true}
  assert(finite(b.gravityScale),"invalid gravityScale")
  self.bodies[b.id]=b
  self.order[#self.order+1]=b.id
  return b.id
end
function World:getBody(id)
  return copy(assert(self.bodies[id],"body not found"))
end
function World:applyForce(id,force)
  local b=assert(self.bodies[id],"body not found"); force=vector(force)
  for _,a in ipairs({"x","y","z"}) do b.force[a]=b.force[a]+force[a] end
end
function World:applyTorque(id,torque)
  local b=assert(self.bodies[id],"body not found"); torque=vector(torque)
  for _,a in ipairs({"x","y","z"}) do b.torque[a]=b.torque[a]+torque[a] end
end
function World:applyImpulse(id,impulse)
  local b=assert(self.bodies[id],"body not found"); impulse=vector(impulse)
  for _,a in ipairs({"x","y","z"}) do b.velocity[a]=b.velocity[a]+impulse[a]/b.mass end
end
function World:castBlocks(position,delta,radius)
  local p,d=vector(position),vector(delta)
  assert(finite(radius) and radius>=0 and radius<=64,"invalid radius")
  local lo,hi={},{}
  local cells=1
  for _,a in ipairs({"x","y","z"}) do
    lo[a]=floor(min(p[a],p[a]+d[a])-radius-1)
    hi[a]=floor(max(p[a],p[a]+d[a])+radius+1)
    cells=cells*(hi[a]-lo[a]+1)
  end
  assert(cells<=self.maxCells,"physics broad-phase limit; increase maxCells explicitly")
  local best,normal,block=math.huge,nil,nil
  for x=lo.x,hi.x do for y=lo.y,hi.y do for z=lo.z,hi.z do
    self.metrics.cellChecks=self.metrics.cellChecks+1
    local b=self.blocks[key(x,y,z)]
    if b and b.solid then
      local t,n=sweptVoxel(p,d,x,y,z,radius)
      if t and t>=0 and t<=1 and t<best then
        best=t; normal=n; block=vec(x,y,z)
      end
    end
  end end end
  if normal then return {fraction=best,normal=normal,block=block} end
  return nil
end
local function resolveBlocks(world,b,d)
  local hit=world:castBlocks(b.position,d,b.radius)
  if not hit then
    for _,a in ipairs({"x","y","z"}) do b.position[a]=b.position[a]+d[a] end
    b.lastContact=nil
    return
  end
  local t=max(0,hit.fraction-1e-7)
  for _,a in ipairs({"x","y","z"}) do b.position[a]=b.position[a]+d[a]*t end
  local n=hit.normal
  local vn=b.velocity.x*n.x+b.velocity.y*n.y+b.velocity.z*n.z
  if vn<0 then
    for _,a in ipairs({"x","y","z"}) do
      b.velocity[a]=b.velocity[a]-(1+b.restitution)*vn*n[a]
    end
    local dot=b.velocity.x*n.x+b.velocity.y*n.y+b.velocity.z*n.z
    local friction=max(0,1-b.friction)
    for _,a in ipairs({"x","y","z"}) do
      b.velocity[a]=dot*n[a]+friction*(b.velocity[a]-dot*n[a])
    end
  end
  b.lastContact=hit
  world.metrics.contacts=world.metrics.contacts+1
  world.events[#world.events+1]={type="voxel_contact",body=b.id,block=hit.block,time=world.time}
end
local function resolveBodies(world)
  -- EN: Swept bounding spheres prevent straight-line body-to-body tunnelling.
  -- RU: Проверка движения сфер предотвращает пролёт тел друг через друга.
  for i=1,#world.order do
    local a=world.bodies[world.order[i]]
    for j=i+1,#world.order do
      local b=world.bodies[world.order[j]]
      if a and b then
        local p=vec(a.previousPosition.x-b.previousPosition.x,
          a.previousPosition.y-b.previousPosition.y,
          a.previousPosition.z-b.previousPosition.z)
        local d=vec((a.position.x-a.previousPosition.x)-(b.position.x-b.previousPosition.x),
          (a.position.y-a.previousPosition.y)-(b.position.y-b.previousPosition.y),
          (a.position.z-a.previousPosition.z)-(b.position.z-b.previousPosition.z))
        local radius=a.radius+b.radius
        local aa=d.x*d.x+d.y*d.y+d.z*d.z
        local bb=2*(p.x*d.x+p.y*d.y+p.z*d.z)
        local cc=p.x*p.x+p.y*p.y+p.z*p.z-radius*radius
        local hit=nil
        if cc<=0 then hit=0
        elseif aa>1e-16 then
          local disc=bb*bb-4*aa*cc
          if disc>=0 then
            local t=(-bb-sqrt(disc))/(2*aa)
            if t>=0 and t<=1 then hit=t end
          end
        end
        if hit then
          local n=vec(p.x+d.x*hit,p.y+d.y*hit,p.z+d.z*hit)
          local length=sqrt(n.x*n.x+n.y*n.y+n.z*n.z)
          if length>1e-12 then
            for _,axis in ipairs({"x","y","z"}) do n[axis]=n[axis]/length end
            local approach=(a.velocity.x-b.velocity.x)*n.x
              +(a.velocity.y-b.velocity.y)*n.y+(a.velocity.z-b.velocity.z)*n.z
            if approach<0 then
              local J=-(1+min(a.restitution,b.restitution))*approach/(1/a.mass+1/b.mass)
              for _,axis in ipairs({"x","y","z"}) do
                a.velocity[axis]=a.velocity[axis]+J*n[axis]/a.mass
                b.velocity[axis]=b.velocity[axis]-J*n[axis]/b.mass
                a.position[axis]=a.previousPosition[axis]
                  +(a.position[axis]-a.previousPosition[axis])*hit+n[axis]*1e-6
                b.position[axis]=b.previousPosition[axis]
                  +(b.position[axis]-b.previousPosition[axis])*hit-n[axis]*1e-6
              end
              world.metrics.contacts=world.metrics.contacts+1
              world.events[#world.events+1]={type="body_contact",body=a.id,other=b.id,time=world.time}
            end
          end
        end
      end
    end
  end
end
function World:step(seconds)
  assert(finite(seconds) and seconds>=0,"invalid duration")
  local count=floor(seconds*self.physicsHz+0.5)
  assert(count<=200000,"too many steps")
  local dt=1/self.physicsHz
  for _=1,count do
    for _,id in ipairs(self.order) do
      local b=self.bodies[id]
      if b and b.active then
        b.previousPosition=copy(b.position)
        local inertia=0.4*b.mass*b.radius*b.radius
        for _,axis in ipairs({"x","y","z"}) do
          local acceleration=self.gravity[axis]*b.gravityScale+b.force[axis]/b.mass
          b.velocity[axis]=(b.velocity[axis]+acceleration*dt)*exp(-b.drag*dt)
          b.angularVelocity[axis]=b.angularVelocity[axis]+b.torque[axis]/inertia*dt
        end
        resolveBlocks(self,b,vec(b.velocity.x*dt,b.velocity.y*dt,b.velocity.z*dt))
        b.orientation=rotate(b.orientation,b.angularVelocity,dt)
        b.force=vec(0,0,0); b.torque=vec(0,0,0)
      end
    end
    resolveBodies(self)
    self.time=self.time+dt; self.steps=self.steps+1
    self.metrics.substeps=self.metrics.substeps+1
  end
  return count
end
function World:snapshot()
  local bodies={}
  for _,id in ipairs(self.order) do
    local b=self.bodies[id]
    if b then
      bodies[#bodies+1]={id=id,position=copy(b.position),velocity=copy(b.velocity),
        orientation=copy(b.orientation),angularVelocity=copy(b.angularVelocity),
        lastContact=b.lastContact and copy(b.lastContact.block) or nil}
    end
  end
  return {time=self.time,physicsHz=self.physicsHz,steps=self.steps,bodies=bodies,metrics=copy(self.metrics)}
end
return World
