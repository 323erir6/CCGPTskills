-- EN: Dependency-free stable JSON for textual test reports.
-- RU: JSON без зависимостей для текстовых отчётов тестирования.
local M={}
local function encode(value,depth)
  depth=depth or 0
  assert(depth<=32,"JSON nesting limit")
  local t=type(value)
  if t=="nil" then return "null" end
  if t=="boolean" then return value and "true" or "false" end
  if t=="number" then
    assert(value==value and math.abs(value)<math.huge,"non-finite number")
    return string.format("%.15g",value)
  end
  if t=="string" then
    return '"'..value:gsub('[%z\1-\31\\"]',function(c)
      return ({['\\']='\\\\',['"']='\\"',['\n']='\\n',['\r']='\\r',['\t']='\\t'})[c]
        or string.format("\\u%04x",string.byte(c))
    end)..'"'
  end
  assert(t=="table","unsupported JSON type "..t)
  local maxIndex,keys,n=0,{},0
  local isArray=true
  for k in pairs(value) do
    n=n+1
    if type(k)~="number" or k<1 or k%1~=0 then
      isArray=false
    else
      maxIndex=math.max(maxIndex,k)
    end
  end
  if isArray and maxIndex==n then
    local out={}
    for i=1,maxIndex do out[#out+1]=encode(value[i],depth+1) end
    return "["..table.concat(out,",").."]"
  end
  for k in pairs(value) do
    assert(type(k)=="string","JSON object needs string keys")
    keys[#keys+1]=k
  end
  table.sort(keys)
  local out={}
  for _,k in ipairs(keys) do
    out[#out+1]=encode(k,depth+1)..":"..encode(value[k],depth+1)
  end
  return "{"..table.concat(out,",").."}"
end
function M.encode(x) return encode(x) end
return M
