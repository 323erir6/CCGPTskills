-- EN: Enumerate all peripheral names, types and method signatures.
-- RU: Вывести имена периферии, типы и доступные методы.
local names = peripheral.getNames()
table.sort(names)
if #names == 0 then
  print("No peripherals detected")
  return
end

for _, name in ipairs(names) do
  print("[" .. name .. "]")
  print("Type: " .. tostring(peripheral.getType(name)))
  local methods = peripheral.getMethods(name) or {}
  table.sort(methods)
  for _, method in ipairs(methods) do
    print("  " .. method)
  end
end
