#!/usr/bin/env python3
"""Inventory blockstate resources from real 1.21.1 mod JARs.

Output is data-only. A model is never assumed from a matching block-name suffix.
The source artifacts are supplied locally, not checked into GitHub.
"""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
from agent.sim.mod_devices import DEVICE_FACTORIES


def audit_jar_files(jars: list[Path]) -> dict:
    artifacts=[];blocks={}
    for path in sorted(jars,key=lambda p:p.name):
        if not zipfile.is_zipfile(path):
            raise ValueError(f"invalid JAR: {path}")
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        with zipfile.ZipFile(path) as jar:
            names=sorted(n for n in jar.namelist()
                if n.startswith("assets/") and "/blockstates/" in n and n.endswith(".json"))
            ids=[]
            for name in names:
                parts=name.split("/")
                if len(parts)!=4 or parts[2]!="blockstates":continue
                id=parts[1]+":"+parts[3][:-5]
                ids.append(id)
                obj=blocks.setdefault(id,{"id":id,"sources":[],"model":"unsupported"})
                obj["sources"].append(path.name)
                if id in DEVICE_FACTORIES:
                    cls,_=DEVICE_FACTORIES[id]
                    obj["model"]=cls.__name__
            artifacts.append({"file":path.name,"sha256":sha,"registered_blockstates":len(ids)})
    models=set(DEVICE_FACTORIES)
    return {
        "schema_version":1,"target":"Minecraft 1.21.1 NeoForge OneOne 6.9.3",
        "basis":"actual extracted modpack JAR blockstate resource names",
        "artifacts":artifacts,"blockstates":sorted(blocks.values(),key=lambda x:x["id"]),
        "modelled_count":sum(v["model"]!="unsupported" for v in blocks.values()),
        "unmodelled_count":sum(v["model"]=="unsupported" for v in blocks.values()),
        "model_without_blockstate":sorted(models-set(blocks)),
        "warning":"Blockstate resource proves an ID exists, not that a block behavior is faithfully reproduced."
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("jars",nargs="+",type=Path)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    output=audit_jar_files(a.jars)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(output,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"Audited {len(output['artifacts'])} JARs: "
          f"{output['modelled_count']} modelled, {output['unmodelled_count']} unsupported IDs")

if __name__=="__main__":main()
