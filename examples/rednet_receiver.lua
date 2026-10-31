-- EN: Receive and validate namespaced Rednet status messages.
-- RU: Принимать и проверять сообщения Rednet выбранного протокола.
local PROTOCOL = "cc-library.status.v1"

local found = false
for _, name in ipairs(peripheral.getNames()) do
  if peripheral.getType(name) == "modem" then
    rednet.open(name)
    found = true
  end
end
if not found then error("No modem attached") end

print("Computer ID:", os.getComputerID())
print("Listening on", PROTOCOL)

while true do
  local sender, message = rednet.receive(PROTOCOL)
  -- EN: A computer ID is not an authenticated identity.
  -- RU: ID компьютера не является подтверждённой личностью.
  if type(message) == "table"
    and message.version == 1
    and message.kind == "status"
    and type(message.payload) == "table"
    and type(message.payload.state) == "string"
    and #message.payload.state <= 64 then
    print("From " .. sender .. ": " .. message.payload.state)
  else
    print("Ignored malformed packet from", sender)
  end
end
