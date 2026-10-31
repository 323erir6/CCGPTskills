# CC:AR — CC integration

**Exact archive file:** `cc_ar-0.2.1.jar`.

## Functionality and behavior

The AR controller supports persistent identified 2D and 3D elements, a label and explicit update. Some draw methods take coordinates plus color and strings; see source bytecode for exact positional argument types before use. 3D elements use world/AR coordinate conventions specific to the add-on, not CraftOS monitor character cells. Do not confuse this with Tom's GPU.

## Peripheral/class method index

| Java peripheral or API family | Declared method candidates |
| --- | --- |
| `ARControllerPeripheral` | `drawLine3D(id,color,x1,y1,z1,x2,y2,z2), drawLine2D(id,color,x1,y1,x2,y2), drawItemIcon2D(...), drawItemIcon3D(...), drawText2D(...), drawText3D(...), drawRect2D(...), delete(id), clear(), setLabel(label), getAllElements(), setAnchor(...), update()` |

## On-device verification

```lua
for _,name in ipairs(peripheral.getNames()) do
  local methods=peripheral.getMethods(name) or {}
  table.sort(methods)
  print(name,peripheral.getType(name))
  print(table.concat(methods,", "))
end
```

This program is read-only and requires no additional API besides CC:Tweaked.

## Evidence and limits

Method names are extracted from Java classes of the **exact installed JAR** with `javap`. A class method is not proof of Lua visibility: annotations, generic adapters, wrapped block entities, runtime flags and other mods determine exposed interfaces. The table includes **method candidates** and deliberately omits Java internals such as constructors, `getType`, `equals`, `getTarget` and `attach`. Method return shapes must be inspected on-device. All nontrivial actuator behavior needs testing on the target build.
