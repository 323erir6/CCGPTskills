-- CC:AR 0.2.1 display bridge, run on a computer ATTACHED to an AR Controller.
-- AR goggles paired to the controller display these elements in-game.
local M=dofile("common.lua")
local config=dofile("config.lua")
local modem,why=M.openWireless()
if not modem then error(why) end
local controller
for _,name in ipairs(peripheral.getNames()) do
  local p=peripheral.wrap(name)
  if p and type(p.drawText2D)=="function" and type(p.update)=="function" then
    controller=p;break
  end
end
if not controller then error("CC:AR controller not connected") end
local last=0
local function show(t)
  local ttl=string.format("OSPREY %s",t.state or "NO DATA")
  local p=t.pos or {x=0,y=0,z=0}
  controller.drawRect2D("osprey:panel",0,8,8,200,64)
  controller.drawText2D("osprey:title",0,12,12,ttl,false)
  controller.drawText2D("osprey:pos",0,12,27,
    string.format("XYZ %.0f %.0f %.0f",p.x,p.y,p.z),false)
  controller.drawText2D("osprey:vel",0,12,42,
    string.format("Speed %.0f m/s",t.speed or 0),false)
  controller.update()
end
while true do
  local id,msg=rednet.receive(M.TELEMETRY,2)
  if type(msg)=="table" and msg.rocket==config.rocket and M.vec(msg.pos) then
    if os.clock()-last>=.2 then
      local ok,err=pcall(show,msg)
      if not ok then print("AR failed: "..tostring(err)) end
      last=os.clock()
    end
  end
end
