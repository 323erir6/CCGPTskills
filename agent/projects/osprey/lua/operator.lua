-- Pocket-computer operator console for an inert Minecraft flight-test craft.
-- Enter coordinates as in-game block coordinates. Does not use real GPS.
local M=dofile("common.lua")
local config=dofile("config.lua")
local modem,why=M.openWireless()
if not modem then error(why) end
local sequence=0
local selected=nil
local latest=nil
local tracks={}
local lastSensor=0
local telemetryUpdated=-math.huge

local function send(cmd,extra)
  sequence=sequence+1
  local p={ver=1,rocket=config.rocket,secret=config.secret,seq=sequence,command=cmd}
  if extra then for k,v in pairs(extra) do p[k]=v end end
  rednet.broadcast(p,M.PROTOCOL)
end
local function draw()
  term.clear();term.setCursorPos(1,1)
  print("OSPREY / Minecraft Test")
  print("Vehicle: "..config.rocket)
  print("State: "..tostring(latest and latest.state or "NO LINK"))
  if latest and latest.pos then
    print(string.format("Pos %.1f %.1f %.1f",latest.pos.x,latest.pos.y,latest.pos.z))
    print(string.format("Speed %.1f m/s",latest.speed or 0))
    if latest.error and latest.error~="" then print("Warn "..latest.error) end
  end
  if selected then
    print(string.format("Target %s",selected.id or selected.kind))
    print(string.format("%.0f %.0f %.0f",selected.pos.x,selected.pos.y,selected.pos.z))
  else print("Target: none") end
  print("1: Static game marker")
  print("2: In-game observed target")
  print("3: Transmit target")
  print("4: Flight test launch")
  print("5: Neutral fins")
  print("Q: Quit")
  local count=0;for _ in pairs(tracks) do count=count+1 end
  print("Sensor tracks: "..count)
end
local function askNumber(prompt)
  write(prompt..": ")
  local n=tonumber(read())
  if not M.finite(n) or math.abs(n)>30000000 then error("invalid world coordinate") end
  return n
end
local function chooseMarker()
  term.clear();term.setCursorPos(1,1)
  local x=askNumber("X");local y=askNumber("Y");local z=askNumber("Z")
  selected={kind="marker",pos={x=x,y=y,z=z},id="marker"}
end
local function chooseTrack()
  local keys={}
  for key,record in pairs(tracks) do if M.vec(record.pos) then keys[#keys+1]=key end end
  table.sort(keys)
  term.clear();term.setCursorPos(1,1)
  for i,key in ipairs(keys) do print(i..": "..key) end
  if #keys==0 then print("No tracked game objects.");sleep(1);return end
  write("Select #: ")
  local i=tonumber(read())
  if i and keys[i] then
    local p=tracks[keys[i]]
    selected={kind="track",id=keys[i],pos=p.pos}
  end
end
local function ingest(sender,message,protocol)
  if protocol==M.TELEMETRY and type(message)=="table" and message.rocket==config.rocket then
    latest=message
    telemetryUpdated=os.clock()
  elseif protocol==M.SENSOR and type(message)=="table" and message.rocket==config.rocket then
    if type(message.id)=="string" and M.vec(message.pos) and #message.id<100 then
      tracks[message.id]={pos=message.pos,last=os.clock()}
      if selected and selected.kind=="track" and selected.id==message.id then
        selected.pos=message.pos
        if os.clock()-lastSensor>=.2 then
          send("SET_TARGET",{target=selected});lastSensor=os.clock()
        end
      end
    end
  end
end
local function messageLoop()
  while true do local _,sender,msg,protocol=os.pullEvent("rednet_message");ingest(sender,msg,protocol) end
end
local function menuLoop()
  local repaint=os.startTimer(.25)
  while true do
    draw();local e,key=os.pullEvent()
    if e=="timer" and key==repaint then repaint=os.startTimer(.25) end
    if e=="key" and key==keys.one then chooseMarker()
    elseif e=="key" and key==keys.two then chooseTrack()
    elseif e=="key" and key==keys.three then if selected then send("SET_TARGET",{target=selected}) end
    elseif e=="key" and key==keys.four then
      if selected and latest and latest.state=="READY" and os.clock()-telemetryUpdated < 3 then
        term.clear();term.setCursorPos(1,1)
        print("Flight-test launch? type YES")
        if read()=="YES" then send("LAUNCH") end
      else
        print("Require a recent READY telemetry and target")
        sleep(1)
      end
    elseif e=="key" and key==keys.five then send("NEUTRAL")
    elseif e=="key" and key==keys.q then break end
  end
end
parallel.waitForAny(messageLoop,menuLoop)
