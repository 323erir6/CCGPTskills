# User interfaces and input

Vanilla CC:Tweaked terminals and monitors are character-cell devices, not pixel GPUs. Coordinates are 1-based, and layout should be computed from `getSize()` on every resize.

## Rendering

Use `term.setCursorPos(x, y)`, `term.write(text)` and `term.clear()` for the local display. A wrapped monitor exposes compatible output methods, plus `setTextScale(scale)`. If necessary, use `term.redirect(monitor)`, but restore the original terminal after completing redirected output.

Avoid clearing and repainting a display for every unrelated event. Update only changed lines where practical.

## Input

- Terminal: `mouse_click`, `mouse_drag`, `mouse_scroll`, `key`, `char`, `paste`.
- Advanced monitor: `monitor_touch` returns monitor name and touch coordinates.
- Resizing: `term_resize` and `monitor_resize`.

Validate touch coordinates against current `getSize()`. Treat the screen as absent when its peripheral detaches.

## Color

Advanced terminal capabilities differ from monochrome computers. Check `term.isColor()` or the target display's capabilities before relying on palettes.

## External GPUs

Third-party GPU peripherals may use different resolutions, coordinate origins, draw APIs, frame synchronization and input events. Their contract must be read from the installed mod instead of assuming terminal behavior.

Sources: https://tweaked.cc/module/term.html and https://tweaked.cc/peripheral/monitor.html
