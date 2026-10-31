# Networking and message protocols

## Rednet

Rednet provides messages over modems. Open an attached modem first, typically by calling `rednet.open(sideOrName)`; a wireless modem is required for wireless peers. `rednet.send(id, payload, protocol)` sends to one computer; `rednet.receive(protocol, timeout)` returns sender, payload and protocol (or `nil` on timeout).

**Rednet does not authenticate or encrypt messages.** Sender IDs are not proof of identity.

## Protocol design

A stable application envelope should contain:

```lua
{
  version = 1,
  kind = "status",
  request_id = "example-001",
  payload = { state = "ready" }
}
```

Check every received value before use: table type, version, `kind`, required fields, expected ranges and message size.

Use protocol namespaces such as `"example.status.v1"` to avoid unrelated traffic. Avoid automatic execution of received code and never use `load` on arbitrary network strings.

## Failure handling

- Add timeouts to request/response interactions.
- Use request IDs to match responses.
- Treat duplicate packets as possible; make state changes idempotent where appropriate.
- Validate device discovery and modem presence.
- Consider reconnect or retry paths after a timeout.
- Limit retries to avoid flooding the network.

## Modem channel API

The lower-level `modem.open(channel)`, `modem.transmit(channel, replyChannel, value)` and `modem_message` events are useful when direct channel control is required. These are distinct from Rednet.

## HTTP

HTTP calls depend on CraftOS configuration and configured domain access. Handle unsuccessful requests and always close response handles.

Sources: https://tweaked.cc/module/rednet.html and https://tweaked.cc/peripheral/modem.html
