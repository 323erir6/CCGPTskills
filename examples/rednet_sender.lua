-- EN: Send a simple status message to a specified computer ID.
-- RU: Отправить сообщение о состоянии компьютеру с указанным ID.
local args = {...}
local target = tonumber(args[1])
if not target or target < 0 or target % 1 ~= 0 then
  error("Usage: rednet_sender <computerId>")
end

local found = false
for _, name in ipairs(peripheral.getNames()) do
  if peripheral.getType(name) == "modem" then
    rednet.open(name)
    found = true
  end
end
if not found then error("No modem attached") end

local message = {
  version = 1,
  kind = "status",
  request_id = tostring(os.getComputerID()) .. "-1",
  payload = { state = "ready" }
}

-- EN: rednet.send reports whether the packet was transmitted, not received.
-- RU: rednet.send подтверждает отправку, а не получение адресатом.
local ok = rednet.send(target, message, "cc-library.status.v1")
print(ok and "Packet sent" or "Packet not sent")
