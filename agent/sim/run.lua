-- EN: Run a repository-owned deterministic scenario, JSON to standard output.
-- RU: Запуск доверенного сценария репозитория, JSON в стандартный вывод.
local Engine=require("agent.sim.engine")
local JSON=require("agent.sim.text")
local name=assert(arg and arg[1],"usage: lua agent/sim/run.lua agent/scenarios/name.lua")
assert(name:match("^agent/scenarios/[a-zA-Z0-9_-]+%.lua$"),"only repository scenarios permitted")
local loader,err=loadfile(name); assert(loader,err)
local scenario=loader()
assert(type(scenario)=="table","scenario must return table")
local engine=Engine.new(scenario.options)
if scenario.setup then scenario.setup(engine) end
engine:stepTicks(scenario.ticks or 20)
if scenario.assertions then scenario.assertions(engine) end
print(JSON.encode({scenario=name,status="passed",state=engine:snapshot()}))
