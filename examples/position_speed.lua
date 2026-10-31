-- EN: Estimate speed from manually supplied world-space positions.
-- RU: Оценить скорость по введённым глобальным координатам.
local math3d = require("lib.math3d")
print("Enter x y z coordinates at two times.")

local function readPoint()
  local line = read()
  local x, y, z = line:match("^%s*([%+%-]?[%d%.]+)%s+([%+%-]?[%d%.]+)%s+([%+%-]?[%d%.]+)%s*$")
  x, y, z = tonumber(x), tonumber(y), tonumber(z)
  if not x or not y or not z then error("Expected three numbers") end
  return math3d.vec(x, y, z)
end

-- EN: os.clock measures Minecraft in-game elapsed time in seconds here.
-- RU: os.clock используется для измерения времени выполнения в секундах.
local first = readPoint()
local t0 = os.clock()
local second = readPoint()
local dt = os.clock() - t0
local v, err = math3d.velocityFromSamples(first, second, dt)
if not v then error(err) end

print(("Velocity X/Y/Z: %.3f %.3f %.3f blocks/s"):format(v.x, v.y, v.z))
print(("Speed: %.3f blocks/s, %.3f km/h"):format(
  math3d.length(v), math3d.blocksPerSecondToKmh(math3d.length(v))
))
