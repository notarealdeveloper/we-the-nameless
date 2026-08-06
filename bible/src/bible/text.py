from __future__ import annotations

from collections.abc import Iterable

from .refs import BookRef, ChapterRef, VerseRef


def verse_texts(_ref: BookRef | ChapterRef | VerseRef) -> Iterable[tuple[VerseRef, str]] | object:
    return NotImplemented


def require_verse_texts(ref: BookRef | ChapterRef | VerseRef) -> Iterable[tuple[VerseRef, str]]:
    texts = verse_texts(ref)
    if texts is NotImplemented:
        raise NotImplementedError(
            "TODO: provide a verse text store keyed by canonical book, chapter, "
            "and verse before implementing grep. Add English and/or Hebrew text "
            "loading here, then return (VerseRef, text) pairs for the requested scope."
        )
    return texts
