-- EN: In-memory CC:Tweaked peripheral registry. Functions use dot calls like CraftOS.
-- RU: Реестр периферии в памяти. Вызовы через точку, как в CraftOS.
local Registry = {}
Registry.__index = Registry

local function sortedNames(devices)
  local result = {}
  for name in pairs(devices) do result[#result + 1] = name end
  table.sort(result)
  return result
end

function Registry.new()
  return setmetatable({ devices = {} }, Registry)
end

function Registry:attach(name, typeName, methods)
  assert(type(name) == 'string' and name ~= '', 'Invalid device name')
  assert(type(typeName) == 'string' and typeName ~= '', 'Invalid device type')
  assert(type(methods) == 'table', 'Methods must be a table')
  self.devices[name] = {typeName = typeName, methods = methods}
end

function Registry:detach(name)
  self.devices[name] = nil
end

function Registry:api()
  local devices = self.devices
  local registry = self
  local api = {}
  function api.getNames() return sortedNames(devices) end
  function api.isPresent(name) return devices[name] ~= nil end
  function api.getType(name) return devices[name] and devices[name].typeName or nil end
  function api.getMethods(name)
    local dev = devices[name]
    if not dev then return nil end
    local result = {}
    for method, func in pairs(dev.methods) do
      if type(func) == 'function' then result[#result + 1] = method end
    end
    table.sort(result)
    return result
  end
  function api.call(name, method, ...)
    local dev = devices[name]
    if not dev then error('No such peripheral: ' .. tostring(name), 2) end
    local fn = dev.methods[method]
    if type(fn) ~= 'function' then error('No such method: ' .. tostring(method), 2) end
    return fn(...)
  end
  function api.wrap(name)
    local dev = devices[name]
    if not dev then return nil end
    local wrapper = {}
    for nameOfMethod in pairs(dev.methods) do
      local method = nameOfMethod
      if type(dev.methods[method]) == 'function' then
        wrapper[method] = function(...) return api.call(name, method, ...) end
      end
    end
    return wrapper
  end
  function api.find(typeName, filter)
    for _, name in ipairs(sortedNames(devices)) do
      if devices[name].typeName == typeName then
        local peripheralObject = api.wrap(name)
        if not filter or filter(name, peripheralObject) then
          return peripheralObject, name
        end
      end
    end
    return nil
  end
  return api
end

return Registry
