from pathlib import Path
import os, shutil

def cache_dir(): return Path(os.environ.get('YHWH_CACHE_DIR',Path.home()/'.cache'/'yhwh'))
def clean_cache():
    p=cache_dir()
    if p.exists(): shutil.rmtree(p)
