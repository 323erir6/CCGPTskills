-- EN: Display yaw, pitch and roll derived from a Sable quaternion.
-- RU: Показать yaw, pitch и roll, вычисленные из кватерниона Sable.
-- EN: Do not change axis signs without checking the actual body axes.
-- RU: Не менять знаки без проверки ориентации реального корпуса.
local poseMath = require("lib.sublevel_pose")
assert(type(sublevel) == "table", "CC:Sable sublevel API missing")
if not sublevel.isInPlotGrid() then error("Computer is not on a sublevel") end

while true do
  local yaw,pitch,roll = poseMath.yawPitchRoll(sublevel.getLogicalPose())
  term.setCursorPos(1,1)
  term.clearLine()
  term.write(("Yaw %.2f  Pitch %.2f  Roll %.2f"):format(yaw,pitch,roll))
  sleep(0.1)
end
