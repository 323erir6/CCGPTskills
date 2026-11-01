-- Run from agent/projects/osprey/lua to preserve relative dofile paths.
local realDofile=dofile
local function scenario(actuate)
  local throttle=0
  local angleCalls=0
  local transmissions=0
  local messages={
    {ver=1,rocket='OSPREY-01',secret='test-token',seq=1,command='SET_TARGET',
     target={kind='marker',pos={x=200,y=301,z=100}}},
    {ver=1,rocket='OSPREY-01',secret='test-token',seq=2,command='LAUNCH'},
  }
  local index=0
  local mocks={}
  for _,name in ipairs({'back','left','right','top'}) do
    mocks[name]={setPowerNormalized=function(v) assert(v==1);throttle=throttle+1 end}
  end
  for _,name in ipairs({'fin_0','fin_1','fin_2','fin_3'}) do
    mocks[name]={setAngle=function(v) assert(type(v)=='number');angleCalls=angleCalls+1 end}
  end
  mocks.wireless={isWireless=function()return true end}
  peripheral={
    getNames=function()return {'wireless'} end,
    hasType=function(name,t)return name=='wireless' and t=='modem' end,
    wrap=function(name)return mocks[name] end
  }
  rednet={
    open=function() end,
    broadcast=function(p)transmissions=transmissions+1 end,
    receive=function()
      index=index+1
      if index <= #messages then return 20,messages[index] end
      error('end of scripted test')
    end
  }
  sublevel={
    getLogicalPose=function()return {position={x=0,y=300,z=0},orientation={x=0,y=0,z=0,w=1}} end,
    getLinearVelocity=function()return {x=0,y=0,z=0} end,
    getAngularVelocity=function()return {x=0,y=0,z=0} end
  }
  local config={rocket='OSPREY-01',secret='test-token',
    engines={'back','left','right','top'},
    fins={pitch_up='fin_0',pitch_down='fin_1',yaw_left='fin_2',yaw_right='fin_3'},
    fin_signs={pitch_up=1,pitch_down=-1,yaw_left=1,yaw_right=-1},
    allow_control=actuate,fin_limit=15,correction_gain=0.8}
  dofile=function(path)
    if path=='config.lua' then return config end
    return realDofile(path)
  end
  local realPrint=print
  local observedEnd=false
  print=function(msg)
    if type(msg)=='string' and msg:find('end of scripted test',1,true) then
      observedEnd=true
    else
      realPrint(msg)
    end
  end
  realDofile('onboard.lua')
  print=realPrint
  dofile=realDofile
  assert(observedEnd,'scripted loop did not finish as expected')
  return throttle,angleCalls
end
local throttle,angles=scenario(false)
assert(throttle==0,'safe default unexpectedly armed propulsion')
assert(angles>=4,'safe default should neutralize fins')
throttle,angles=scenario(true)
assert(throttle==4,'not all test engines started')
assert(angles>=8,'in-game flap command not executed')
print('OSPREY onboard mocked peripheral tests passed')
