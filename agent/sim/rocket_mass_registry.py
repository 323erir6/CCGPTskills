"""Mass-per-block resolution from versioned Sable/NeoForge datapack resources.

The resolver models block tags and Sable PhysicsBlockPropertiesDefinitionLoader
(priority order, per-state overrides); it does NOT execute the Minecraft registry
or account for external world datapacks unless they are supplied explicitly.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import json
import zipfile


class MassRegistry:
    def __init__(self,jars):
        self.jars={name:Path(path) for name,path in jars.items()}
        self.tags=defaultdict(list)
        self.definitions=[]
        self.sources=[]
        self._collect()

    def _collect(self):
        for jar_name, path in self.jars.items():
            with zipfile.ZipFile(path) as archive:
                for filename in archive.namelist():
                    if not filename.startswith('data/') or not filename.endswith('.json'):
                        continue
                    try:
                        body=json.loads(archive.read(filename))
                    except (ValueError, UnicodeError):
                        continue
                    pieces=filename.split('/')
                    if len(pieces)>=5 and pieces[2:4]==['tags','block']:
                        key=pieces[1]+':'+'/'.join(pieces[4:])[:-5]
                        if body.get('replace',False):
                            self.tags[key]=[]
                        for record in body.get('values',[]):
                            entry=record if isinstance(record,str) else record.get('id')
                            if isinstance(entry,str):self.tags[key].append(entry)
                        removals=set(x if isinstance(x,str) else x.get('id')
                                     for x in body.get('remove',[]))
                        if removals:
                            self.tags[key]=[x for x in self.tags[key] if x not in removals]
                    elif len(pieces)==4 and pieces[2]=='physics_block_properties':
                        selector=body.get('selector')
                        if isinstance(selector,str) and 'sable:mass' in body.get('properties',{}):
                            self.definitions.append({'priority':int(body.get('priority',1000)),
                                'selector':selector, 'mass':body['properties']['sable:mass'],
                                'overrides':body.get('overrides',{}),
                                'jar':jar_name,'file':filename})
        self.definitions.sort(key=lambda x:x['priority'])

    def contains(self,tag,block,seen=None):
        if tag.startswith('#'):tag=tag[1:]
        if seen is None:seen=set()
        if tag in seen:return False
        seen=seen|{tag}
        for entry in self.tags.get(tag,[]):
            if entry==block:return True
            if entry.startswith('#') and self.contains(entry[1:],block,seen):return True
        return False

    @staticmethod
    def _state_matches(text,props):
        # Matches Sable condition syntax property=value (comma-separated AND).
        return all(props.get(k.strip())==v.strip() for pair in text.split(',')
                   for k,v in [pair.split('=',1)])

    def mass_of(self,block,props=None):
        props=props or {}
        mass=1.0
        matched=[]
        for definition in self.definitions:
            selector=definition['selector']
            applies=(self.contains(selector[1:],block) if selector.startswith('#')
                     else selector==block)
            if not applies:continue
            mass=float(definition['mass'])
            reason={'file':definition['file'],'jar':definition['jar'],
                    'priority':definition['priority'],'mass':mass,
                    'selector':selector}
            for condition,override in definition['overrides'].items():
                if 'sable:mass' in override and self._state_matches(condition,props):
                    mass=float(override['sable:mass'])
                    reason['override']=condition
                    reason['mass']=mass
            matched.append(reason)
        return {'id':block,'mass':mass,'matched_rules':matched,'default_used':not bool(matched)}

    def report(self,construct):
        records=[]
        for block in construct['blocks']:
            state=construct['palette'][block['state']]
            record=self.mass_of(state['name'],state.get('properties',{}))
            record['pos']=block['pos']
            records.append(record)
        return {'blocks':records,'total_mass':sum(r['mass'] for r in records),
                'source_jars':{name:path.name for name,path in self.jars.items()},
                'limitations':['loaded modpack JAR tag resources only; user/server datapacks can override',
                               'no registry runtime execution or dynamic BlockState rule evaluation']}
