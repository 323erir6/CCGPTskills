-- EN: Verify PID proportional response, reset and output saturation.
-- RU: Проверка P-компонента, сброса и ограничения выхода PID.
local PID = require("lib.pid")

local p = PID.new({ kp = 2, minOutput = -4, maxOutput = 4 })
assert(p:step(1, 0.1) == 2)
assert(p:step(10, 0.1) == 4)
assert(p:step(-10, 0.1) == -4)
p:reset()
assert(p:step(0, 0.1) == 0)

local i = PID.new({
  ki = 1, minIntegral = -2, maxIntegral = 2,
  minOutput = -1, maxOutput = 1
})
for _ = 1, 20 do
  local out = i:step(10, 0.1)
  assert(out <= 1 and out >= -1)
end
assert(i.integral <= 2)
print("pid tests passed")
