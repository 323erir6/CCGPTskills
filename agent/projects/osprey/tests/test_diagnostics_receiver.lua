local realDofile=dofile
local realP,realR,realO,realT,realPrint=peripheral,rednet,os,term,print
local P=realDofile('diagnostics_protocol.lua')
local frames={}
local pose={position={x=10,y=80,z=20},orientation={x=0,y=0,z=0,w=1}}
frames[1]=P.frame('LAB','test-session',0,.1,pose,{x=2,y=0,z=0},{x=0,y=0,z=0})
frames[2]=frames[1] -- replayed message must be rejected
frames[3]=P.frame('LAB','test-session',1,.2,pose,{x=2,y=0,z=0},{x=0,y=0,z=0})
frames[4]=P.frame('LAB','test-session',2,.3,nil,nil,nil)
frames[5]={ver=1,type='diagnostic',vehicle='LAB',session='test-session',seq=3,
           elapsed_s=.4,status='ok',command='launch'}
local loop=0
local output={}
local arOutput={}
local txCalls=0
os={clock=function()return loop<=5 and loop or 20 end}
peripheral={
  getNames=function()return {'modem_0','ar_0'} end,
  hasType=function(_,kind)return kind=='modem' end,
  wrap=function(name)
    if name=='modem_0' then return {isWireless=function()return true end} end
    return {drawText2D=function(...)arOutput[#arOutput+1]='text' end,
            update=function()arOutput[#arOutput+1]='update' end}
  end,
}
rednet={open=function()end,
  send=function()txCalls=txCalls+1;error('forbidden')end,
  broadcast=function()txCalls=txCalls+1;error('forbidden')end,
  receive=function(channel,timeout)
    assert(channel==P.CHANNEL and timeout==.5)
    loop=loop+1
    if loop>6 then error('END_OF_TEST') end
    return loop,frames[loop]
  end}
term={clear=function()end,setCursorPos=function()end}
print=function(s)output[#output+1]=tostring(s) end
dofile=function(name)
  if name=='diagnostics_receiver_config.lua' then return {vehicle='LAB',stale_seconds=3}end
  return realDofile(name)
end
local ok,err=pcall(realDofile,'diagnostics_receiver.lua')
dofile,peripheral,rednet,os,term,print=realDofile,realP,realR,realO,realT,realPrint
assert(not ok and tostring(err):find('END_OF_TEST',1,true),tostring(err))
assert(txCalls==0,'receiver must never transmit')
local all=table.concat(output,'\n')
assert(all:find('Link: ok',1,true),'no valid update shown')
assert(all:find('Link: sensor_error',1,true),'no sensor fault shown')
assert(all:find('Link: stale',1,true),'no stale link shown')
assert(all:find('Packets: 3 ok, 2 rejected',1,true),'packet rejection broken')
assert(#arOutput>0,'AR display was not exercised')
print('OSPREY read-only pocket and AR display integration passed')
