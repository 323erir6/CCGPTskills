-- EN: Headless synthetic free fall; returns a JSON physics snapshot.
-- RU: Текстовый пример условного падения с выводом снимка JSON.
return {
  options={physicsHz=120},ticks=10,
  setup=function(engine)
    for x=-1,1 do for z=-1,1 do engine.world:setBlock(x,0,z,true) end end
    engine.world:addBody({position={x=0,y=4,z=0},mass=2,radius=0.25})
  end,
  assertions=function(engine)
    local b=engine.world:getBody(1)
    assert(b.position.y>1.25 and b.position.y<4,"free fall height")
    assert(b.velocity.y<0,"falling body must accelerate")
    assert(engine.tick==10 and engine.world.steps==60)
  end
}
