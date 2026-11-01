-- Sensor relay from GAME-ONLY player and sublevel radar peripherals.
-- Does not invent scan range or methods. Requires observed coordinates.
local M=dofile("common.lua")
local config=dofile("config.lua")
local m,why=M.openWireless()
if not m then error(why) end
local seq=0
local function getVec(t)
  if type(t)~="table" then return nil end
  if M.vec(t.pos) then return t.pos end
  if M.vec(t.position) then return t.position end
  if M.vec(t) then return {x=t.x,y=t.y,z=t.z} end
  return nil
end
local function transmit(kind,id,point)
  if not M.vec(point) or type(id)~="string" then return end
  rednet.broadcast({rocket=config.rocket,id=kind..":"..id,
                    pos=point,seen=os.clock()},M.SENSOR)
end
local function scanList(kind,rows)
  if type(rows)~="table" then return end
  for _,obj in pairs(rows) do
    local pos=getVec(obj)
    if pos then
      local id=tostring(obj.name or obj.nickname or obj.id or obj.uuid or "unknown")
      transmit(kind,id,pos)
    end
  end
end
local function findByMethod(method)
  for _,name in ipairs(peripheral.getNames()) do
    local p=peripheral.wrap(name)
    if p and type(p[method])=="function" then return p end
  end
end
local function loop()
  local player=findByMethod("getPlayerPos")
  local playerList=findByMethod("getOnlinePlayers")
  local entityRadar=findByMethod("scanForEntities")
  local shipRadar=findByMethod("scanForSubLevels")
  while true do
    -- playerDetector, if installed. The provided 6.9.3 pack does not list it.
    if player and playerList then
      local ok,people=pcall(playerList.getOnlinePlayers)
      if ok and type(people)=="table" then
        for _,name in ipairs(people) do
          local good,point=pcall(player.getPlayerPos,name)
          if good then transmit("player",name,getVec(point)) end
        end
      end
    end
    -- NeoPeripheral is installed. The argument contract is mod-specific:
    -- invoking with no arguments is optional and protected by pcall.
    if entityRadar then
      local ok,entities=pcall(entityRadar.scanForEntities)
      if ok then scanList("entity",entities) end
      if not playerList and type(entityRadar.scanForPlayers)=="function" then
        local ok2,people=pcall(entityRadar.scanForPlayers)
        if ok2 then scanList("player",people) end
      end
    end
    if shipRadar then
      local ok,ships=pcall(shipRadar.scanForSubLevels)
      if ok then scanList("ship",ships) end
    end
    sleep(0.5)
  end
end
loop()
