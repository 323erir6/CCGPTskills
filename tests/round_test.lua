-- EN: Verify half-away-from-zero decimal rounding.
-- RU: Проверить округление десятичных чисел от нуля.
local round = require("lib.round").round
assert(round(1.235,2) == 1.24)
assert(round(-1.235,2) == -1.24)
assert(round(1.234,2) == 1.23)
assert(round(-1.234,2) == -1.23)
assert(round(145,-1) == 150)
assert(round(-145,-1) == -150)
print("round tests passed")
