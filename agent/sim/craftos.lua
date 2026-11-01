-- EN: Bounded CC:Tweaked-like Lua runner for trusted simulation programs.
-- RU: Ограниченный запуск Lua-программ с имитацией окружения CC:Tweaked.
local CraftOS={}
function CraftOS.run(engine,node,source,options)
  options=options or {}
  assert(type(source)=="string","Lua source required")
  local output={}
  local limit=options.instructions or 2000000
  assert(type(limit)=="number" and limit>=1000 and limit<=20000000,
    "invalid instruction budget")
  local function log(...)
    local parts={}
    for i=1,select("#",...) do
      parts[#parts+1]=tostring(select(i,...))
    end
    output[#output+1]=table.concat(parts,"\t")
  end
  local osapi={}
  for k,v in pairs(node:os()) do osapi[k]=v end
  osapi.epoch=function(kind)
    assert(kind==nil or kind=="utc" or kind=="local" or kind=="ingame",
      "unsupported epoch type")
    return math.floor(engine.clock.now*1000)
  end
  local sleep=function(seconds)
    assert(type(seconds)=="number" and seconds>=0 and seconds<=3600,
      "invalid sleep")
    engine:stepTicks(math.max(1,math.ceil(seconds*20)))
  end
  -- EN: The fake environment intentionally omits io, package, load and native debug.
  -- RU: В окружение намеренно не переданы io, package, load и системный debug.
  local env={
    assert=assert,error=error,ipairs=ipairs,pairs=pairs,next=next,
    select=select,pcall=pcall,xpcall=xpcall,
    tonumber=tonumber,tostring=tostring,type=type,
    math=math,string=string,table=table,utf8=utf8,
    unpack=table.unpack,print=log,write=log,sleep=sleep,
    os=osapi,peripheral=node.peripheral,rednet=node.rednet,
    redstone=node:redstone(),sublevel=node:sublevel(),
    term={write=log,clear=function() output={} end}
  }
  env._G=env
  local fn,syntax=load(source,"=simulated CraftOS","t",env)
  if not fn then return {ok=false,error=syntax,output=output,steps=0} end
  local used=0
  local function hook()
    used=used+1000
    if used>limit then error("simulation instruction budget exceeded",0) end
  end
  local previous,mask,count=debug.gethook()
  debug.sethook(hook,"",1000)
  local ok,result=pcall(fn)
  debug.sethook(previous,mask,count)
  return {
    ok=ok,error=not ok and tostring(result) or nil,
    output=output,steps=used,simulationTime=engine.clock.now
  }
end
return CraftOS
