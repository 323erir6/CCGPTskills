-- EN: Small keyboard-controlled menu for a CraftOS terminal.
-- RU: Небольшое меню терминала с управлением с клавиатуры.
local options = { "Show computer ID", "Show uptime", "Exit" }
local selected = 1

local function render()
  local width, height = term.getSize()
  term.setBackgroundColor(colors.black)
  term.setTextColor(colors.white)
  term.clear()
  local title = "CraftOS menu"
  term.setCursorPos(1, 1)
  term.write(title:sub(1, width))
  for i, label in ipairs(options) do
    local y = i + 2
    if y <= height then
      term.setCursorPos(1, y)
      local prefix = selected == i and "> " or "  "
      term.write((prefix .. label):sub(1, width))
    end
  end
end

render()
while true do
  local event, code = os.pullEvent()
  if event == "term_resize" then
    render()
  elseif event == "key" then
    if code == keys.up then selected = (selected - 2) % #options + 1 end
    if code == keys.down then selected = selected % #options + 1 end
    if code == keys.enter then
      if selected == 3 then break end
      local message
      if selected == 1 then
        message = "Computer ID: " .. os.getComputerID()
      else
        message = ("Uptime: %.2fs"):format(os.clock())
      end
      local w, h = term.getSize()
      term.setCursorPos(1, math.min(h, #options + 4))
      term.clearLine()
      term.write(message:sub(1, w))
    else
      render()
    end
    if code == keys.up or code == keys.down then render() end
  end
end
term.setTextColor(colors.white)
term.setBackgroundColor(colors.black)
term.clear()
term.setCursorPos(1, 1)
print("Menu closed")
