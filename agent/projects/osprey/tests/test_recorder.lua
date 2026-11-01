-- Tests the independent read-only CC:Sable recorder with fake sensors.
local realDofile = dofile
local realClock = os.clock
local realPrint = print
local realFS = fs
local realSublevel = sublevel
local realTextutils = textutils
local realSleep = sleep
local realPeripheral = peripheral
local realRednet = rednet

local records = {}
local sampleId = 0
local fakeTime = 0
local closed = false
local usedStorage = false
os.clock = function()
  fakeTime = fakeTime + .1
  return fakeTime
end
fs = {
  exists=function()return false end,
  open=function(name,mode)
    assert(name=='instrumentation_test.jsonl')
    assert(mode=='w', 'recorder must not append to an existing file')
    usedStorage=true
    return {
      writeLine=function(frame) records[#records+1]=frame end,
      flush=function()end,
      close=function()closed=true end,
    }
  end,
}
sublevel = {
  getLogicalPose=function()
    sampleId = sampleId + 1
    if sampleId==2 then return {position={x=0,y=300,z=0}} end
    return {position={x=0,y=180,z=0},orientation={x=0,y=0,z=0,w=1}}
  end,
  getLinearVelocity=function()return {x=0,y=-1,z=0} end,
  getAngularVelocity=function()return {x=0,y=0,z=0} end,
}
textutils={serializeJSON=function(frame)return frame end}
sleep=function()end
peripheral = {getNames=function() error('forbidden peripheral access') end}
rednet = {open=function()error('forbidden rednet access')end,
          broadcast=function()error('forbidden rednet access')end}
dofile=function(name)
  if name == 'recorder_config.lua' then
    return {hz=10,samples=3,file='instrumentation_test.jsonl',vehicle='LAB-01'}
  end
  return realDofile(name)
end
print=function()end
local ok,err=pcall(realDofile,'flight_recorder.lua')
-- Always restore the global CC APIs even if a test assertion fails.
dofile,os.clock,print,fs,sublevel,textutils,sleep,peripheral,rednet =
  realDofile,realClock,realPrint,realFS,realSublevel,realTextutils,realSleep,realPeripheral,realRednet
assert(ok, tostring(err))
assert(usedStorage and closed and #records==3, 'not all frames were flushed')
assert(records[1].status=='ok' and records[1].seq==0)
assert(records[2].status=='sensor_error' and not records[2].pos)
assert(records[3].status=='ok' and records[3].seq==2)
assert(records[1].t_s < records[2].t_s and records[2].t_s < records[3].t_s)
print('OSPREY read-only CC:Sable recorder test passed')
