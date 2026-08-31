from pathlib import Path
import os
from .model import Corpus
from .tex import parse_directory

def find_data(path=None):
    if path: return Path(path)
    if os.environ.get('YHWH_DATA_DIR'): return Path(os.environ['YHWH_DATA_DIR'])
    cwd=Path.cwd()
    candidates=[cwd/'primary-history',cwd,cwd/'data'/'primary-history.jsonl.gz']
    for p in candidates:
        if p.is_file() or (p.is_dir() and any(p.glob('01-genesis/*.tex'))): return p
    bundled=Path(__file__).resolve().parents[2]/'data'/'primary-history.jsonl.gz'
    if bundled.exists(): return bundled
    raise FileNotFoundError('No yhwh corpus found; set YHWH_DATA_DIR or pass path=')

def load(path=None):
    p=find_data(path)
    return Corpus.from_jsonl(p) if p.is_file() and (p.name.endswith('.jsonl') or p.name.endswith('.jsonl.gz')) else parse_directory(p)
