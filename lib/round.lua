-- EN: Decimal rounding with halves away from zero.
-- RU: Округление десятичных чисел; половины от нуля.
local M = {}

function M.round(num, decimals)
  assert(type(num) == "number", "num must be a number")
  decimals = decimals or 0
  assert(type(decimals) == "number" and decimals % 1 == 0, "decimals must be an integer")
  assert(decimals >= -12 and decimals <= 12, "decimals out of supported range")
  local factor = 10 ^ decimals
  if num >= 0 then
    return math.floor(num * factor + 0.5) / factor
  end
  return math.ceil(num * factor - 0.5) / factor
end

return M
