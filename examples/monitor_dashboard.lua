-- EN: Basic dashboard for a vanilla CC:Tweaked monitor.
-- RU: Простой экран состояния для стандартного монитора CC:Tweaked.
local monitorName
for _, name in ipairs(peripheral.getNames()) do
  if peripheral.getType(name) == "monitor" then
    monitorName = name
    break
  end
end
if not monitorName then error("No monitor attached") end

local monitor = assert(peripheral.wrap(monitorName))
monitor.setTextScale(0.5)

local count = 0
local function render()
  local w, h = monitor.getSize()
  monitor.setBackgroundColor(colors.black)
  monitor.setTextColor(colors.white)
  monitor.clear()

  local lines = {
    "CC:Tweaked dashboard",
    "Computer: " .. os.getComputerID(),
    "Updates: " .. count,
    "Touch to refresh"
  }
  for y, line in ipairs(lines) do
    if y <= h then
      monitor.setCursorPos(1, y)
      monitor.write(line:sub(1, w))
    end
  end
end

render()
local timerId = os.startTimer(1)
while true do
  local event, a = os.pullEvent()
  if (event == "timer" and a == timerId)
    or (event == "monitor_touch" and a == monitorName)
    or (event == "monitor_resize" and a == monitorName) then
    count = count + 1
    render()
    if event == "timer" and a == timerId then
      timerId = os.startTimer(1)
    end
  end
end
