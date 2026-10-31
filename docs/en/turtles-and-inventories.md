# Turtles, inventories and storage automation

## Turtle movement

The turtle API is available only on turtle computers. Key commands: `forward`, `back`, `up`, `down`, `turnLeft`, `turnRight`, `inspect`, `getFuelLevel`, `select` and `getItemDetail`.

Movement returns a success flag and often a reason. Always check the result. Avoid assuming that a command moved the turtle. Check numeric fuel limits before starting multi-step routes; fuel may be reported as `"unlimited"`.

Be conservative about digging or interacting with the world: use `inspect`, request bounded routes and stop on obstacles by default.

## Inventory peripheral

A compatible inventory exposes `size()`, `list()`, `getItemDetail(slot)`, `pushItems(toName, fromSlot, limit, toSlot)`, and `pullItems(fromName, fromSlot, limit, toSlot)`. Not all containers are exposed, and method support depends on configuration and peripheral providers.

Inventory `list()` returns a sparse slot-keyed table: iterate with `pairs`, not `ipairs`. Never assume every slot is occupied.

When transferring items, check source/destination names, permissions and returned moved count. Do not assume the transfer succeeded.

## Testing

Start with one container and single-item moves. Verify the slot indexes and the actual output inventory after each operation. For mobile turtles, verify the final world position before extending the route.

Sources: https://tweaked.cc/module/turtle.html and https://tweaked.cc/generic_peripheral/inventory.html
