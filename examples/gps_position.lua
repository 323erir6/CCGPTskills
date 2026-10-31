-- EN: GPS requires a wireless modem and configured GPS hosts.
-- RU: Для GPS нужен беспроводной модем и настроенные GPS-хосты.
local x, y, z = gps.locate(5)
if not x then
  print("GPS position unavailable")
  return
end
print(("World position: %.2f %.2f %.2f"):format(x, y, z))
