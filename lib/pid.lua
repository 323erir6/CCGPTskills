-- EN: Discrete PID controller with bounded integral and output.
-- RU: Дискретный PID-регулятор с ограничением интеграла и выхода.
local PID = {}
PID.__index = PID

local function clamp(value, low, high)
  return math.max(low, math.min(high, value))
end

-- EN: Gains and limits are application-specific; no universal tuning exists.
-- RU: Коэффициенты и пределы зависят от системы; универсальных настроек нет.
function PID.new(options)
  assert(type(options) == "table", "Expected PID options")
  local self = setmetatable({}, PID)
  self.kp = options.kp or 0
  self.ki = options.ki or 0
  self.kd = options.kd or 0
  self.minOutput = options.minOutput or -math.huge
  self.maxOutput = options.maxOutput or math.huge
  self.minIntegral = options.minIntegral or -math.huge
  self.maxIntegral = options.maxIntegral or math.huge
  self.integral = 0
  self.previousError = nil
  assert(self.minOutput < self.maxOutput, "Invalid output limits")
  assert(self.minIntegral <= self.maxIntegral, "Invalid integral limits")
  return self
end

function PID:reset()
  self.integral = 0
  self.previousError = nil
end

-- EN: Use consistent physical units for error and dt (seconds).
-- RU: Для ошибки и dt (секунды) нужны согласованные единицы.
function PID:step(error, dt)
  assert(type(error) == "number", "Error must be numeric")
  assert(type(dt) == "number" and dt > 0, "dt must be positive")
  local derivative = 0
  if self.previousError ~= nil then
    derivative = (error - self.previousError) / dt
  end

  local oldIntegral = self.integral
  local candidateIntegral = clamp(
    oldIntegral + error * dt, self.minIntegral, self.maxIntegral
  )
  local candidate = self.kp * error + self.ki * candidateIntegral + self.kd * derivative

  -- EN: Roll back integration when saturation would be driven further.
  -- RU: Отменить интегрирование, усиливающее насыщение выхода.
  if (candidate > self.maxOutput and self.ki * error > 0)
    or (candidate < self.minOutput and self.ki * error < 0) then
    self.integral = oldIntegral
  else
    self.integral = candidateIntegral
  end

  self.previousError = error
  local output = self.kp * error + self.ki * self.integral + self.kd * derivative
  return clamp(output, self.minOutput, self.maxOutput)
end

return PID
