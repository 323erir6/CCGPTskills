local realDofile=dofile
local realP=peripheral
local realRednet=rednet
local realSublevel=sublevel
local realSleep=sleep
local realOS=os
local realPrint=print
local P=realDofile('diagnostics_protocol.lua')
local calls={}
local sent={}
local time=0
local samples=0
local cmdAccess=0
os={clock=function()time=time+.05;return time end,
    getComputerID=function()return 9 end,epoch=function()return 1000 end}
peripheral={
  getNames=function()return {'modem_2'}end,
  hasType=function(name,kind) return name=='modem_2' and kind=='modem' end,
  wrap=function()return {isWireless=function()return true end}end,
}
rednet={open=function(name)assert(name=='modem_2')end,
  broadcast=function(packet,proto)
    assert(proto==P.CHANNEL)
    sent[#sent+1]=packet
  end,
  receive=function()cmdAccess=cmdAccess+1;error('receiver forbidden')end}
sublevel={
  getLogicalPose=function()
    samples=samples+1
    if samples==3 then return {position={x=1,y=2,z=3}} end
    return {position={x=1,y=2,z=3},orientation={x=0,y=0,z=0,w=1}}
  end,
  getLinearVelocity=function()return {x=0,y=-2,z=0}end,
  getAngularVelocity=function()return {x=0,y=0,z=0}end,
}
sleep=function()end
print=function()end
dofile=function(name)
  if name=='diagnostics_config.lua' then
    return {vehicle='LAB',hz=5,samples=5}
  end
  return realDofile(name)
end
local ok,err=pcall(realDofile,'diagnostics_sender.lua')
dofile,peripheral,rednet,sublevel,sleep,os,print=
  realDofile,realP,realRednet,realSublevel,realSleep,realOS,realPrint
assert(ok,tostring(err))
assert(#sent==5 and cmdAccess==0)
local state=P.newState('LAB')
for i,pkt in ipairs(sent) do
  assert(pkt.seq==i-1 and pkt.session=='diag-9-1000')
  local accepted,why=P.accept(state,pkt,i)
  assert(accepted,tostring(why))
end
assert(sent[3].status=='sensor_error' and not sent[3].pos)
assert(state.accepted==5)
print('OSPREY read-only diagnostics sender integration passed')
