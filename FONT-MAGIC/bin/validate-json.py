#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fontmagic.common import atomic_json,strip_json_fences,validate_minimal
p=argparse.ArgumentParser(); p.add_argument("schema",type=Path); p.add_argument("input",type=Path); p.add_argument("output",type=Path); a=p.parse_args()
try: obj=json.loads(strip_json_fences(a.input.read_text()))
except Exception as e: raise SystemExit(f"Malformed SW2 JSON: {e}")
schema=json.loads(a.schema.read_text())
try:
 import jsonschema; jsonschema.validate(obj,schema)
except ImportError:
 errors=validate_minimal(obj,schema)
 if errors: raise SystemExit("Schema errors: "+"; ".join(errors))
except Exception as e: raise SystemExit(f"Schema validation failed: {e}")
atomic_json(a.output,obj)
