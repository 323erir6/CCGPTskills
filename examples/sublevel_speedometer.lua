-- EN: Global speed and body-forward signed speed from CC:Sable only.
-- RU: Мировая скорость и продольная скорость из одного CC:Sable.
-- EN: Works without player detectors or GPS; axis +Z is configured forward.
-- RU: Без детектора игроков или GPS; локальная ось +Z считается вперёд.
local poseMath = require("lib.sublevel_pose")
local USE_KMH = true -- EN: false = blocks/s. RU: false = блоков/с.
local FORWARD = {x=0,y=0,z=1}

assert(type(sublevel) == "table", "CC:Sable sublevel API missing")
if not sublevel.isInPlotGrid() then error("Computer is not on a sublevel") end

while true do
  local pose = sublevel.getLogicalPose()
  local vel = sublevel.getVelocity()
  -- EN: 'getVelocity' is documented as global; do not use X/Z alone.
  -- RU: 'getVelocity' описана как глобальная; нельзя брать только X/Z.
  local speed = math.sqrt(vel.x*vel.x+vel.y*vel.y+vel.z*vel.z)
  local forward = poseMath.speedAlongLocalAxis(vel, FORWARD, pose)
  local coefficient = USE_KMH and 3.6 or 1
  local unit = USE_KMH and "km/h" or "blocks/s"
  term.setCursorPos(1,1)
  term.clearLine()
  term.write(("Speed %.2f %s"):format(speed*coefficient,unit))
  term.setCursorPos(1,2)
  term.clearLine()
  term.write(("Forward %.2f %s"):format(forward*coefficient,unit))
  sleep(0.1)
end
