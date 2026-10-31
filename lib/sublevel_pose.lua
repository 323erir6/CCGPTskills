-- EN: Sable sublevel pose mathematics, independent of the Minecraft runtime.
-- RU: Математика позы Sable Sub-Level, без зависимости от среды Minecraft.
-- EN: Conventions: quaternion (w,x,y,z), right-handed active rotation,
--     local X/Y/Z, pose.rotationPoint, pose.scale and pose.position.
-- RU: Соглашения: кватернион (w,x,y,z), активный правосторонний поворот,
--     локальные X/Y/Z и поля rotationPoint, scale, position.
local M = {}

local function isNumber(n)
  return type(n) == "number" and n == n and n ~= math.huge and n ~= -math.huge
end

local function validateVector(v, label)
  assert(type(v) == "table" and isNumber(v.x)
    and isNumber(v.y) and isNumber(v.z), "Invalid vector: " .. label)
end

-- EN: Extract and normalize the quaternion from CC:Sable pose.orientation.
-- RU: Извлечь и нормализовать кватернион из pose.orientation CC:Sable.
function M.quaternion(pose)
  assert(type(pose) == "table" and type(pose.orientation) == "table", "Missing orientation")
  local o = pose.orientation
  assert(type(o.v) == "table", "Missing quaternion vector")
  local w, x, y, z = o.a, o.v.x, o.v.y, o.v.z
  assert(isNumber(w) and isNumber(x) and isNumber(y) and isNumber(z),
    "Invalid quaternion components")
  local squared = w*w + x*x + y*y + z*z
  assert(squared > 1e-20, "Zero-length quaternion")
  local inv = 1 / math.sqrt(squared)
  return w*inv, x*inv, y*inv, z*inv
end

-- EN: Rotate a vector by a unit quaternion, preserving vector length.
-- RU: Повернуть вектор единичным кватернионом с сохранением длины.
function M.rotate(v, w, x, y, z)
  validateVector(v, "input")
  local x2, y2, z2 = x*x, y*y, z*z
  return {
    x = v.x*(1-2*(y2+z2)) + v.y*2*(x*y-z*w) + v.z*2*(x*z+y*w),
    y = v.x*2*(x*y+z*w) + v.y*(1-2*(x2+z2)) + v.z*2*(y*z-x*w),
    z = v.x*2*(x*z-y*w) + v.y*2*(y*z+x*w) + v.z*(1-2*(x2+y2))
  }
end

local function validatePose(pose)
  assert(type(pose) == "table", "Expected pose table")
  validateVector(pose.position, "pose.position")
  validateVector(pose.rotationPoint, "pose.rotationPoint")
  validateVector(pose.scale, "pose.scale")
end

-- EN: Global = pose.position + R * ((local - rotationPoint) * scale).
-- RU: Глобальная = pose.position + R * ((локальная - rotationPoint) * scale).
function M.localToWorld(localPos, pose)
  validateVector(localPos, "localPos")
  validatePose(pose)
  local rp, s = pose.rotationPoint, pose.scale
  local q0, q1, q2, q3 = M.quaternion(pose)
  local offset = {
    x = (localPos.x-rp.x)*s.x,
    y = (localPos.y-rp.y)*s.y,
    z = (localPos.z-rp.z)*s.z
  }
  local rotated = M.rotate(offset, q0, q1, q2, q3)
  return {
    x = pose.position.x + rotated.x,
    y = pose.position.y + rotated.y,
    z = pose.position.z + rotated.z
  }
end

-- EN: Inverse transform, invalid for a zero scale on any axis.
-- RU: Обратное преобразование недопустимо при нулевом масштабе любой оси.
function M.worldToLocal(worldPos, pose)
  validateVector(worldPos, "worldPos")
  validatePose(pose)
  local scale = pose.scale
  assert(math.abs(scale.x) > 1e-12 and math.abs(scale.y) > 1e-12
    and math.abs(scale.z) > 1e-12, "Non-invertible zero scale")
  local q0, q1, q2, q3 = M.quaternion(pose)
  local offset = {
    x = worldPos.x-pose.position.x,
    y = worldPos.y-pose.position.y,
    z = worldPos.z-pose.position.z
  }
  local unrotated = M.rotate(offset, q0, -q1, -q2, -q3)
  return {
    x = pose.rotationPoint.x + unrotated.x/scale.x,
    y = pose.rotationPoint.y + unrotated.y/scale.y,
    z = pose.rotationPoint.z + unrotated.z/scale.z
  }
end

-- EN: World direction of a body-local axis (does not include translation).
-- RU: Глобальное направление локальной оси (без переноса).
function M.localDirectionToWorld(direction, pose)
  local w,x,y,z = M.quaternion(pose)
  return M.rotate(direction,w,x,y,z)
end

-- EN: Euler convention matching +Z forward, +X right and +Y up:
--     yaw=atan2(forward.x,forward.z); pitch=asin(forward.y);
--     roll=atan2(right.y,up.y).
-- RU: Углы для +Z вперёд, +X вправо, +Y вверх:
--     yaw=atan2(forward.x,forward.z); pitch=asin(forward.y);
--     roll=atan2(right.y,up.y).
-- EN: At |pitch|=90 deg the reported yaw/roll are convention-dependent.
-- RU: При |pitch|=90° yaw/roll зависят от соглашения (сингулярность).
function M.yawPitchRoll(pose)
  local w,x,y,z = M.quaternion(pose)
  local forwardY = 2*(y*z-x*w)
  local forwardX = 2*(x*z+y*w)
  local forwardZ = 1-2*(x*x+y*y)
  local rightY = 2*(x*y+z*w)
  local upY = 1-2*(x*x+z*z)
  local safe = math.max(-1, math.min(1, forwardY))
  return math.deg(math.atan(forwardX, forwardZ)),
    math.deg(math.asin(safe)),
    math.deg(math.atan(rightY, upY))
end

-- EN: Project world velocity onto a body-local axis (axis is normalized).
-- RU: Спроецировать мировую скорость на нормализованную локальную ось.
function M.speedAlongLocalAxis(worldVelocity, localAxis, pose)
  validateVector(worldVelocity, "worldVelocity")
  local axis = M.localDirectionToWorld(localAxis, pose)
  local len = math.sqrt(axis.x*axis.x+axis.y*axis.y+axis.z*axis.z)
  assert(len > 1e-12, "Zero local axis")
  return (worldVelocity.x*axis.x+worldVelocity.y*axis.y+worldVelocity.z*axis.z)/len
end

return M
