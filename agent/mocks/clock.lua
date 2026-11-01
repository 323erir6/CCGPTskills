-- EN: Deterministic test clock and event queue. Empty queues raise instead of blocking.
-- RU: Детерминированные часы и очередь. Пустая очередь вызывает ошибку, а не блокировку.
local Clock = {}
Clock.__index = Clock

function Clock.new()
  return setmetatable({now = 0, nextTimer = 0, timers = {}, events = {}}, Clock)
end

function Clock:startTimer(seconds)
  assert(type(seconds) == 'number' and seconds >= 0, 'Invalid timer duration')
  self.nextTimer = self.nextTimer + 1
  self.timers[self.nextTimer] = self.now + seconds
  return self.nextTimer
end

function Clock:queueEvent(name, ...)
  assert(type(name) == 'string', 'Invalid event name')
  self.events[#self.events + 1] = {name, ...}
end

function Clock:advance(seconds)
  assert(type(seconds) == 'number' and seconds >= 0, 'Invalid time step')
  self.now = self.now + seconds
  local expired = {}
  for id, deadline in pairs(self.timers) do
    if deadline <= self.now then expired[#expired + 1] = id end
  end
  table.sort(expired)
  for _, id in ipairs(expired) do
    self.timers[id] = nil
    self:queueEvent('timer', id)
  end
end

function Clock:pullEvent(filter)
  while #self.events > 0 do
    local event = table.remove(self.events, 1)
    if not filter or filter == event[1] then
      if event[1] == 'terminate' then error('Terminated', 0) end
      return table.unpack(event)
    end
  end
  error('Mock event queue empty: advance clock or queue an event', 2)
end

function Clock:api()
  local this = self
  return {
    clock = function() return this.now end,
    startTimer = function(seconds) return this:startTimer(seconds) end,
    cancelTimer = function(id) this.timers[id] = nil end,
    pullEvent = function(filter) return this:pullEvent(filter) end,
    queueEvent = function(name, ...) this:queueEvent(name, ...) end,
  }
end

return Clock
