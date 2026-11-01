-- OSPREY Minecraft-only CC:Tweaked packet and vector utilities.
-- No real-world coordinates or external network APIs.
local M = {}
M.PROTOCOL = "osprey_v1"
M.TELEMETRY = "osprey_tlm_v1"
M.SENSOR = "osprey_sensor_v1"
M.VERSION = 1

function M.finite(n)
  return type(n) == "number" and n == n and n ~= math.huge and n ~= -math.huge
end
function M.vec(v)
  return type(v) == "table" and M.finite(v.x) and M.finite(v.y) and M.finite(v.z)
end
function M.length(v)
  return math.sqrt(v.x*v.x+v.y*v.y+v.z*v.z)
end
function M.sub(a,b)
  return {x=a.x-b.x,y=a.y-b.y,z=a.z-b.z}
end
function M.add(a,b)
  return {x=a.x+b.x,y=a.y+b.y,z=a.z+b.z}
end
function M.mul(a,s)
  return {x=a.x*s,y=a.y*s,z=a.z*s}
end
function M.clamp(x,a,b)
  return math.max(a, math.min(b,x))
end
function M.normalize(v)
  local n=M.length(v)
  if n < 0.00001 then return {x=0,y=0,z=0} end
  return M.mul(v,1/n)
end
function M.quaternion(q)
  return type(q)=="table" and M.finite(q.x) and M.finite(q.y) and M.finite(q.z) and M.finite(q.w)
end
function M.worldToLocal(q,v)
  -- q rotation convention: x,y,z,w (verified CC:Sable CCSableUtils.toLua).
  local x,y,z,w=-q.x,-q.y,-q.z,q.w
  local tx=2*(y*v.z-z*v.y)
  local ty=2*(z*v.x-x*v.z)
  local tz=2*(x*v.y-y*v.x)
  return {x=v.x+w*tx+(y*tz-z*ty),
          y=v.y+w*ty+(z*tx-x*tz),
          z=v.z+w*tz+(x*ty-y*tx)}
end
function M.point(t)
  return type(t)=="table" and (t.kind=="marker" or t.kind=="track")
    and M.vec(t.pos) and (t.kind~="track" or type(t.id)=="string")
end
function M.validPacket(p,rocket,secret)
  return type(p)=="table" and p.ver==M.VERSION and p.rocket==rocket
    and p.secret==secret and M.finite(p.seq) and p.seq>=0 and p.seq%1==0
    and type(p.command)=="string"
end
function M.openWireless()
  if not peripheral or not peripheral.getNames then return nil,"no peripheral API" end
  for _,name in ipairs(peripheral.getNames()) do
    if peripheral.hasType and peripheral.hasType(name,"modem") then
      local p=peripheral.wrap(name)
      local ok,wireless=pcall(function()return p.isWireless() end)
      if ok and wireless then
        rednet.open(name)
        return name
      end
    end
  end
  return nil,"no wireless modem"
end
return M
