-- EN: Redstone mock recording output transitions and enforcing side/level ranges.
-- RU: Имитация redstone с историей переключений и проверкой допустимых значений.
local M = {}
M.__index = M
local SIDES = {left=true,right=true,front=true,back=true,top=true,bottom=true}
function M.new()
  return setmetatable({outputs={}, analog={}, history={}}, M)
end
function M:api()
  local selfRef = self
  local api = {}
  function api.setOutput(side,value)
    assert(SIDES[side] and type(value)=='boolean','Invalid digital output')
    selfRef.outputs[side] = value
    selfRef.history[#selfRef.history+1] = {'digital', side, value}
  end
  function api.getOutput(side) assert(SIDES[side]); return selfRef.outputs[side] or false end
  function api.setAnalogOutput(side,value)
    assert(SIDES[side] and type(value)=='number' and value%1==0 and value>=0 and value<=15,'Invalid analog output')
    selfRef.analog[side] = value
    selfRef.history[#selfRef.history+1] = {'analog', side, value}
  end
  function api.getAnalogOutput(side) assert(SIDES[side]); return selfRef.analog[side] or 0 end
  return api
end
return M
