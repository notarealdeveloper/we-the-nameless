"""Whitespace-token frequency analysis with source-aware attribution."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping

from .model import Verse, Verses
from .normalize import MatresMode, normalize_english, normalize_hebrew, whitespace_tokens
from .sources import DEFAULT_SOURCE_MAP, SourceMap, source_sort_key


class Word(str):
    """A string token with lightweight analysis metadata.

    Word boundaries are exactly whitespace boundaries. Apostrophes, hyphens,
    maqaf, punctuation, and other Unicode characters remain part of the token.
    """

    language: str
    original: str

    def __new__(cls, value: str, *, language: str = "english", original: str | None = None) -> "Word":
        obj = str.__new__(cls, value)
        obj.language = language
        obj.original = value if original is None else original
        return obj


class Frequency(Counter[Word]):
    """Counter subclass carrying normalization and corpus metadata."""

    def __init__(
        self,
        values: Mapping[str, float] | Iterable[str] | None = None,
        *,
        language: str = "english",
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__()
        self.language = language
        self.metadata: dict[str, Any] = dict(metadata or {})
        if values is not None:
            if isinstance(values, Mapping):
                for key, value in values.items():
                    self[Word(str(key), language=language)] += value
            else:
                self.update(Word(str(key), language=language) for key in values)

    @property
    def total_tokens(self) -> float:
        return float(sum(self.values()))

    @property
    def vocabulary_size(self) -> int:
        return len(self)

    def rate(self, word: str, per: float = 1_000_000) -> float:
        return 0.0 if not self.total_tokens else float(self[word]) / self.total_tokens * per

    def to_dict(self) -> dict[str, Any]:
        return {
            "language": self.language,
            "total_tokens": self.total_tokens,
            "vocabulary_size": self.vocabulary_size,
            "metadata": self.metadata,
            "counts": {str(key): value for key, value in self.most_common()},
        }

    def to_json(self, path: str | Path | None = None, *, indent: int | None = 2) -> str | Path:
        value = json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
        if path is None:
            return value
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value, encoding="utf-8")
        return target

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "Frequency":
        return cls(
            value.get("counts", {}),
            language=str(value.get("language", "english")),
            metadata=value.get("metadata", {}),
        )

    def plot(self, **kwargs: Any) -> Any:
        from .plotting import plot_frequency

        return plot_frequency(self, **kwargs)

    def __repr__(self) -> str:
        top = ", ".join(f"{word!s}: {count:g}" for word, count in self.most_common(5))
        return (
            f"<Frequency {self.language}, {self.total_tokens:g} tokens, "
            f"{self.vocabulary_size} types{'; ' + top if top else ''}>"
        )


class SourceFrequencies(dict[str, Frequency]):
    def __init__(
        self,
        values: Mapping[str, Frequency] | None = None,
        *,
        language: str = "english",
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(values or {})
        self.language = language
        self.metadata: dict[str, Any] = dict(metadata or {})

    @property
    def vocabulary(self) -> set[str]:
        return {str(word) for counter in self.values() for word in counter}

    @property
    def totals(self) -> dict[str, float]:
        return {source: counter.total_tokens for source, counter in self.items()}

    def profile(self, word: str, **kwargs: Any) -> Any:
        from .statistics import profile_from_frequencies

        return profile_from_frequencies(self, word, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "language": self.language,
            "metadata": self.metadata,
            "sources": {source: counter.to_dict() for source, counter in self.items()},
        }

    def to_json(self, path: str | Path | None = None, *, indent: int | None = 2) -> str | Path:
        value = json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
        if path is None:
            return value
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value, encoding="utf-8")
        return target

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "SourceFrequencies":
        return cls(
            {source: Frequency.from_dict(counter) for source, counter in value.get("sources", {}).items()},
            language=str(value.get("language", "english")),
            metadata=value.get("metadata", {}),
        )

    def __repr__(self) -> str:
        sources = ", ".join(
            f"{source}={counter.total_tokens:g}"
            for source, counter in sorted(self.items(), key=lambda x: source_sort_key(x[0]))
        )
        return f"<SourceFrequencies {self.language}: {sources}>"


def normalize_token(
    token: str,
    *,
    language: str,
    case_sensitive: bool = False,
    niqqud: bool | None = None,
    matres: MatresMode | str | bool | None = MatresMode.KEEP,
) -> str:
    if language.lower().startswith(("h", "heb")):
        return normalize_hebrew(token, niqqud=niqqud, spaces=True, matres=matres)
    return normalize_english(token, case_sensitive=case_sensitive, collapse_spaces=False)


def words(
    text: str,
    *,
    language: str = "english",
    case_sensitive: bool = False,
    niqqud: bool | None = None,
    matres: MatresMode | str | bool | None = MatresMode.KEEP,
) -> Iterator[tuple[Word, int, int]]:
    for raw, start, end in whitespace_tokens(text):
        normalized = normalize_token(
            raw,
            language=language,
            case_sensitive=case_sensitive,
            niqqud=niqqud,
            matres=matres,
        )
        if normalized:
            yield Word(normalized, language=language, original=raw), start, end


def frequency_text(
    text: str,
    *,
    language: str = "english",
    case_sensitive: bool = False,
    niqqud: bool | None = None,
    matres: MatresMode | str | bool | None = MatresMode.KEEP,
) -> Frequency:
    counter = Frequency(language=language, metadata={"kind": "standalone-string"})
    for word, _, _ in words(
        text,
        language=language,
        case_sensitive=case_sensitive,
        niqqud=niqqud,
        matres=matres,
    ):
        counter[word] += 1
    return counter


def _values(values: Iterable[Verse] | None) -> Iterable[Verse]:
    if values is not None:
        return values
    from .corpus import Corpus

    return Corpus.from_tex().primary_history()


def frequency(
    verses: Iterable[Verse] | None = None,
    *,
    language: str = "english",
    source: str | Iterable[str] | None = None,
    canonical_sources: bool = True,
    source_map: SourceMap = DEFAULT_SOURCE_MAP,
    case_sensitive: bool = False,
    niqqud: bool | None = None,
    matres: MatresMode | str | bool | None = MatresMode.KEEP,
    attribution: str = "majority",
) -> Frequency:
    """Count whitespace-delimited words in any verse subset.

    When ``source`` is supplied, mixed-source tokens are assigned according to
    ``attribution``: ``majority`` (default), ``fractional``, ``all``, or
    ``composite``. With no source filter every token is counted exactly once.
    """
    wanted = None if source is None else ({source} if isinstance(source, str) else set(source))
    counter = Frequency(
        language=language,
        metadata={
            "source": sorted(wanted) if wanted else None,
            "canonical_sources": canonical_sources,
            "attribution": attribution,
            "word_boundary": "unicode-whitespace-only",
            "niqqud": niqqud,
            "matres": MatresMode.coerce(matres).value,
        },
    )
    for verse in _values(verses):
        text = verse.text(language)
        for word, start, end in words(
            text,
            language=language,
            case_sensitive=case_sensitive,
            niqqud=niqqud,
            matres=matres,
        ):
            if wanted is None:
                counter[word] += 1
                continue
            weights = verse.source_weights(
                language,
                start,
                end,
                canonical=canonical_sources,
                source_map=source_map,
            )
            if not weights:
                continue
            if attribution == "majority":
                label = max(weights.items(), key=lambda x: (x[1], x[0]))[0]
                if label in wanted:
                    counter[word] += 1
            elif attribution == "fractional":
                counter[word] += sum(weight for label, weight in weights.items() if label in wanted)
            elif attribution == "all":
                counter[word] += sum(1 for label in weights if label in wanted)
            elif attribution == "composite":
                label = "+".join(sorted(weights, key=source_sort_key))
                if label in wanted:
                    counter[word] += 1
            else:
                raise ValueError("attribution must be majority, fractional, all, or composite")
    return counter


def frequencies_by_source(
    verses: Iterable[Verse] | None = None,
    *,
    language: str = "english",
    sources: Iterable[str] | None = None,
    canonical_sources: bool = True,
    source_map: SourceMap = DEFAULT_SOURCE_MAP,
    case_sensitive: bool = False,
    niqqud: bool | None = None,
    matres: MatresMode | str | bool | None = MatresMode.KEEP,
    attribution: str = "fractional",
    include_unassigned: bool = False,
) -> SourceFrequencies:
    """Build full long-tail counters for every source in one pass."""
    allowed = set(sources) if sources is not None else None
    counters: dict[str, Frequency] = {}

    def get(label: str) -> Frequency:
        if label not in counters:
            counters[label] = Frequency(
                language=language,
                metadata={"source": label, "attribution": attribution},
            )
        return counters[label]

    count_verses = 0
    for verse in _values(verses):
        count_verses += 1
        text = verse.text(language)
        for word, start, end in words(
            text,
            language=language,
            case_sensitive=case_sensitive,
            niqqud=niqqud,
            matres=matres,
        ):
            weights = verse.source_weights(
                language,
                start,
                end,
                canonical=canonical_sources,
                source_map=source_map,
            )
            if not weights:
                if include_unassigned and (allowed is None or "Unassigned" in allowed):
                    get("Unassigned")[word] += 1
                continue
            if attribution == "fractional":
                for label, weight in weights.items():
                    if allowed is None or label in allowed:
                        get(label)[word] += weight
            elif attribution == "majority":
                label = max(weights.items(), key=lambda x: (x[1], x[0]))[0]
                if allowed is None or label in allowed:
                    get(label)[word] += 1
            elif attribution == "all":
                for label in weights:
                    if allowed is None or label in allowed:
                        get(label)[word] += 1
            elif attribution == "composite":
                label = "+".join(sorted(weights, key=source_sort_key))
                if allowed is None or label in allowed:
                    get(label)[word] += 1
            else:
                raise ValueError("attribution must be majority, fractional, all, or composite")
    return SourceFrequencies(
        dict(sorted(counters.items(), key=lambda x: source_sort_key(x[0]))),
        language=language,
        metadata={
            "verses": count_verses,
            "canonical_sources": canonical_sources,
            "attribution": attribution,
            "word_boundary": "unicode-whitespace-only",
            "niqqud": niqqud,
            "matres": MatresMode.coerce(matres).value,
        },
    )


full_frequency = frequency
source_frequencies = frequencies_by_source
