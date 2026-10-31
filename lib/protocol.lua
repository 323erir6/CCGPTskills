-- EN: Small input-validation helpers; not an encryption layer.
-- RU: Проверка структуры пакетов; не является шифрованием.
local M = {}

local MAX_TEXT = 4096

function M.create(kind, requestId, payload)
  assert(type(kind) == "string" and #kind > 0 and #kind <= 64)
  assert(type(requestId) == "string" and #requestId <= 128)
  assert(type(payload) == "table", "Expected payload table")
  return {
    version = 1,
    kind = kind,
    request_id = requestId,
    payload = payload
  }
end

-- EN: This validates the envelope, not application-specific payload fields.
-- RU: Проверяется оболочка пакета, но не внутренние поля приложения.
function M.validate(message, expectedKind)
  if type(message) ~= "table" then return false, "Message is not a table" end
  if message.version ~= 1 then return false, "Unsupported protocol version" end
  if type(message.kind) ~= "string" or #message.kind < 1 or #message.kind > 64 then
    return false, "Invalid kind"
  end
  if expectedKind and message.kind ~= expectedKind then
    return false, "Unexpected kind"
  end
  if type(message.request_id) ~= "string" or #message.request_id > 128 then
    return false, "Invalid request ID"
  end
  if type(message.payload) ~= "table" then return false, "Invalid payload" end
  -- EN: Approximate packet-size guard; also validate all nested fields.
  -- RU: Приблизительная проверка размера; вложенные поля требуют проверки.
  local ok, serialized = pcall(textutils.serialize, message)
  if not ok or #serialized > MAX_TEXT then return false, "Packet too large" end
  return true
end

return M
