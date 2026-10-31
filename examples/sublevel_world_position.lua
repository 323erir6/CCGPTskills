-- EN: Convert a user-defined ship-local coordinate to global world coordinates.
-- RU: Перевести заданную локальную координату корабля в глобальную.
-- EN: Requires CC:Sable 'sublevel' API on a sublevel.
-- RU: Нужен API 'sublevel' CC:Sable на физической конструкции.
local poseMath = require("lib.sublevel_pose")
local round = require("lib.round").round

local localPos = { x=0, y=0, z=0 } -- EN: Edit local coordinates. RU: Изменить локальные координаты.
assert(type(sublevel) == "table", "CC:Sable sublevel API missing")
if not sublevel.isInPlotGrid() then error("Computer is not on a sublevel") end

-- EN: Set to 0.1 seconds, not a busy loop.
-- RU: Интервал 0.1 секунды вместо цикла без паузы.
while true do
  local pose = sublevel.getLogicalPose()
  local world = poseMath.localToWorld(localPos,pose)
  term.setCursorPos(1,1)
  term.clearLine()
  print(("World X: %.2f Y: %.2f Z: %.2f"):format(
    round(world.x,2), round(world.y,2),round(world.z,2)))
  sleep(0.1)
end
