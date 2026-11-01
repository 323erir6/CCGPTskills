-- Passive OSPREY laboratory telemetry. No commands, targets or actuators.
local P = {}
P.CHANNEL = 'osprey_diagnostics_v1'
P.VERSION = 1

local function finite(n)
  return type(n)=='number' and n==n and n~=math.huge and n~=-math.huge
end
local function vector(v)
  return type(v)=='table' and finite(v.x) and finite(v.y) and finite(v.z)
end
local function quaternion(q)
  if not (type(q)=='table' and finite(q.x) and finite(q.y)
          and finite(q.z) and finite(q.w)) then return false end
  local norm = q.x*q.x + q.y*q.y + q.z*q.z + q.w*q.w
  return norm>=0.9025 and norm<=1.1025
end
local function bounded(s, maxlen)
  return type(s)=='string' and #s>0 and #s<=maxlen
end

function P.validate(p, expectedVehicle)
  if type(p)~='table' or p.ver~=P.VERSION or p.type~='diagnostic' then
    return false,'schema'
  end
  -- Defense in depth: reject attempts to smuggle operational commands.
  if p.command~=nil or p.target~=nil or p.launch~=nil or p.payload~=nil then
    return false,'commands_not_supported'
  end
  if not bounded(p.vehicle,64) or not bounded(p.session,80) then return false,'identity' end
  if expectedVehicle and p.vehicle~=expectedVehicle then return false,'vehicle' end
  if not (finite(p.seq) and p.seq>=0 and p.seq%1==0 and p.seq<2147483648
      and finite(p.elapsed_s) and p.elapsed_s>=0) then return false,'sequence' end
  if p.status=='ok' then
    if not (vector(p.pos) and vector(p.velocity)
      and vector(p.angular_velocity) and quaternion(p.orientation)) then
      return false,'sensor_fields'
    end
  elseif p.status=='sensor_error' then
    if p.pos~=nil or p.orientation~=nil or p.velocity~=nil
      or p.angular_velocity~=nil then return false,'stale_sensor_fields' end
    if p.error~=nil and not bounded(p.error,80) then return false,'error_field' end
  else return false,'status' end
  return true,nil
end

function P.newState(vehicle)
  assert(bounded(vehicle,64),'invalid expected vehicle')
  return {vehicle=vehicle,session=nil,last_seq=-1,last_elapsed=-1,
          received_at=nil,last_frame=nil,accepted=0,rejected=0}
end

function P.accept(s,p,receivedAt)
  assert(type(s)=='table','state required')
  assert(finite(receivedAt) and receivedAt>=0,'valid local receive time required')
  local ok,reason=P.validate(p,s.vehicle)
  if not ok then s.rejected=s.rejected+1;return false,reason end
  if s.session~=nil and s.session~=p.session then
    -- Do not accept a new session until the old one has been silent for 10s.
    if s.received_at~=nil and receivedAt-s.received_at<10 then
      s.rejected=s.rejected+1;return false,'session_conflict'
    end
    s.last_seq=-1;s.last_elapsed=-1
  end
  if p.seq<=s.last_seq or p.elapsed_s<s.last_elapsed then
    s.rejected=s.rejected+1;return false,'out_of_order'
  end
  s.session=p.session
  s.last_seq=p.seq
  s.last_elapsed=p.elapsed_s
  s.received_at=receivedAt
  s.last_frame=p
  s.accepted=s.accepted+1
  return true,nil
end

function P.health(s,now,timeout)
  assert(finite(now) and now>=0 and finite(timeout) and timeout>0)
  if not s.last_frame then return 'no_data' end
  if now-s.received_at>timeout then return 'stale' end
  return s.last_frame.status
end

function P.frame(vehicle,session,seq,elapsed,pose,velocity,omega)
  local p={ver=P.VERSION,type='diagnostic',vehicle=vehicle,session=session,
           seq=seq,elapsed_s=elapsed,status='sensor_error'}
  if type(pose)=='table' and vector(pose.position)
       and quaternion(pose.orientation) and vector(velocity) and vector(omega) then
    p.status='ok';p.pos=pose.position;p.orientation=pose.orientation
    p.velocity=velocity;p.angular_velocity=omega
  else p.error='invalid_or_unavailable_sable_data' end
  local valid,err=P.validate(p)
  assert(valid,'cannot serialize bad frame: '..tostring(err))
  return p
end

function P.speed(v)
  if not vector(v) then return nil end
  return math.sqrt(v.x*v.x+v.y*v.y+v.z*v.z)
end
return P
