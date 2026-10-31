-- EN: Pure geometric helpers; all distances use caller-selected units.
-- RU: Геометрические функции; единицы расстояния задаются вызывающим кодом.
local M = {}

function M.clamp(value, low, high)
  assert(type(value) == "number" and low <= high, "Invalid clamp arguments")
  return math.max(low, math.min(high, value))
end

-- EN: Normalize degrees to the half-open interval [-180, 180).
-- RU: Нормализовать градусы к полуинтервалу [-180, 180).
function M.wrapDegrees(degrees)
  assert(type(degrees) == "number", "Angle must be a number")
  return (degrees + 180) % 360 - 180
end

function M.shortestError(target, current)
  return M.wrapDegrees(target - current)
end

function M.vec(x, y, z)
  return { x = x, y = y, z = z }
end

function M.subtract(a, b)
  return M.vec(a.x - b.x, a.y - b.y, a.z - b.z)
end

function M.add(a, b)
  return M.vec(a.x + b.x, a.y + b.y, a.z + b.z)
end

function M.scale(v, factor)
  return M.vec(v.x * factor, v.y * factor, v.z * factor)
end

function M.dot(a, b)
  return a.x * b.x + a.y * b.y + a.z * b.z
end

function M.length(v)
  return math.sqrt(M.dot(v, v))
end

-- EN: Return nil if length is too small for a meaningful direction.
-- RU: Возвратить nil, если длина слишком мала для определения направления.
function M.normalize(v, epsilon)
  epsilon = epsilon or 1e-9
  local len = M.length(v)
  if len <= epsilon then return nil end
  return M.scale(v, 1 / len)
end

function M.distance(a, b)
  return M.length(M.subtract(a, b))
end

-- EN: Direction convention: 0 deg is +Z, positive angles turn toward +X.
-- RU: Направление: 0 град. вдоль +Z, положительный угол к +X.
function M.headingFromDelta(dx, dz)
  return math.deg(math.atan(dx, dz))
end

-- EN: Derive world velocity from two positions sampled in seconds.
-- RU: Вычислить мировую скорость по позициям и времени в секундах.
function M.velocityFromSamples(previous, current, dt)
  if type(dt) ~= "number" or dt <= 1e-6 then
    return nil, "dt must be greater than 1e-6 seconds"
  end
  return M.scale(M.subtract(current, previous), 1 / dt)
end

function M.forwardSpeed(worldVelocity, worldForward)
  local forward = M.normalize(worldForward)
  if not forward then return nil, "Forward vector has zero length" end
  return M.dot(worldVelocity, forward)
end

function M.blocksPerSecondToKmh(value)
  return value * 3.6
end

return M
