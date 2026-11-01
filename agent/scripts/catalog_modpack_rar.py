#!/usr/bin/env python3
"""Extract text-only block registries from every JAR in a local modpack RAR.

Requires libarchive (provided by most Linux images). The RAR/JAR binaries are
not copied into the repository. Subordinate jarjar archives are scanned once.
"""
from __future__ import annotations
import argparse,ctypes,ctypes.util,gzip,hashlib,io,json,zipfile
from pathlib import Path
from agent.sim.mod_devices import DEVICE_FACTORIES

MAX_SINGLE_JAR=150*1024*1024
MAX_JARS=400
MAX_TOTAL_BYTES=2*1024*1024*1024


def jar_blockstates(filename: str,raw: bytes):
    if len(raw)>MAX_SINGLE_JAR:raise ValueError("JAR exceeds configured size limit")
    with zipfile.ZipFile(io.BytesIO(raw)) as jar:
        states=[];inner=[]
        for n in jar.namelist():
            if n.startswith("assets/") and n.endswith(".json"):
                p=n.split("/")
                if len(p)==4 and p[2]=="blockstates":
                    states.append(p[1]+":"+p[3][:-5])
            if n.startswith("META-INF/jarjar/") and n.endswith(".jar"):
                inner.append((filename+"!/"+n,jar.read(n)))
    return sorted(set(states)),inner


def audit_entries(entries):
    artifacts=[];states={};processed=0;total=0
    def add_jar(name,data,nested=False):
        nonlocal processed,total
        processed+=1;total+=len(data)
        if processed>MAX_JARS or total>MAX_TOTAL_BYTES:
            raise ValueError("modpack archive processing budget exceeded")
        ids,embedded=jar_blockstates(name,data)
        artifacts.append({"file":name,"sha256":hashlib.sha256(data).hexdigest(),
                          "nested":nested,"registered_blockstates":len(ids)})
        for id in ids:
            obj=states.setdefault(id,{"id":id,"sources":[],"model":"unsupported"})
            obj["sources"].append(name)
            if id in DEVICE_FACTORIES:
                obj["model"]=DEVICE_FACTORIES[id][0].__name__
        for inner_name,inner_data in embedded:add_jar(inner_name,inner_data,True)
    for name,data in entries:
        if name.lower().endswith(".jar"):
            add_jar(name,data)
    values=sorted(states.values(),key=lambda x:x["id"])
    return {"schema_version":1,"target":"Minecraft 1.21.1 NeoForge OneOne 6.9.3",
            "basis":"actual modpack RAR JAR resources, including nested Aeronautics/Simulated",
            "artifacts":artifacts,"blockstates":values,
            "modelled_count":sum(s["model"]!="unsupported" for s in values),
            "unmodelled_count":sum(s["model"]=="unsupported" for s in values),
            "model_without_blockstate":sorted(set(DEVICE_FACTORIES)-set(states)),
            "warning":"Blockstate existence does not prove mod behavior parity; unsupported must stay explicit."}


def compact_report(report):
    """Emit the reproducible compact schema used by the committed gzip registry."""
    sources={artifact["file"]:i for i,artifact in enumerate(report["artifacts"])}
    return {
        "schema_version":2,
        "target":report["target"],
        "basis":report["basis"],
        "artifacts":report["artifacts"],
        "blockstates":[[block["id"],*(sources[x] for x in block["sources"])]
                       for block in report["blockstates"]],
        "device_models":{block["id"]:block["model"] for block in report["blockstates"]
                         if block["model"]!="unsupported"},
        "modelled_count":report["modelled_count"],
        "unmodelled_count":report["unmodelled_count"],
        "model_without_blockstate":report["model_without_blockstate"],
        "warning":report["warning"],
        "format_note":"blockstates entries are [block_id, artifact_index,...]. Absence from device_models means unsupported."
    }


def rar_entries(path:Path):
    name=ctypes.util.find_library("archive")
    if not name:raise RuntimeError("libarchive system library not installed")
    lib=ctypes.CDLL(name)
    lib.archive_read_new.restype=ctypes.c_void_p
    for symbol in ("archive_read_support_filter_all","archive_read_support_format_all","archive_read_free"):
        getattr(lib,symbol).argtypes=[ctypes.c_void_p]
    lib.archive_read_open_filename.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_size_t]
    lib.archive_read_next_header.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_void_p)]
    lib.archive_entry_pathname.argtypes=[ctypes.c_void_p]
    lib.archive_entry_pathname.restype=ctypes.c_char_p
    lib.archive_entry_size.argtypes=[ctypes.c_void_p]
    lib.archive_entry_size.restype=ctypes.c_int64
    lib.archive_read_data.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t]
    lib.archive_read_data.restype=ctypes.c_ssize_t
    lib.archive_read_data_skip.argtypes=[ctypes.c_void_p]
    handle=lib.archive_read_new()
    lib.archive_read_support_filter_all(handle);lib.archive_read_support_format_all(handle)
    if lib.archive_read_open_filename(handle,str(path).encode("utf-8"),131072)!=0:
        lib.archive_read_free(handle);raise RuntimeError("libarchive cannot open this RAR")
    entry=ctypes.c_void_p()
    try:
        while lib.archive_read_next_header(handle,ctypes.byref(entry))==0:
            name=lib.archive_entry_pathname(entry).decode("utf-8","replace")
            if not name.lower().endswith(".jar"):
                lib.archive_read_data_skip(handle);continue
            size=lib.archive_entry_size(entry)
            if size>MAX_SINGLE_JAR:raise ValueError("JAR too large: "+name)
            buf=ctypes.create_string_buffer(65536)
            parts=[];read_size=0
            while True:
                n=lib.archive_read_data(handle,buf,len(buf))
                if n==0:break
                if n<0:raise RuntimeError("RAR read failure: "+name)
                read_size+=n
                if read_size>MAX_SINGLE_JAR:raise ValueError("JAR stream too large: "+name)
                parts.append(buf.raw[:n])
            yield name,b"".join(parts)
    finally:
        lib.archive_read_free(handle)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("archive",type=Path)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    report=compact_report(audit_entries(rar_entries(args.archive)))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    content=(json.dumps(report,ensure_ascii=False,separators=(",",":"))+"\n").encode("utf-8")
    if args.out.name.endswith(".gz"):
        args.out.write_bytes(gzip.compress(content,compresslevel=9,mtime=0))
    else:
        args.out.write_bytes(content)
    print(f"Scanned {len(report['artifacts'])} JAR layers: "
          f"{report['modelled_count']} modelled and {report['unmodelled_count']} unmodelled block IDs")

if __name__=="__main__":main()
