-- EN: Simulate a first-order plant with PID; no physical output is driven.
-- RU: Моделирование PID и объекта первого порядка без физического привода.
local PID = require("lib.pid")
local controller = PID.new({
  kp = 2.0, ki = 0.4, kd = 0.2,
  minOutput = -10, maxOutput = 10,
  minIntegral = -20, maxIntegral = 20
})

local position, target = 0, 10
local velocity = 0
local dt = 0.05

for step = 1, 200 do
  local error = target - position
  local command = controller:step(error, dt)
  -- EN: Simple illustrative dynamics: acceleration = command - damping.
  -- RU: Упрощённая динамика: ускорение = команда - сопротивление.
  local acceleration = command - velocity * 1.5
  velocity = velocity + acceleration * dt
  position = position + velocity * dt
  if step % 20 == 0 then
    print(("t=%.1f pos=%.2f command=%.2f"):format(step * dt, position, command))
  end
end
