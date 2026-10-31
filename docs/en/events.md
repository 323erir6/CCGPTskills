# Events and cooperative concurrency

CraftOS programs should respond to input, timers and peripherals without starving the event queue.

## Common events

| Event | Arguments after event name |
| --- | --- |
| `timer` | timer ID |
| `rednet_message` | sender ID, message, protocol |
| `modem_message` | side, channel, reply channel, message, distance |
| `monitor_touch` | monitor name, x, y |
| `mouse_click` | button, x, y |
| `key` | key code, held flag |
| `peripheral` | attached device name |
| `peripheral_detach` | detached device name |
| `redstone` | no extra arguments |

## Timers

`local timerID = os.startTimer(1)` requests an event. Other code may schedule timers too, so check `eventTimerID == timerID` before acting.

```lua
local id = os.startTimer(1)
while true do
  local event, value = os.pullEvent()
  if event == "timer" and value == id then
    print("One second elapsed")
    break
  end
end
```

## Parallel

`parallel.waitForAny(functionA, functionB)` returns when any worker finishes; `parallel.waitForAll` waits for all workers. Workers cooperatively yield and event filters are managed separately.

Avoid two independent workers both consuming the same logically exclusive stream without a clear dispatch strategy.

## Lifecycle

Prefer `os.pullEvent` so Ctrl+T can terminate the program. `os.pullEventRaw` suppresses the standard termination behavior and should be reserved for deliberate lifecycle handling.

Use a single event router or small specialized loops; never redraw a complete UI for every unrelated event.

Source: https://tweaked.cc/module/os.html and https://tweaked.cc/module/parallel.html
