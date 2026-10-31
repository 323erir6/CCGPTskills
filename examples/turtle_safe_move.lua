-- EN: Conservative forward motion without digging or attacking.
-- RU: Осторожное движение вперёд без копания и атаки.
if not turtle then error("Requires a turtle") end

local steps = tonumber(({...})[1]) or 1
if steps < 1 or steps > 64 or steps % 1 ~= 0 then
  error("Usage: turtle_safe_move <steps 1..64>")
end

local fuel = turtle.getFuelLevel()
-- EN: An "unlimited" fuel setting may return a string.
-- RU: При бесконечном топливе метод может вернуть строку.
if type(fuel) == "number" and fuel < steps then
  error("Not enough fuel for requested route")
end

for i = 1, steps do
  local success, reason = turtle.forward()
  if not success then
    print("Stopped at step " .. i .. ": " .. tostring(reason))
    break
  end
  print("Step", i, "of", steps)
end
