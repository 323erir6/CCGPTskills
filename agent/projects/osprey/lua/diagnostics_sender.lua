-- Read-only CC:Sable sender. Never receives packets, commands, or changes actuators.
local P=dofile('diagnostics_protocol.lua')
local cfg=dofile('diagnostics_config.lua')
local hz=assert(tonumber(cfg.hz),'missing hz')
local samples=assert(tonumber(cfg.samples),'missing samples')
assert(hz>=1 and hz<=20 and hz%1==0,'hz must be 1..20')
assert(samples>=1 and samples<=100000 and samples%1==0,'samples must be integer 1..100000')
assert(type(cfg.vehicle)=='string' and #cfg.vehicle>0 and #cfg.vehicle<=64,'vehicle required')
assert(sublevel and type(sublevel.getLogicalPose)=='function' and
  type(sublevel.getLinearVelocity)=='function' and
  type(sublevel.getAngularVelocity)=='function','CC:Sable missing')
assert(peripheral and peripheral.getNames and rednet and rednet.open and rednet.broadcast,
       'CC:Tweaked wireless modem required')
local modem
for _,name in ipairs(peripheral.getNames()) do
  if peripheral.hasType and peripheral.hasType(name,'modem') then
    local p=peripheral.wrap(name)
    local ok,wireless=pcall(function()return p.isWireless() end)
    if ok and wireless then modem=name;break end
  end
end
assert(modem,'wireless modem not found')
rednet.open(modem)
local id=(os.getComputerID and os.getComputerID() or 0)
local session=string.format('diag-%s-%s',tostring(id),tostring(os.epoch and os.epoch('utc') or os.clock()))
local start=os.clock()
for seq=0,samples-1 do
  local ok,pose,v,w=pcall(function()
    return sublevel.getLogicalPose(),sublevel.getLinearVelocity(),sublevel.getAngularVelocity()
  end)
  local frame=P.frame(cfg.vehicle,session,seq,math.max(0,os.clock()-start),
                      ok and pose or nil,v,w)
  rednet.broadcast(frame,P.CHANNEL)
  if seq<samples-1 then sleep(1/hz) end
end
print('Diagnostics transmission completed ('..samples..' frames)')
