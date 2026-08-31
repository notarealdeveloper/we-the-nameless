"""Search Verse collections while preserving match and source-span information."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Pattern

from .model import Verse, Verses
from .normalize import MatresMode, TextMatch, find_english, find_hebrew
from .sources import DEFAULT_SOURCE_MAP, SourceMap


@dataclass(frozen=True)
class VerseMatch:
    verse: Verse
    language: str
    match: TextMatch
    sources: tuple[tuple[str, float], ...]

    @property
    def text(self) -> str:
        return self.match.text

    @property
    def start(self) -> int:
        return self.match.start

    @property
    def end(self) -> int:
        return self.match.end

    def to_dict(self) -> dict[str, Any]:
        return {
            "verse": self.verse.id,
            "language": self.language,
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "normalized_text": self.match.normalized_text,
            "sources": dict(self.sources),
        }


def _source_allowed(
    weights: dict[str, float] | Any,
    source: str | Iterable[str] | None,
    *,
    source_map: SourceMap,
) -> bool:
    if source is None:
        return True
    wanted = {source} if isinstance(source, str) else set(source)
    canonical_wanted = {source_map.canonical(x) for x in wanted}
    raw = set(weights)
    canonical = {source_map.canonical(x) for x in raw}
    return bool((raw & wanted) or (canonical & canonical_wanted))


def _grep(
    verses: Iterable[Verse],
    query: str | Pattern[str],
    *,
    language: str,
    source: str | Iterable[str] | None,
    canonical_sources: bool,
    source_map: SourceMap,
    finder_kwargs: dict[str, Any],
) -> Verses:
    selected: list[Verse] = []
    all_matches: dict[str, list[VerseMatch]] = {}
    for verse in verses:
        text = verse.text(language)
        found = (
            find_hebrew(text, query, **finder_kwargs)
            if language == "hebrew"
            else find_english(text, query, **finder_kwargs)
        )
        accepted: list[VerseMatch] = []
        for match in found:
            weights = verse.source_weights(
                language,
                match.start,
                match.end,
                canonical=canonical_sources,
                source_map=source_map,
            )
            if _source_allowed(weights, source, source_map=source_map):
                accepted.append(
                    VerseMatch(
                        verse,
                        language,
                        match,
                        tuple(sorted(weights.items(), key=lambda x: (-x[1], x[0]))),
                    )
                )
        if accepted:
            selected.append(verse)
            all_matches[verse.id] = accepted
    return Verses(
        selected,
        matches=all_matches,
        metadata={"language": language, "query": getattr(query, "pattern", str(query))},
    )


def grep_english(
    verses: Iterable[Verse],
    query: str | Pattern[str],
    *,
    regex: bool = False,
    case_sensitive: bool = False,
    whole_word: bool | str = "auto",
    source: str | Iterable[str] | None = None,
    canonical_sources: bool = True,
    source_map: SourceMap = DEFAULT_SOURCE_MAP,
) -> Verses:
    """Return verses matching an English word, literal phrase, or regex.

    A one-token literal is a whitespace-delimited word by default. Phrases keep
    their spaces. Pass ``whole_word=False`` for arbitrary substring matching.
    """
    return _grep(
        verses,
        query,
        language="english",
        source=source,
        canonical_sources=canonical_sources,
        source_map=source_map,
        finder_kwargs={
            "regex": regex,
            "case_sensitive": case_sensitive,
            "whole_word": whole_word,
        },
    )


def grep_hebrew(
    verses: Iterable[Verse],
    query: str | Pattern[str],
    *,
    regex: bool = False,
    niqqud: bool | None = None,
    spaces: bool = False,
    matres: MatresMode | str | bool | None = MatresMode.KEEP,
    source: str | Iterable[str] | None = None,
    canonical_sources: bool = True,
    source_map: SourceMap = DEFAULT_SOURCE_MAP,
) -> Verses:
    """Return verses matching Hebrew, ignoring spaces and niqqud by default."""
    return _grep(
        verses,
        query,
        language="hebrew",
        source=source,
        canonical_sources=canonical_sources,
        source_map=source_map,
        finder_kwargs={"regex": regex, "niqqud": niqqud, "spaces": spaces, "matres": matres},
    )


def grep(
    verses: Iterable[Verse], query: str | Pattern[str], *, language: str = "english", **kwargs: Any
) -> Verses:
    if language.lower().startswith(("h", "heb")):
        return grep_hebrew(verses, query, **kwargs)
    return grep_english(verses, query, **kwargs)
