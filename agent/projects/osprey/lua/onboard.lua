-- OSPREY Minecraft flight-test controller; inert, no payload activation.
-- Requires CC:Sable 1.3.4, NeoPeripheral Synaxis compact flaps and Propulsion.
-- Flight behavior unqualified: never claim 20..600 km range from this code.
local M=dofile("common.lua")
local config=dofile("config.lua")
local state="READY"
local seq=-1
local target=nil
local targetUpdated=0
local missionTime=0
local boot=os.clock()
local lastTelemetry=0
local lastError=""
local engines,fins={},{}

local function stamp() return os.clock()-boot end
local function safeCall(dev,method,...)
  if not dev or type(dev[method])~="function" then return false,"missing "..method end
  return pcall(dev[method],...)
end
local function connect()
  for i,name in ipairs(config.engines or {}) do
    local dev=peripheral.wrap(name)
    if not dev then error("missing engine peripheral: "..tostring(name)) end
    if type(dev.setPowerNormalized)~="function" then error("invalid engine: "..tostring(name)) end
    engines[i]=dev
  end
  if #engines==0 then error("no fuel engine configured") end
  for key,name in pairs(config.fins or {}) do
    local dev=peripheral.wrap(name)
    if not dev or type(dev.setAngle)~="function" then error("missing Synaxis compact flap: "..tostring(name)) end
    fins[key]=dev
  end
end
local function neutral()
  for _,dev in pairs(fins) do safeCall(dev,"setAngle",0) end
end
local function telemetry()
  local pose,linear,angular
  local ok=pcall(function()
    pose=sublevel.getLogicalPose()
    linear=sublevel.getLinearVelocity()
    angular=sublevel.getAngularVelocity()
  end)
  if not ok or not pose or not M.vec(pose.position) then
    lastError="CC:Sable position unavailable; verify assembly"
    return
  end
  local v=linear or {x=0,y=0,z=0}
  local p={ver=1,rocket=config.rocket,kind="telemetry",state=state,
    pos=pose.position,velocity=v,angular=angular,
    speed=M.length(v),target=target,uptime=stamp(),error=lastError}
  rednet.broadcast(p,M.TELEMETRY)
end
local function verify(msg,sender)
  if not M.validPacket(msg,config.rocket,config.secret) then return false end
  if config.operator_id and sender~=config.operator_id then return false end
  if msg.seq<=seq then return false end
  seq=msg.seq
  return true
end
local function onMessage(sender,msg)
  if not verify(msg,sender) then return end
  if msg.command=="SET_TARGET" then
    if not M.point(msg.target) then return end
    target=msg.target
    targetUpdated=stamp()
    if state=="TRACK_LOST" then state="COAST";lastError="" end
  elseif msg.command=="LAUNCH" then
    if state~="READY" or not target then return end
    if not config.allow_control then lastError="actuation disabled in config.lua" return end
    state="BOOST";missionTime=stamp()
    for _,engine in ipairs(engines) do
      local ok,why=safeCall(engine,"setPowerNormalized",1)
      if not ok then lastError="engine launch failed: "..tostring(why) end
    end
  elseif msg.command=="SAFE" and state=="READY" then
    target=nil;neutral()
  elseif msg.command=="NEUTRAL" then
    neutral()
  end
  -- Solid fuel cannot be assumed safely shutdown or reignited; no STOP command.
end
local function guidance()
  if state=="BOOST" and stamp()-missionTime>=(config.burn_seconds or 800) then state="COAST" end
  if state~="BOOST" and state~="COAST" then return end
  if not target then neutral();return end
  if target.kind=="track" and stamp()-targetUpdated>(config.target_timeout or 3) then
    state="TRACK_LOST";neutral();lastError="target telemetry stale"
    return
  end
  local ok,pose=pcall(sublevel.getLogicalPose)
  if not ok or not pose or not M.vec(pose.position) or not M.quaternion(pose.orientation) then
    neutral();lastError="invalid CC:Sable pose";return
  end
  local delta=M.sub(target.pos,pose.position)
  local range=M.length(delta)
  if range<10 then state="ARRIVED";neutral();return end
  local localVec=M.worldToLocal(pose.orientation,M.normalize(delta))
  -- Game-only directional assist using compact flap peripherals.
  -- This is NOT a validated ballistic interceptor or aerodynamic model.
  local pitch=math.atan2(localVec.y,math.max(.01,localVec.z))
  local yaw=math.atan2(localVec.x,math.max(.01,localVec.z))
  local limit=config.fin_limit or 15
  local pitchAngle=M.clamp(pitch*180/math.pi*(config.correction_gain or .8),-limit,limit)
  local yawAngle=M.clamp(yaw*180/math.pi*(config.correction_gain or .8),-limit,limit)
  for key,dev in pairs(fins) do
    local correction=(key=="pitch_up" or key=="pitch_down") and pitchAngle or yawAngle
    local sign=(config.fin_signs or {})[key] or 1
    safeCall(dev,"setAngle",correction*sign)
  end
end
local function loop()
  local modem,reason=M.openWireless()
  if not modem then error(reason) end
  if not sublevel or type(sublevel.getLogicalPose)~="function" then error("CC:Sable sublevel API unavailable") end
  connect();neutral()
  if config.auto_assemble_fins then
    for _,fin in pairs(fins) do safeCall(fin,"assemble") end
  end
  while true do
    local sender,msg=rednet.receive(M.PROTOCOL,1/(config.control_hz or 10))
    if sender then onMessage(sender,msg) end
    if stamp()-lastTelemetry>=.5 then telemetry();lastTelemetry=stamp() end
    guidance()
  end
end
local ok,err=pcall(loop)
if not ok then print("OSPREY FATAL: "..tostring(err));neutral() end
