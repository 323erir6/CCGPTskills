"""Headless functional blocks for version-pinned Minecraft NeoForge modpack.

Source of signatures: exact installed JARs (see mod_devices_manifest.json).
Do NOT treat simplified motor dynamics / resource use as native mod equivalence.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from math import cos, sin, radians, pi, sqrt, isfinite
from typing import Any, ClassVar
from .geometry import Vector, add, sub, mul, cross, dot, quaternion_axes, norm

DIRECTIONS = {
    "east": (1., 0., 0.), "west": (-1., 0., 0.),
    "up": (0., 1., 0.), "down": (0., -1., 0.),
    "south": (0., 0., 1.), "north": (0., 0., -1.),
}


def clamp(x, lo, hi):
    x = number(x)
    return max(lo, min(hi, x))


def number(x):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not isfinite(x):
        raise ValueError("finite numeric argument required")
    return float(x)


def rotate_local(v: Vector, quaternion: tuple) -> Vector:
    axes = quaternion_axes(quaternion)
    return tuple(sum(axes[j][i] * v[j] for j in range(3)) for i in range(3))


def axis_from_state(state: dict) -> Vector:
    return DIRECTIONS.get(str(state.get("facing", state.get("axis_direction", "north"))).lower(), (0., 0., -1.))


def atmospheric_factor(is_air_breathing: bool, pressure: float, bonus: float) -> float:
    """Port of AtmosphericThrustMath.calculateFactor from createpropulsion-1.1.5.jar.

    The JAR accepts pressure in [0,1], bonus in [0,2]; its isAirBreathing
    branch scales vacuum thrust from 0.2..1 before the bonus application.
    """
    p = clamp(pressure, 0., 1.)
    b = clamp(bonus, 0., 2.)
    if is_air_breathing:
        base = clamp(1. - .8 * p, .2, 1.)
    else:
        base = 1. + (1. - p) * .15
    return clamp(1. + (base - 1.) * b, .05, 5.)


def ion_powered_fraction(requested_fe: int, required_fe: int, received_fe: int) -> float:
    """Literal IonThrusterEnergyMath.poweredFraction bytecode (argument positions)."""
    if requested_fe <= 0: return 0.
    if required_fe <= 0: return 1.
    return clamp(received_fe / required_fe, 0., 1.)


@dataclass
class FunctionalDevice:
    key: str
    block_id: str
    body_id: int
    block_pos: tuple[int, int, int]
    properties: dict = field(default_factory=dict)
    cc_type: str | None = None
    accuracy: str = "state_only"
    last_force: Vector = (0., 0., 0.)
    last_torque: Vector = (0., 0., 0.)
    tick_count: int = 0
    METHODS: ClassVar[tuple] = ()

    def call(self, name: str, *arguments):
        if name not in self.METHODS:
            raise AttributeError(f"{self.cc_type or self.block_id} does not expose {name}")
        return getattr(self, name)(*arguments)

    def methods(self):
        return sorted(self.METHODS)

    def physics_step(self, runtime, dt):
        self.last_force = self.last_torque = (0., 0., 0.)

    def tick(self, runtime):
        self.tick_count += 1

    def snapshot(self):
        return {"key": self.key, "block": self.block_id, "body_id": self.body_id,
                "local_pos": self.block_pos, "type": self.cc_type,
                "accuracy": self.accuracy, "last_force": self.last_force,
                "last_torque": self.last_torque, "ticks": self.tick_count}

    def _force(self, runtime, local_force: Vector, offset: Vector | None = None):
        body = runtime.world.bodies[self.body_id]
        world_force = rotate_local(local_force, body.orientation)
        center = tuple(self.block_pos[i] + .5 for i in range(3))
        if offset is not None: center = add(center, offset)
        rel = sub(center, body.com)
        at = add(body.position, rotate_local(rel, body.orientation))
        world_torque = cross(sub(at, body.position), world_force)
        runtime.world.step_force(self.body_id, world_force,
                                 world_point=at, source=self.key)
        self.last_force = world_force
        self.last_torque = world_torque


class PropulsionThruster(FunctionalDevice):
    """Actual CC contract, source-derived atmospheric and FE fractions.

    Exact thrust output and fuel burn require device-specific configuration;
    set them explicitly instead of silently inventing per-block values.
    """
    METHODS = ("getObstruction", "setPower", "setPowerNormalized", "getPower",
               "getCurrentThrustPN", "getCurrentThrustKN", "getDisplayedThrustPN",
               "getDisplayedThrustKN", "getAirflowMs")

    def __init__(self, *args, kind="thruster", max_thrust_pn=None,
                 fuel_amount=0., fuel_capacity=0., fuel_per_second=None,
                 energy_fe=0., energy_capacity_fe=0., energy_per_second=None,
                 air_breathing=False, atmospheric_bonus=0., **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = kind
        self.cc_type = kind
        self.accuracy = "source_math+approximate_dynamics"
        self.max_thrust_pn = None if max_thrust_pn is None else number(max_thrust_pn)
        self.fuel_amount = number(fuel_amount)
        self.fuel_capacity = number(fuel_capacity)
        self.fuel_per_second = None if fuel_per_second is None else number(fuel_per_second)
        self.energy_fe = number(energy_fe)
        self.energy_capacity_fe = number(energy_capacity_fe)
        self.energy_per_second = None if energy_per_second is None else number(energy_per_second)
        self.air_breathing = bool(air_breathing)
        self.atmospheric_bonus = number(atmospheric_bonus)
        self.peripheral_connected = False
        self.throttle = 0.
        self.redstone_signal = 0
        self.obstruction = 0
        self.vector_x = self.vector_y = 0.
        self.target_vector_x = self.target_vector_y = 0.
        self.config_thrust = 0
        self.custom_thrust_pn = None
        self.airflow_ms = 0.
        self.last_effective_thrust = 0.
        if kind in ("vector_thruster", "liquid_vector_thruster", "creative_vector_thruster"):
            self.METHODS = ("getVectorX", "getVectorY", "getTargetVectorX", "getTargetVectorY",
                            "setVectorX", "setVectorY", "setVector", "setThrust", "setThrustNormalized",
                            "setPower", "setPowerNormalized", "getThrust", "getPower")
            if kind == "creative_vector_thruster":
                self.METHODS += ("setThrustOutput", "clearThrustOutput", "getMaxThrustOutputPn",
                                 "isCustomThrustOutputActive")
            if kind == "liquid_vector_thruster":
                self.METHODS += ("tanks", "pushFluid", "pullFluid")
        else:
            self.METHODS = tuple(self.METHODS)
            if kind == "thruster":
                self.METHODS += ("getFuelAmountMb", "getFuelCapacityMb", "tanks", "pushFluid", "pullFluid")
            elif kind == "ion_thruster":
                self.METHODS += ("getEnergyAmountFe", "getEnergyCapacityFe")
            elif kind == "solid_fuel_thruster":
                self.METHODS += ("getFuelAmount", "getFuelCapacity", "getBurnTimeRemaining",
                                 "isBurning", "list", "pushItems", "pullItems")
            elif kind == "creative_thruster":
                self.METHODS += ("setThrustConfig", "getThrustConfig", "getTargetThrustPN", "getTargetThrustKN")

    def set_redstone(self, signal: int):
        self.redstone_signal = int(clamp(signal, 0, 15))

    def attach(self):
        self.peripheral_connected = True
        self.throttle = 0.

    def detach(self):
        self.peripheral_connected = False
        self.throttle = 0.

    def getObstruction(self):return self.obstruction
    def setPower(self, value):self.attach_if_required();self.throttle = int(clamp(value, 0, 15)) / 15.
    def setPowerNormalized(self, value):self.attach_if_required();self.throttle = clamp(value, 0., 1.)
    def attach_if_required(self):
        if not self.peripheral_connected:self.attach()
    def getPower(self):return self.throttle if self.peripheral_connected else self.redstone_signal / 15.
    def getCurrentThrustPN(self):return self.last_effective_thrust
    def getCurrentThrustKN(self):return self.last_effective_thrust / 1000.
    def getDisplayedThrustPN(self):return self.last_effective_thrust
    def getDisplayedThrustKN(self):return self.last_effective_thrust / 1000.
    def getAirflowMs(self):return self.airflow_ms
    def tanks(self):
        return {1: {"amount":int(self.fuel_amount),"capacity":int(self.fuel_capacity)}}
    def pushFluid(self,*args):raise NotImplementedError("CC fluid transfer requires network inventory simulation")
    def pullFluid(self,*args):raise NotImplementedError("CC fluid transfer requires network inventory simulation")
    def list(self):return {1:{"count":int(self.fuel_amount)}}
    def pushItems(self,*args):raise NotImplementedError("CC inventory transfer requires item transport")
    def pullItems(self,*args):raise NotImplementedError("CC inventory transfer requires item transport")
    def getFuelAmountMb(self):return int(self.fuel_amount)
    def getFuelCapacityMb(self):return int(self.fuel_capacity)
    def getEnergyAmountFe(self):return int(self.energy_fe)
    def getEnergyCapacityFe(self):return int(self.energy_capacity_fe)
    def getFuelAmount(self):return int(self.fuel_amount)
    def getFuelCapacity(self):return int(self.fuel_capacity)
    def getBurnTimeRemaining(self):return int(self.fuel_amount)
    def isBurning(self):return self.last_effective_thrust > 0.
    def setThrustConfig(self, value):self.config_thrust = int(clamp(value, 0, 1000000))
    def getThrustConfig(self):return self.config_thrust
    def getTargetThrustPN(self):return (self.max_thrust_pn or 0.) * self.getPower()
    def getTargetThrustKN(self):return self.getTargetThrustPN() / 1000.
    def getVectorX(self):return self.vector_x
    def getVectorY(self):return self.vector_y
    def getTargetVectorX(self):return self.target_vector_x
    def getTargetVectorY(self):return self.target_vector_y
    def setVectorX(self, value):self.target_vector_x = clamp(value, -1, 1)
    def setVectorY(self, value):self.target_vector_y = clamp(value, -1, 1)
    def setVector(self, x, y):self.setVectorX(x);self.setVectorY(y)
    def setThrust(self, power):self.setPower(power)
    def setThrustNormalized(self, power):self.setPowerNormalized(power)
    def getThrust(self):return int(round(self.getPower() * 15))
    def setThrustOutput(self, value):self.custom_thrust_pn = max(0., number(value))
    def clearThrustOutput(self):self.custom_thrust_pn = None
    def getMaxThrustOutputPn(self):return self.max_thrust_pn or 0.
    def isCustomThrustOutputActive(self):return self.custom_thrust_pn is not None

    def physics_step(self, runtime, dt):
        super().physics_step(runtime, dt)
        max_force = self.custom_thrust_pn if self.custom_thrust_pn is not None else self.max_thrust_pn
        if max_force is None:
            self.last_effective_thrust = 0.
            runtime.unresolved.add(self.key + ": missing config max_thrust_pn")
            return
        power = self.getPower()
        if self.obstruction:power *= max(0., 1. - self.obstruction / 100.)
        is_creative = self.kind.startswith("creative_")
        if not is_creative and self.kind in ("thruster", "liquid_vector_thruster", "solid_fuel_thruster"):
            if self.fuel_amount <= 0.:power = 0.
            if self.fuel_per_second is None and power:
                runtime.unresolved.add(self.key + ": unknown fuel consumption; thrust suppressed")
                power = 0.
        if self.kind in ("ion_thruster", "vector_thruster"):
            if self.energy_fe <= 0.:power = 0.
            if self.energy_per_second is None and power:
                runtime.unresolved.add(self.key + ": unknown FE consumption; thrust suppressed")
                power = 0.
        thrust = max_force * power * atmospheric_factor(self.air_breathing, runtime.air_pressure,
                                                        self.atmospheric_bonus)
        if not is_creative and self.fuel_per_second is not None and self.kind in (
                "thruster", "liquid_vector_thruster", "solid_fuel_thruster"):
            use = min(self.fuel_amount, self.fuel_per_second * power * dt)
            self.fuel_amount -= use
        if self.energy_per_second is not None and self.kind in ("ion_thruster", "vector_thruster"):
            use = min(self.energy_fe, self.energy_per_second * power * dt)
            self.energy_fe -= use
        self.last_effective_thrust = thrust
        if thrust <= 0.:return
        direction = axis_from_state(self.properties)
        # Vector gimbals use independent pitch/yaw targeting. Slew rate must be
        # taken from real JAR; explicit approximation here uses 0.2/tick.
        if self.kind in ("vector_thruster", "liquid_vector_thruster", "creative_vector_thruster"):
            delta = min(1., dt * 20 * .2)
            self.vector_x += (self.target_vector_x - self.vector_x) * delta
            self.vector_y += (self.target_vector_y - self.vector_y) * delta
            # Relative to the facing direction; vector components are approximate.
            direction = (self.vector_x, -self.vector_y, sqrt(max(0.,1.-self.vector_x**2-self.vector_y**2)))
            if self.properties.get("facing") == "north":direction=mul(direction, -1)
            direction = mul(direction, 1./max(norm(direction), 1e-9))
        self._force(runtime, mul(direction, thrust))

    def snapshot(self):
        data = super().snapshot()
        data.update(throttle=self.getPower(),redstone=self.redstone_signal,
                    peripheral_connected=self.peripheral_connected,
                    thrust_pn=self.last_effective_thrust,
                    fuel_mb=self.fuel_amount,energy_fe=self.energy_fe,
                    vector=[self.vector_x,self.vector_y])
        return data


class AeronauticsPropeller(FunctionalDevice):
    """Thrust = configThrust * directionIndependentSpeed, from Aero 1.3.2 bytecode."""
    def __init__(self, *args, config_thrust=1., config_airflow=.1,
                 reversed=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.cc_type = None
        self.accuracy = "source_math+approximate_force_application"
        self.config_thrust=number(config_thrust)
        self.config_airflow=number(config_airflow)
        self.kinetic_rpm=0.
        self.rotation_speed=0.
        self.reversed=bool(reversed)
        self.thrust=0.

    def set_rpm(self, value):self.kinetic_rpm=clamp(value,-256.,256.)
    def tick(self,runtime):
        super().tick(runtime)
        # Exact Aero tick-side smoothing coefficient 0.15.
        self.rotation_speed += (self.kinetic_rpm * .3 - self.rotation_speed) * .15

    def physics_step(self,runtime,dt):
        super().physics_step(runtime,dt)
        facing=self.properties.get("facing", "north")
        sign = -1. if self.reversed else 1.
        speed = self.rotation_speed * 3.3333333 * sign
        self.thrust = self.config_thrust * speed
        if not self.thrust:return
        self._force(runtime,mul(DIRECTIONS.get(facing, (0,0,-1)),self.thrust))

    def snapshot(self):
        d=super().snapshot();d.update(rpm=self.kinetic_rpm,rot_speed=self.rotation_speed,
                                       thrust=self.thrust,airflow=self.config_airflow*self.rotation_speed*3.3333333)
        return d


class AeroPropellerBearing(AeronauticsPropeller):
    """Version 1.3.2 thrust scales with sailPower**1.5, not linearly."""
    def __init__(self, *args, sail_power=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.sail_power = sail_power
        self.accuracy = "source_thrust_formula+approximate_sail_count"

    def physics_step(self,runtime,dt):
        FunctionalDevice.physics_step(self,runtime,dt)
        if self.sail_power is None:
            self.thrust=0.
            runtime.unresolved.add(self.key+": bearing requires computed sail power from assembled blocks")
            return
        facing=self.properties.get("facing","north")
        sp=number(self.sail_power)
        if sp<0:raise ValueError("sail power cannot be negative")
        sign=-1. if self.reversed else 1.
        speed=self.rotation_speed*3.3333333*sign
        self.thrust = sp**1.5*speed*self.config_thrust
        if self.thrust:self._force(runtime,mul(DIRECTIONS.get(facing,(0,0,-1)),self.thrust))

    def snapshot(self):
        d=super().snapshot();d["sail_power"]=self.sail_power
        return d


class SynaxisMotor(FunctionalDevice):
    """Version-correct peripheral signatures; PID drive remains a test approximation."""
    METHODS=("setGainP","setGainI","setGainD","setPID","getGainP","getGainI","getGainD",
             "setTarget","GetTarget","setMode","getMode","setGravityCompensation",
             "getGravityCompensation","collect")
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.cc_type="synaxis_dynamic_motor"
        self.accuracy="verified_CC_contract+approximate_servo"
        self.target=0.;self.angle=0.;self.speed=0.
        self.p=1.;self.i=0.;self.d=0.
        self.integral=0.;self.angle_mode=True;self.gravity_compensation=False
        self.max_speed=4.;self.max_acceleration=20.

    def setGainP(self,x):self.p=number(x)
    def setGainI(self,x):self.i=number(x)
    def setGainD(self,x):self.d=number(x)
    def setPID(self,p,i,d):self.setGainP(p);self.setGainI(i);self.setGainD(d)
    def getGainP(self):return self.p
    def getGainI(self):return self.i
    def getGainD(self):return self.d
    def setTarget(self,x):self.target=number(x)
    def GetTarget(self):return self.target
    def setMode(self,x):self.angle_mode=bool(x)
    def getMode(self):return self.angle_mode
    def setGravityCompensation(self,x):self.gravity_compensation=bool(x)
    def getGravityCompensation(self):return self.gravity_compensation
    def collect(self):return {"target":self.target,"gainP":self.p,"gainI":self.i,
                              "gainD":self.d,"angleMode":self.angle_mode,
                              "eliminateGravity":self.gravity_compensation}
    def physics_step(self,runtime,dt):
        super().physics_step(runtime,dt)
        error=(self.target-self.angle) if self.angle_mode else self.target-self.speed
        self.integral=clamp(self.integral+error*dt,-100.,100.)
        desired=clamp(self.p*error+self.i*self.integral-self.d*self.speed,-self.max_speed,self.max_speed)
        delta=clamp(desired-self.speed,-self.max_acceleration*dt,self.max_acceleration*dt)
        self.speed+=delta
        self.angle+=self.speed*dt
    def snapshot(self):
        d=super().snapshot();d.update(target_rad=self.target,angle_rad=self.angle,
                                       angular_speed=self.speed,angle_mode=self.angle_mode,
                                       p=self.p,i=self.i,d=self.d)
        return d


class SynaxisJet(FunctionalDevice):
    METHODS=("setTrust","getTrust","setHorizontalAngle","getHorizontalAngle",
             "setVerticalAngle","getVerticalAngle","collect")
    def __init__(self,*args,max_thrust_pn=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.cc_type="synaxis_jet";self.accuracy="verified_CC_contract+approximate_physics"
        self.trust=0.;self.horizontal=0.;self.vertical=0.
        self.max_thrust_pn=max_thrust_pn
    def setTrust(self,x):self.trust=clamp(x,0.,1.)
    def getTrust(self):return self.trust
    def setHorizontalAngle(self,x):self.horizontal=number(x)
    def getHorizontalAngle(self):return self.horizontal
    def setVerticalAngle(self,x):self.vertical=number(x)
    def getVerticalAngle(self):return self.vertical
    def collect(self):return {"trust":self.trust,"horizontalAngle":self.horizontal,
                              "verticalAngle":self.vertical}
    def physics_step(self,runtime,dt):
        super().physics_step(runtime,dt)
        if self.max_thrust_pn is None:
            runtime.unresolved.add(self.key+": Synaxis jet maximum thrust not source-calibrated")
            return
        h,v=self.horizontal,self.vertical
        direction=(sin(h)*cos(v),sin(v),cos(h)*cos(v))
        self._force(runtime,mul(direction,self.trust*number(self.max_thrust_pn)))


class ReactionWheel(FunctionalDevice):
    """Source-discovered reaction-wheel block with explicit test torque capacity.

    Rotational dynamics are driven through the schematic body's inertia; exact
    Create Propulsion power demand and torque curves need source validation.
    """
    def __init__(self,*args,max_torque=None,axis=(0.,1.,0.),**kwargs):
        super().__init__(*args,**kwargs)
        self.max_torque=max_torque
        self.axis=tuple(axis)
        self.command=0.
        self.accuracy="approximate_torque_with_explicit_capacity"
    def set_command(self,value):self.command=clamp(value,-1,1)
    def physics_step(self,runtime,dt):
        super().physics_step(runtime,dt)
        if self.max_torque is None:
            runtime.unresolved.add(self.key+": reaction wheel torque is unknown")
            return
        value=mul(self.axis,number(self.max_torque)*self.command)
        body=runtime.world.bodies[self.body_id]
        torque=rotate_local(value,body.orientation)
        runtime.world.step_torque(self.body_id,torque,source=self.key)
        self.last_torque=torque
    def snapshot(self):
        d=super().snapshot();d.update(command=self.command,max_torque=self.max_torque)
        return d


class ConfiguredActuator(FunctionalDevice):
    """Generic model for source-identified mod thrust/buoyancy machines.

    No guessed force constants: requires explicit max_force calibration.
    """
    def __init__(self,*args,max_force=None,resource_level=None,
                 fuel_per_second=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.max_force=max_force
        self.throttle=0.
        self.resource_level=resource_level
        self.fuel_per_second=fuel_per_second
        self.accuracy="approximate_force_explicitly_configured"
    def set_throttle(self,value):self.throttle=clamp(value,0,1)
    def physics_step(self,runtime,dt):
        super().physics_step(runtime,dt)
        if self.max_force is None:
            runtime.unresolved.add(self.key+": no source-calibrated force configured")
            return
        if self.resource_level is not None and self.resource_level<=0:return
        if self.resource_level is not None and self.fuel_per_second is None:
            runtime.unresolved.add(self.key+": fuel consumption rate missing")
            return
        if self.resource_level is not None:
            self.resource_level=max(0.,self.resource_level-number(self.fuel_per_second)*self.throttle*dt)
        self._force(runtime,mul(axis_from_state(self.properties),number(self.max_force)*self.throttle))
    def snapshot(self):
        d=super().snapshot();d.update(throttle=self.throttle,max_force=self.max_force,
                                       resource=self.resource_level)
        return d


class HydraulicActuator(FunctionalDevice):
    """Linear travel actuator for automated integration-test scenarios."""
    def __init__(self,*args,max_travel=1.,speed=0.2,**kwargs):
        super().__init__(*args,**kwargs)
        self.max_travel=number(max_travel);self.speed=number(speed)
        self.position=0.;self.target=0.
        self.accuracy="approximate_state_machine"
    def set_target(self,value):self.target=clamp(value,0,self.max_travel)
    def physics_step(self,runtime,dt):
        super().physics_step(runtime,dt)
        self.position+=clamp(self.target-self.position,-self.speed*dt,self.speed*dt)
    def snapshot(self):
        d=super().snapshot();d.update(linear_position=self.position,target=self.target)
        return d


class SynaxisFlap(FunctionalDevice):
    METHODS=("setAngle","getAngle","setTilt","getTilt","assemble","disassemble")
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.cc_type="compact_flap"
        self.angle=0.;self.tilt=0.;self.assembled=False
    def setAngle(self,x):self.angle=number(x)
    def getAngle(self):return self.angle
    def setTilt(self,x):self.tilt=number(x)
    def getTilt(self):return self.tilt
    def assemble(self):self.assembled=True
    def disassemble(self):self.assembled=False
    def snapshot(self):
        d=super().snapshot();d.update(angle=self.angle,tilt=self.tilt,
                                       assembled=self.assembled)
        return d


class SynaxisResistor(FunctionalDevice):
    METHODS=("getRatio","setRatio")
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.cc_type="synaxis_kinetic_resistor";self.ratio=0.
    def setRatio(self,x):self.ratio=clamp(x,0.,1.)
    def getRatio(self):return self.ratio


class SynaxisAnchor(FunctionalDevice):
    METHODS=("setAirResistance","getAirResistance","setExtraGravity","getExtraGravity",
             "setRotationalResistance","getRotationalResistance","collect")
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.cc_type="synaxis_anchor";self.air=0.;self.extra=0.;self.rotation=0.
    def setAirResistance(self,x):self.air=number(x)
    def getAirResistance(self):return self.air
    def setExtraGravity(self,x):self.extra=number(x)
    def getExtraGravity(self):return self.extra
    def setRotationalResistance(self,x):self.rotation=number(x)
    def getRotationalResistance(self):return self.rotation
    def collect(self):return {"airResistance":self.air,"extraGravity":self.extra,
                              "rotationalResistance":self.rotation}


class Transmission(FunctionalDevice):
    METHODS=("getTransmissionMode","setTransmissionMode","getShiftLevel","setShiftLevel")
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.cc_type="redstone_transmission"
        self.mode="passive";self.level=0
    def getTransmissionMode(self):return self.mode
    def setTransmissionMode(self,mode):
        if not isinstance(mode,str) or not mode:raise ValueError("mode required")
        self.mode=mode
    def getShiftLevel(self):return self.level
    def setShiftLevel(self,x):self.level=int(clamp(x,0,15))


class SwivelBearing(FunctionalDevice):
    METHODS=("getTargetAngle","getTargetAngleRad")
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.cc_type="swivel_bearing";self.target=0.
    def getTargetAngle(self):return self.target*180/pi
    def getTargetAngleRad(self):return self.target
    def set_control_target(self,value):self.target=number(value)


class TiltAdapter(FunctionalDevice):
    METHODS=("getLeftSignal","getRightSignal","setTargetAngle")
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.cc_type="tilt_adapter";self.left=0.;self.right=0.;self.target=0.
    def getLeftSignal(self):return self.left
    def getRightSignal(self):return self.right
    def setTargetAngle(self,x):self.target=number(x)
    def snapshot(self):
        d=super().snapshot();d.update(left_signal=self.left,right_signal=self.right,
                                      target_angle=self.target)
        return d


class AeroWorksServo(FunctionalDevice):
    """Servo block state for Aeroworks 1.5.0, no source-verified joint solver."""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.target=0.;self.angle=0.;self.rate=0.5
        self.accuracy="approximate_state_machine"
    def set_target_degrees(self,value):self.target=number(value)
    def physics_step(self,runtime,dt):
        super().physics_step(runtime,dt)
        diff=self.target-self.angle
        self.angle+=clamp(diff,-self.rate*dt,self.rate*dt)
    def snapshot(self):
        d=super().snapshot();d.update(angle_degrees=self.angle,target_degrees=self.target)
        return d


class AnalogTransmission(FunctionalDevice):
    """Simulated analog transmission signal state; kinetic network not implemented."""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.signal=0;self.direction=-1;self.rpm=0.
        self.accuracy="state_only_no_create_kinetic_network"
    def set_redstone(self,level):
        self.signal=int(clamp(level,0,15))
    def snapshot(self):
        d=super().snapshot();d.update(redstone_signal=self.signal,direction=self.direction,
                                      rpm=self.rpm)
        return d


class KineticSpeedController(FunctionalDevice):
    """Model a configured Create RPM target, not source-verified stress propagation."""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.rpm=0.;self.overstressed=False
        self.accuracy="state_only_no_create_kinetic_network"
    def set_rpm(self,value):self.rpm=clamp(value,-256,256)
    def snapshot(self):
        d=super().snapshot();d.update(rpm=self.rpm,overstressed=self.overstressed)
        return d


class SignalPID(FunctionalDevice):
    """Discrete PID test component, not a port of Synaxis Cimulink runtime."""
    def __init__(self,*args,kp=1.,ki=0.,kd=0.,**kwargs):
        super().__init__(*args,**kwargs)
        self.kp=number(kp);self.ki=number(ki);self.kd=number(kd)
        self.target=0.;self.input=0.;self.output=0.;self.integral=0.;self.previous_error=0.
        self.accuracy="generic_PID_approximation"
    def set_input(self,value):self.input=number(value)
    def set_target(self,value):self.target=number(value)
    def physics_step(self,runtime,dt):
        super().physics_step(runtime,dt)
        err=self.target-self.input
        self.integral=clamp(self.integral+err*dt,-100.,100.)
        self.output=self.kp*err+self.ki*self.integral+self.kd*(err-self.previous_error)/dt
        self.previous_error=err
    def snapshot(self):
        d=super().snapshot();d.update(input=self.input,target=self.target,output=self.output)
        return d


DEVICE_FACTORIES={
    "createpropulsion:thruster":(PropulsionThruster,{"kind":"thruster"}),
    "createpropulsion:ion_thruster":(PropulsionThruster,{"kind":"ion_thruster"}),
    "createpropulsion:creative_thruster":(PropulsionThruster,{"kind":"creative_thruster"}),
    "createpropulsion:vector_thruster":(PropulsionThruster,{"kind":"vector_thruster"}),
    "createpropulsion:liquid_vector_thruster":(PropulsionThruster,{"kind":"liquid_vector_thruster"}),
    "createpropulsion:creative_vector_thruster":(PropulsionThruster,{"kind":"creative_vector_thruster"}),
    "createpropulsion:solid_fuel_thruster":(PropulsionThruster,{"kind":"solid_fuel_thruster"}),
    "createpropulsion:redstone_transmission":(Transmission,{}),
    "createpropulsion:tilt_adapter":(TiltAdapter,{}),
    "createpropulsion:reaction_wheel":(ReactionWheel,{}),
    "synaxis:dynamic_joint_motor":(SynaxisMotor,{}),
    "synaxis:dynamic_revolute_motor":(SynaxisMotor,{}),
    "synaxis:jet":(SynaxisJet,{}),
    "synaxis:propeller":(ConfiguredActuator,{}),
    "synaxis:jet_rudder":(ConfiguredActuator,{}),
    "synaxis:hydraulic_linear_actuator":(HydraulicActuator,{}),
    "synaxis:compact_flap":(SynaxisFlap,{}),
    "synaxis:kinetic_resistor":(SynaxisResistor,{}),
    "synaxis:anchor":(SynaxisAnchor,{}),
    "synaxis:cimulink_pid_controller":(SignalPID,{}),
    "simulated:swivel_bearing":(SwivelBearing,{}),
    "simulated:analog_transmission":(AnalogTransmission,{}),
    "aeroworks:mechanical_servo":(AeroWorksServo,{}),
    "aeroworks:stepper_servo":(AeroWorksServo,{}),
    "aeroengineering:missile_thruster":(ConfiguredActuator,{}),
    "aeroengineering:engine_propeller":(ConfiguredActuator,{}),
    "aeroengineering:airflow_nozzle":(ConfiguredActuator,{}),
    "create:rotation_speed_controller":(KineticSpeedController,{}),
    "simulated:portable_engine":(KineticSpeedController,{}),
    "aeronautics:adjustable_burner":(ConfiguredActuator,{}),
    "aeronautics:steam_vent":(ConfiguredActuator,{}),
    "aeronautics:wooden_propeller":(AeronauticsPropeller,{"config_thrust":1.,"config_airflow":.1}),
    "aeronautics:andesite_propeller":(AeronauticsPropeller,{"config_thrust":1.,"config_airflow":.1}),
    "aeronautics:smart_propeller":(AeronauticsPropeller,{"config_thrust":1.,"config_airflow":.1}),
    "aeronautics:propeller_bearing":(AeroPropellerBearing,{"config_thrust":.2,"config_airflow":.05}),
    "aeronautics:gyroscopic_propeller_bearing":(AeroPropellerBearing,{"config_thrust":.2,"config_airflow":.05}),
}

# Create: Simulated portable engines are registered as sixteen color variants in
# the installed 1.3.2 JAR, not as an unsuffixed 'portable_engine' block.
for _color in ("white","orange","magenta","light_blue","yellow","lime","pink","gray",
               "light_gray","cyan","purple","blue","brown","green","red","black"):
    DEVICE_FACTORIES["simulated:"+_color+"_portable_engine"]=(KineticSpeedController,{})
DEVICE_FACTORIES.pop("simulated:portable_engine",None)
