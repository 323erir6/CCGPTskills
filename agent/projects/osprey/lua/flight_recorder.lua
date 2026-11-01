-- Read-only CC:Sable flight recorder for a non-destructive physics test.
-- This module never opens rednet or commands engines, control surfaces, or payloads.
local cfg = dofile('recorder_config.lua')
local rate = tonumber(cfg.hz) or 10
local count = tonumber(cfg.samples) or 600
assert(rate >= 1 and rate <= 20 and rate % 1 == 0, 'hz must be integer 1..20')
assert(count >= 2 and count <= 100000 and count % 1 == 0, 'samples must be integer 2..100000')
assert(type(cfg.file) == 'string' and #cfg.file > 0 and #cfg.file < 200, 'invalid log path')
assert(sublevel and type(sublevel.getLogicalPose) == 'function', 'CC:Sable required')
assert(textutils and type(textutils.serializeJSON) == 'function', 'JSON serializer required')

assert(not fs.exists(cfg.file), 'log already exists: choose a fresh recorder_config.lua file path')
local file = assert(fs.open(cfg.file, 'w'), 'cannot open telemetry log')
local start = os.clock()
local function finite(x)
  return type(x) == 'number' and x == x and x ~= math.huge and x ~= -math.huge
end
local function xyz(v)
  return type(v)=='table' and finite(v.x) and finite(v.y) and finite(v.z)
end
local function quat(q)
  if type(q)~='table' or not (finite(q.x) and finite(q.y) and finite(q.z) and finite(q.w)) then
    return false
  end
  local n = q.x*q.x+q.y*q.y+q.z*q.z+q.w*q.w
  return n > .9025 and n < 1.1025
end
local function sample(seq)
  local frame = {schema_version=1,kind='sable_pose',vehicle=tostring(cfg.vehicle or 'LAB-01'),
    seq=seq,t_s=os.clock()-start,status='sensor_error'}
  local ok,pose,v,w = pcall(function()
    return sublevel.getLogicalPose(),sublevel.getLinearVelocity(),sublevel.getAngularVelocity()
  end)
  if ok and type(pose)=='table' and xyz(pose.position) and quat(pose.orientation)
    and xyz(v) and xyz(w) then
    frame.status='ok'
    frame.pos=pose.position
    frame.orientation=pose.orientation
    frame.velocity=v
    frame.angular_velocity=w
  else
    frame.error='invalid_or_unavailable_sensor_data'
  end
  file.writeLine(textutils.serializeJSON(frame))
  file.flush()
end
for seq=0,count-1 do
  sample(seq)
  if seq<count-1 then sleep(1/rate) end
end
file.close()
print('Read-only telemetry log saved: '..cfg.file)
