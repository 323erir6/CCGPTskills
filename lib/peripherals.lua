-- EN: Generic discovery helpers for core and modded peripherals.
-- RU: Поиск стандартной и модифицированной периферии.
local M = {}

function M.inspect()
  local result = {}
  for _, name in ipairs(peripheral.getNames()) do
    local methods = peripheral.getMethods(name) or {}
    table.sort(methods)
    result[#result + 1] = {
      name = name,
      type = peripheral.getType(name),
      methods = methods
    }
  end
  return result
end

-- EN: Validate method availability before interacting with a device.
-- RU: Проверять наличие методов до работы с устройством.
function M.requireMethods(name, required)
  assert(type(name) == "string" and name ~= "", "Invalid peripheral name")
  if not peripheral.isPresent(name) then
    return nil, "Missing peripheral: " .. name
  end
  local available = {}
  for _, method in ipairs(peripheral.getMethods(name) or {}) do
    available[method] = true
  end
  for _, method in ipairs(required or {}) do
    if not available[method] then
      return nil, "Peripheral " .. name .. " lacks method " .. method
    end
  end
  return peripheral.wrap(name)
end

-- EN: Invoke a validated method without assuming the device remains attached.
-- RU: Вызвать метод, учитывая возможное отключение периферии.
function M.safeCall(name, method, ...)
  if not peripheral.isPresent(name) then
    return false, "Peripheral detached: " .. name
  end
  return pcall(peripheral.call, name, method, ...)
end

return M
