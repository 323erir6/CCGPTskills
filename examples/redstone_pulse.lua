-- EN: Turn a redstone output on for a bounded duration.
-- RU: Включить выход редстоуна на ограниченное время.
local args = {...}
local side = args[1] or "back"
local seconds = tonumber(args[2]) or 1
local allowed = {
  left = true, right = true, front = true,
  back = true, top = true, bottom = true
}
if not allowed[side] then error("Invalid side") end
if seconds <= 0 or seconds > 30 then error("Duration must be 0..30 seconds") end

redstone.setOutput(side, false)
local ok, err = pcall(function()
  redstone.setOutput(side, true)
  sleep(seconds)
end)
-- EN: Always turn the output off after normal or caught failures.
-- RU: Отключать выход после штатного завершения или ошибки.
redstone.setOutput(side, false)
if not ok then error(err, 0) end
print("Pulse complete")
