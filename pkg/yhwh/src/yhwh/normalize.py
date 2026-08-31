"""Pure text normalization/tokenization helpers; no corpus or TeX dependency."""
from __future__ import annotations
import re, unicodedata
from typing import Iterable

_NIQQUD = re.compile(r"[\u0591-\u05C7]")
_MAQAF = "\u05be"
_niqqud_default = False

def set_niqqud(value: bool) -> None:
    """Set whether Hebrew matching preserves niqqud/cantillation by default."""
    global _niqqud_default
    _niqqud_default = bool(value)

def get_niqqud() -> bool:
    return _niqqud_default

def strip_niqqud(text: str) -> str:
    return _NIQQUD.sub("", unicodedata.normalize("NFD", text))

def normalize_hebrew(text: str, *, niqqud: bool | None = None, spaces: bool = False,
                     matres: str | bool | None = None) -> str:
    """Normalize Hebrew for matching.

    By default niqqud/cantillation and whitespace are ignored. ``matres='internal'``
    removes internal ו/י in each whitespace-delimited token; ``matres='all'`` removes
    ו/י everywhere.  This deliberately does not remove א/ה, which are too often
    consonantal to be a useful blind normalization.
    """
    if niqqud is None:
        niqqud = get_niqqud()
    out = unicodedata.normalize("NFC", text)
    if not niqqud:
        out = strip_niqqud(out)
    if matres is True:
        matres = "all"
    if matres:
        if matres not in {"internal", "all"}:
            raise ValueError("matres must be False/None, 'internal', or 'all'")
        if matres == "all":
            out = out.replace("ו", "").replace("י", "")
        else:
            def f(tok: str) -> str:
                if len(tok) <= 2: return tok
                return tok[0] + tok[1:-1].replace("ו", "").replace("י", "") + tok[-1]
            out = " ".join(f(t) for t in out.split(" "))
    if not spaces:
        out = re.sub(r"\s+", "", out)
    else:
        out = re.sub(r"\s+", " ", out).strip()
    return out

def normalize_english(text: str, *, case: bool = False) -> str:
    out = unicodedata.normalize("NFC", text)
    return out if case else out.casefold()

def words(text: str, *, lower: bool = True) -> list[str]:
    """Split only on whitespace. Apostrophes, hyphens and punctuation stay attached."""
    toks = text.split()
    return [t.casefold() for t in toks] if lower else toks

def hebrew_words(text: str, *, niqqud: bool | None = None,
                 matres: str | bool | None = None) -> list[str]:
    if niqqud is None: niqqud = get_niqqud()
    raw = unicodedata.normalize("NFC", text).split()
    return [normalize_hebrew(t, niqqud=niqqud, spaces=True, matres=matres) for t in raw if t]
