from __future__ import annotations
import re
from .model import Verses
from .normalize import normalize_hebrew, normalize_english
from .sources import matches_source

def _source_ok(v,sources):
    if not sources: return True
    if isinstance(sources,str): sources=[sources]
    return any(any(matches_source(sp.source,w) for w in sources) for sp in v.hebrew_spans+v.english_spans)

def grep(verses, query, *, language='english', regex=False, case=False, niqqud=None, spaces=None, matres=None, sources=None):
    """Search verses. Hebrew defaults to ignoring spaces and niqqud."""
    if language not in {'english','hebrew','eng','heb'}: raise ValueError(language)
    heb=language.startswith('h')
    if spaces is None: spaces=not heb
    out=Verses()
    if heb:
        for v in verses:
            if not _source_ok(v,sources): continue
            hay=normalize_hebrew(v.hebrew,niqqud=niqqud,spaces=spaces,matres=matres)
            needle=normalize_hebrew(str(query),niqqud=niqqud,spaces=spaces,matres=matres)
            if (re.search(needle,hay) if regex else needle in hay): out.append(v)
    else:
        flags=0 if case else re.IGNORECASE
        for v in verses:
            if not _source_ok(v,sources): continue
            hay=v.english
            ok=re.search(str(query),hay,flags) is not None if regex else normalize_english(str(query),case=case) in normalize_english(hay,case=case)
            if ok: out.append(v)
    return out
