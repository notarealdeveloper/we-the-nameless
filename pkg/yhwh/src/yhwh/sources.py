"""Source labels: retain raw labels, optionally collapse them for analysis."""
from __future__ import annotations
D_FAMILY={'Dtn','DtrA','DtrB','DtrH','Dtr1','Dtr2','Dtr'}
CANONICAL_DEFAULT=('J','E','P','R','D')

def canonical_source(source: str) -> str:
    if source in D_FAMILY or source.startswith('Dtr'): return 'D'
    if source in {'RJE','JE'}: return source
    return source

def source_members(source: str) -> set[str]:
    if source == 'D': return set(D_FAMILY)
    return {source}

def matches_source(raw: str, wanted: str) -> bool:
    if wanted=='D': return canonical_source(raw)=='D'
    return raw==wanted
