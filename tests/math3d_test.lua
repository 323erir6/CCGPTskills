-- EN: Basic deterministic tests for reusable geometry helpers.
-- RU: Детерминированные тесты геометрических функций.
local M = require("lib.math3d")
local function near(a, b)
  assert(math.abs(a - b) < 1e-7, tostring(a) .. " != " .. tostring(b))
end

near(M.wrapDegrees(360), 0)
near(M.wrapDegrees(190), -170)
near(M.shortestError(-179, 179), 2)
near(M.length(M.vec(3, 4, 0)), 5)
near(M.distance(M.vec(0, 0, 0), M.vec(0, 3, 4)), 5)
near(M.forwardSpeed(M.vec(10, 0, 0), M.vec(2, 0, 0)), 10)
near(M.blocksPerSecondToKmh(10), 36)
local v = assert(M.velocityFromSamples(M.vec(0, 0, 0), M.vec(10, 0, 0), 2))
near(v.x, 5)
assert(M.velocityFromSamples(M.vec(0,0,0), M.vec(1,0,0), 0) == nil)
print("math3d tests passed")
