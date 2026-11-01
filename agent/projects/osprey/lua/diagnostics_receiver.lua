-- Operator pocket terminal: read-only status display. No transmit or control path.
local P=dofile('diagnostics_protocol.lua')
local cfg=dofile('diagnostics_receiver_config.lua')
local s=P.newState(cfg.vehicle)
local timeout=tonumber(cfg.stale_seconds) or 3
assert(timeout>=1 and timeout<=30,'stale_seconds must be 1..30')
assert(peripheral and peripheral.getNames and rednet and rednet.open and rednet.receive,
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

local ar=nil
for _,name in ipairs(peripheral.getNames()) do
  local p=peripheral.wrap(name)
  if p and type(p.drawText2D)=='function' and type(p.update)=='function' then
    ar=p;break
  end
end
local function draw(now)
  local health=P.health(s,now,timeout)
  local frame=s.last_frame
  local pos=frame and frame.pos
  local speed=frame and P.speed(frame.velocity)
  term.clear();term.setCursorPos(1,1)
  print('OSPREY / passive diagnostics')
  print('Vehicle: '..cfg.vehicle)
  print('Link: '..health)
  print('Packets: '..s.accepted..' ok, '..s.rejected..' rejected')
  if health=='ok' and pos then
    print(string.format('XYZ %.2f %.2f %.2f',pos.x,pos.y,pos.z))
    print(string.format('Speed %.2f blocks/s',speed))
    print('Sample: '..tostring(frame.seq))
  else
    print('Motion data unavailable')
  end
  if ar then
    local ok=pcall(function()
      ar.drawText2D('osprey_diag_title',0,8,8,'OSPREY DIAG '..health,false)
      ar.drawText2D('osprey_diag_link',0,8,24,
                    'Samples '..s.accepted..'  Rejected '..s.rejected,false)
      ar.update()
    end)
    if not ok then ar=nil end
  end
end
while true do
  local sender,packet=rednet.receive(P.CHANNEL,.5)
  local now=os.clock()
  if sender and type(packet)=='table' then
    P.accept(s,packet,now)
  end
  draw(now)
end
