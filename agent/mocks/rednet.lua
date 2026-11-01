-- EN: Deterministic multi-computer packet bus with optional packet drops.
-- RU: Шина сообщений между компьютерами с возможностью потери пакетов.
local Bus = {}
Bus.__index = Bus

function Bus.new()
  return setmetatable({ nodes = {}, dropNext = false }, Bus)
end

function Bus:node(id)
  assert(type(id) == 'number' and id >= 0, 'Invalid computer ID')
  local node = { id = id, opened = false, inbox = {} }
  self.nodes[id] = node
  local bus = self
  local api = {}

  function api.open(name)
    assert(type(name) == 'string' and name ~= '', 'Modem name required')
    node.opened = true
  end
  function api.close() node.opened = false end
  function api.isOpen() return node.opened end
  local function transmit(toId, message, protocol)
    if bus.dropNext then
      bus.dropNext = false
      return false
    end
    local destination = bus.nodes[toId]
    if not node.opened or not destination or not destination.opened then return false end
    destination.inbox[#destination.inbox + 1] = {
      sender = id, message = message, protocol = protocol
    }
    return true
  end
  function api.send(toId, message, protocol)
    return transmit(toId, message, protocol)
  end
  function api.broadcast(message, protocol)
    for peerId in pairs(bus.nodes) do
      if peerId ~= id then transmit(peerId, message, protocol) end
    end
  end
  -- EN: Empty inbox returns nil: no real waiting or timeout simulation.
  -- RU: Пустая очередь возвращает nil: ожидание в реальном времени не имитируется.
  function api.receive(protocol, _timeout)
    for i, packet in ipairs(node.inbox) do
      if not protocol or packet.protocol == protocol then
        table.remove(node.inbox, i)
        return packet.sender, packet.message, packet.protocol
      end
    end
    return nil
  end
  return api
end

return Bus
