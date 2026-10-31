-- EN: Set an analog redstone output briefly and reset to zero.
-- RU: Кратковременно установить аналоговый выход и сбросить его в ноль.
local args = {...}
local side = args[1] or "back"
local level = tonumber(args[2]) or 8
local seconds = tonumber(args[3]) or 2
local allowed = {
  left = true, right = true, front = true,
  back = true, top = true, bottom = true
}
if not allowed[side] then error("Invalid side") end
if level < 0 or level > 15 or level % 1 ~= 0 then
  error("Level must be an integer in 0..15")
end
if seconds < 0 or seconds > 30 then error("Duration must be 0..30") end

redstone.setAnalogOutput(side, 0)
local ok, err = pcall(function()
  redstone.setAnalogOutput(side, level)
  sleep(seconds)
end)
redstone.setAnalogOutput(side, 0)
if not ok then error(err, 0) end
print("Analog output reset")
