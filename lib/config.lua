-- EN: Namespaced persistent settings, stored outside global .settings.
-- RU: Настройки с префиксом, сохраняемые в отдельном файле.
local M = {}
local PREFIX = "cc_library."
local FILE = "cc_library.settings"

settings.define(PREFIX .. "interval", {
  description = "Refresh interval in seconds",
  default = 0.5,
  type = "number"
})
settings.define(PREFIX .. "enabled", {
  description = "Enable periodic display refresh",
  default = true,
  type = "boolean"
})

-- EN: Use explicit file loads and saves to persist values.
-- RU: Для сохранения значений явно вызывать load и save.
function M.load()
  if fs.exists(FILE) then
    return settings.load(FILE)
  end
  return true
end

function M.get()
  return {
    interval = settings.get(PREFIX .. "interval"),
    enabled = settings.get(PREFIX .. "enabled")
  }
end

function M.save(values)
  if type(values) ~= "table" then return false, "Expected table" end
  if values.interval ~= nil then
    if type(values.interval) ~= "number" or values.interval <= 0 then
      return false, "interval must be positive"
    end
    settings.set(PREFIX .. "interval", values.interval)
  end
  if values.enabled ~= nil then
    if type(values.enabled) ~= "boolean" then
      return false, "enabled must be boolean"
    end
    settings.set(PREFIX .. "enabled", values.enabled)
  end
  return settings.save(FILE)
end

return M
