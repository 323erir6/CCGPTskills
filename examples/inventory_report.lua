-- EN: Report all occupied inventory slots without moving items.
-- RU: Вывести заполненные слоты инвентаря без перемещения предметов.
local name, inv
for _, candidate in ipairs(peripheral.getNames()) do
  -- EN: An inventory can advertise multiple peripheral types.
  -- RU: Инвентарь может предоставлять несколько типов периферии.
  local methods = peripheral.getMethods(candidate) or {}
  local hasList, hasSize = false, false
  for _, method in ipairs(methods) do
    if method == "list" then hasList = true end
    if method == "size" then hasSize = true end
  end
  if hasList and hasSize then
    name = candidate
    inv = peripheral.wrap(candidate)
    break
  end
end
if not inv then error("No compatible inventory attached") end

print("Inventory: " .. name .. " / slots: " .. inv.size())
local items = inv.list()
if type(items) ~= "table" then error("Unexpected item list") end

local slots = {}
for slot in pairs(items) do slots[#slots + 1] = slot end
table.sort(slots)
for _, slot in ipairs(slots) do
  local item = items[slot]
  print(("%d: %s x%d"):format(slot, tostring(item.name), tonumber(item.count) or 0))
end
