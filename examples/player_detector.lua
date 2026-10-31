-- EN: Optional Advanced Peripherals example with version-aware type names.
-- RU: Пример для Advanced Peripherals с учётом имён в разных версиях.
local detector = peripheral.find("player_detector")
  or peripheral.find("playerDetector")
if not detector then error("Advanced Peripherals Player Detector not found") end

local players = detector.getOnlinePlayers()
if type(players) ~= "table" then error("Unexpected player list") end

for _, username in ipairs(players) do
  local info = detector.getPlayerPos(username)
  if type(info) == "table"
    and type(info.x) == "number"
    and type(info.y) == "number"
    and type(info.z) == "number" then
    print(("%s: %.1f %.1f %.1f"):format(username, info.x, info.y, info.z))
  else
    print(username .. ": position unavailable")
  end
end
