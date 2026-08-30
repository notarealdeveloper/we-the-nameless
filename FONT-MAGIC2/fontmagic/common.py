from __future__ import annotations

import hashlib, json, os, re, tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ["aleph","bet","gimel","dalet","he","waw","zayin","het","tet","yod","kaf","lamed","mem","nun","samekh","ayin","pe","tsade","qof","resh","shin","taw"]

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024), b""): h.update(block)
    return h.hexdigest()

def atomic_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=path.name+".", dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f: json.dump(data,f,indent=2,sort_keys=True); f.write("\n")
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def load_json(path: Path, default: Any=None) -> Any:
    return json.loads(path.read_text()) if path.exists() else default

def slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+","-",s.strip()).strip("-") or "font"

def ensure_run(run: Path) -> None:
    for d in ["source","preprocess","segmentation","crops","masks","masks/final","traces/raw","traces/clean","traces/repaired","normalized","proofs","manifests","logs"]: (run/d).mkdir(parents=True,exist_ok=True)

def stage_key(stage: str, inputs: list[Path], config: dict) -> str:
    h=hashlib.sha256(stage.encode())
    for p in inputs:
        h.update(str(p).encode()); h.update(sha256(p).encode() if p.exists() and p.is_file() else b"missing")
    h.update(json.dumps(config,sort_keys=True).encode()); return h.hexdigest()

def cached(run: Path, stage: str, key: str, force=False) -> bool:
    p=run/"manifests"/"cache.json"; d=load_json(p,{})
    if not force and d.get(stage)==key: return True
    d[stage]=key; atomic_json(p,d); return False

def config(run: Path) -> dict: return load_json(run/"manifests"/"config.json",{})

def mapping(encoding: str) -> dict[str,int]:
    data=load_json(ROOT/"data"/"unicode-mappings.json")
    return {k:int(v,16) if isinstance(v,str) else v for k,v in data[encoding].items()}

def strip_json_fences(text: str) -> str:
    text=text.strip()
    m=re.fullmatch(r"```(?:json)?\s*(.*?)\s*```",text,re.S|re.I)
    return m.group(1).strip() if m else text

def validate_minimal(instance: Any, schema: dict, path="$") -> list[str]:
    """Small dependency-free JSON Schema subset; doctor recommends jsonschema for full validation."""
    errors=[]; typ=schema.get("type")
    ok={"object":isinstance(instance,dict),"array":isinstance(instance,list),"string":isinstance(instance,str),"number":isinstance(instance,(int,float)) and not isinstance(instance,bool),"integer":isinstance(instance,int) and not isinstance(instance,bool),"boolean":isinstance(instance,bool),"null":instance is None}
    if typ and typ in ok and not ok[typ]: return [f"{path}: expected {typ}"]
    if isinstance(instance,dict):
        for k in schema.get("required",[]):
            if k not in instance: errors.append(f"{path}: missing {k}")
        props=schema.get("properties",{})
        for k,v in instance.items():
            if k in props: errors += validate_minimal(v,props[k],path+"."+k)
    if isinstance(instance,list) and "items" in schema:
        for i,v in enumerate(instance): errors += validate_minimal(v,schema["items"],f"{path}[{i}]")
    if "enum" in schema and instance not in schema["enum"]: errors.append(f"{path}: not in enum")
    return errors
