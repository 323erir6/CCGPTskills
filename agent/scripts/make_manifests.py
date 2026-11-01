"""Source-verified registry snapshot generator; run manually after repository audits."""
from pathlib import Path
import json

OUT = Path(__file__).resolve().parents[1] / 'api'

def method(name, arguments, returns, source_path, description=''):
    return {'name': name, 'arguments': arguments, 'returns': returns,
            'verification': 'source-confirmed', 'source_path': source_path,
            'description': description}

def save(mod_id, display, version, repo, commit, interfaces):
    payload = {'schema_version': 1, 'id': mod_id, 'mod': display,
               'version': version, 'minecraft': '1.21.1',
               'source_url': 'https://github.com/323erir6/' + repo,
               'source_commit': commit,
               'interfaces': interfaces}
    (OUT / (mod_id + '.json')).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

src = 'src/main/java/ua/ivan/cbcprogrammablefuzes/peripheral/FuzePeripheralMethods.java'
fuze = [
 ('hasProgrammableFuze', [], ['boolean']),
 ('setProximity', ['number: radius', 'boolean: active'], ['boolean']),
 ('setTimer', ['number: seconds', 'boolean: active'], ['boolean']),
 ('setPersistent', ['boolean: active'], ['boolean']),
 ('setFuzeChannel', ['string: channel'], ['boolean']),
 ('listFuzeProjectiles', ['string: channel'], ['table[]']),
 ('getFuzeTelemetry', ['string: channel','string: uuid'], ['boolean','table?']),
 ('setFuzeProjectileTimer', ['string: channel','string: uuid','number: seconds','boolean: active'], ['boolean']),
 ('setFuzeProjectileProximity', ['string: channel','string: uuid','number: radius','boolean: active'], ['boolean']),
 ('setFuzeProjectilePersistent', ['string: channel','string: uuid','boolean: active'], ['boolean']),
 ('setFuzeProjectileChannel', ['string: channel','string: uuid','string: newChannel'], ['boolean']),
 ('setFuzeProjectileSettings', ['string: channel','string: uuid','number: timerSeconds','boolean: timerActive','number: proximityRadius','boolean: proximityActive','boolean: persistent'], ['boolean']),
 ('hasTrajectoryCorrectionModule', [], ['boolean']),
 ('setCorrectionChannel', ['string: channel'], ['boolean']),
 ('setCorrectionPersistent', ['boolean: active'], ['boolean']),
 ('setImpactCoordinates', ['number: x','number: y','number: z'], ['boolean']),
 ('listCorrectionProjectiles', ['string: channel'], ['table[]']),
 ('getCorrectionTelemetry', ['string: channel','string: uuid'], ['boolean','table?']),
 ('setCorrectionProjectileTarget', ['string: channel','string: uuid','number: x','number: y','number: z'], ['boolean']),
 ('getLoadedProjectileInfo', [], ['boolean','table?']),
 ('getLoadedPropellantInfo', [], ['boolean','table?']),
 ('getCannonInfo', [], ['boolean','table?']),
]
save('cbc_programmable_fuzes','CBC Programmable Fuzes', '1.4.1', 'CBC-Programmable-Fuzes',
     'd3ba2fd8cd0a74facd71c7f9c3718bdb66cc0282',
     [{'name':'programmable_fuze', 'kind':'peripheral',
       'notes':'Additional types: cbc_programmable_fuze; generic peripheral methods may augment CBC mounts.',
       'methods':[method(*item,src) for item in fuze]}])

radar = 'src/main/java/dev/radarcompat/enhanceddetector/mixin/RadarPeripheralMixin.java'
engine = 'src/main/java/dev/radarcompat/enhanceddetector/mixin/SableEnginePeripheralMixin.java'
player = 'src/main/java/dev/radarcompat/enhanceddetector/mixin/PlayerDetectorPrecisionMixin.java'
save('enhanced_detector_radar','Enhanced Detector Radar','1.0.5','Enhanced-Detector-Radar',
     'e14b41b64a0d28871d69ec0bb51a2ee2a2ba1043',[
         {'name':'radar', 'kind':'peripheral', 'notes':'Extends NeoPeripheral scanForSubLevels rows with velocity and size fields. Does not create a new radar type.',
          'methods':[method('scanForSubLevels',['number?: radius','boolean?: absolute'],['table[]'],radar)]},
         {'name':'sable_engine','kind':'peripheral', 'notes':'Extends NeoPeripheral engine; impulses are world-axis impulses, not forces.',
          'methods':[
              method('getPhysicsState',[],['table?'],engine),
              method('applyControlImpulse',['number: lx','number: ly','number: lz','number: ax','number: ay','number: az'],['boolean'],engine),
              method('stepControl',['number: lx','number: ly','number: lz','number: ax','number: ay','number: az'],['table?'],engine)]},
         {'name':'playerDetector', 'kind':'peripheral', 'notes':'Enhances Advanced Peripherals getPlayerPos default precision to 3 decimal places. Exact type name is version-dependent.',
          'methods':[method('getPlayerPos',['string: username','number?: precision'],['table?'],player)]}
     ])

syncsrc = 'src/main/java/dev/sableccticksync/SableSyncApi.java'
save('sable_cc_tick_sync','Sable CC Tick Sync','1.6.4','Sable-CC-Tick-Sync',
     '32ed09ce8e8944ee20b3787b547971617003fafb',
     [{'name':'sableSync','kind':'global','methods':[
         method('isHighFrequency',[],['boolean'],syncsrc),
         method('getPhysicsFrequency',[],['number'],syncsrc)]}])

msrc = 'src/main/java/dev/mianbaosablecompat/peripheral/ExplosivePeripheral.java'
save('mianbao_sable_explosion_compat','Mianbao Sable Explosion Compat','1.2.9','MianbaoSableExplosionCompat',
     '2335b47b2fb4cf9cee9375424d8b22b5f83ae401',
     [{'name':'explosive','kind':'peripheral','methods':[
         method('detonate',[],['boolean'],msrc)]}])

print('Created source-verified manifests')
