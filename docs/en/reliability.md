# Reliability, validation and secure programming

## Initialization

Check every required peripheral, method, monitor size, file and configuration value before entering a control loop. Report device name, required type and missing methods.

## Runtime

- Catch recoverable peripheral errors with `pcall`; show diagnostic messages.
- Prefer event-driven waits or bounded `sleep` delays over polling at maximum speed.
- Use a clear shutdown path for outputs and connected devices.
- Ensure persisted files are closed and writes have checked failure modes.
- Validate data received from modems and HTTP.
- Use timeouts and finite retry limits for network requests.
- Keep terminal and GUI painting isolated from control logic.
- Avoid huge serialized packets and unnecessarily frequent full-screen redraws.

## Safety of I/O

Do not run downloaded Lua blindly. Treat network messages and on-disk configuration as untrusted input. Never expose keys, tokens or real service credentials in examples. Rednet protocol names and computer IDs are **not** cryptographic authentication.

## Testing matrix

| Area | Scenarios |
| --- | --- |
| Startup | Missing peripheral, wrong type, inaccessible file |
| Networking | Disconnected modem, malformed message, timeout, duplicate response |
| UI | Terminal resize, smaller monitor, invalid touch coordinates |
| Math | Zero distance, angle wrapping, very small `dt`, saturation |
| Lifetime | Restart, termination, peripheral detachment |

## Verification labels

Mark each result as **executed and passed**, **executed and failed**, **reviewed only**, or **not tested**. Static review is not proof of successful execution inside Minecraft.

Sources: https://tweaked.cc/ and https://tweaked.cc/module/rednet.html
