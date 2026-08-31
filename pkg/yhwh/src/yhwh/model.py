"""Corpus object model: spans, verses, chapters, books, and verse collections."""
from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence, overload

from .ansi import BLUE, LIGHT_GREY, RED, paint
from .sources import DEFAULT_SOURCE_MAP, SourceMap, source_sort_key


@dataclass(frozen=True, order=True)
class Span:
    """A half-open source assignment in extracted plain text."""

    start: int
    end: int
    source: str
    macro: str | None = None

    def __post_init__(self) -> None:
        if self.start < 0 or self.end < self.start:
            raise ValueError(f"Invalid span [{self.start}, {self.end})")
        if not self.source:
            raise ValueError("A source span requires a non-empty literal source label")

    @property
    def length(self) -> int:
        return self.end - self.start

    def overlaps(self, start: int, end: int) -> int:
        return max(0, min(self.end, end) - max(self.start, start))

    def to_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "start": self.start,
            "end": self.end,
            "source": self.source,
        }
        if self.macro is not None:
            value["macro"] = self.macro
        return value

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "Span":
        return cls(
            int(value["start"]),
            int(value["end"]),
            str(value["source"]),
            str(value["macro"]) if value.get("macro") is not None else None,
        )


@dataclass(frozen=True)
class VerseRef:
    book: str
    chapter: int
    verse: str
    ordinal: int = 0

    @property
    def canonical_id(self) -> str:
        return f"{self.book}.{self.chapter}.{self.verse}"

    @property
    def id(self) -> str:
        return self.canonical_id if self.ordinal == 0 else f"{self.canonical_id}#{self.ordinal + 1}"

    def __str__(self) -> str:
        return f"{self.book} {self.chapter}:{self.verse}"


@dataclass(frozen=True)
class Verse:
    """A paired Hebrew/English verse with lossless literal source spans."""

    book: str
    chapter: int
    number: str
    hebrew: str = ""
    english: str = ""
    hebrew_spans: tuple[Span, ...] = ()
    english_spans: tuple[Span, ...] = ()
    path: str | None = None
    raw_tex: str | None = None
    ordinal: int = 0
    metadata: Mapping[str, Any] = field(default_factory=dict, compare=False, hash=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "number", str(self.number))
        self._validate_spans(self.hebrew, self.hebrew_spans, "Hebrew")
        self._validate_spans(self.english, self.english_spans, "English")

    @staticmethod
    def _validate_spans(text: str, spans: Sequence[Span], label: str) -> None:
        last = 0
        for span in spans:
            if span.end > len(text):
                raise ValueError(f"{label} source span exceeds text: {span.end} > {len(text)}")
            if span.start < last:
                raise ValueError(f"{label} source spans overlap or are unsorted")
            last = span.end

    @property
    def verse(self) -> str:
        return self.number

    @property
    def ref(self) -> VerseRef:
        return VerseRef(self.book, self.chapter, self.number, self.ordinal)

    @property
    def canonical_id(self) -> str:
        return self.ref.canonical_id

    @property
    def id(self) -> str:
        return self.ref.id

    def text(self, language: str = "english") -> str:
        return self.hebrew if language.lower().startswith(("h", "heb")) else self.english

    def spans(self, language: str = "english") -> tuple[Span, ...]:
        return self.hebrew_spans if language.lower().startswith(("h", "heb")) else self.english_spans

    def source_weights(
        self,
        language: str = "english",
        start: int | None = None,
        end: int | None = None,
        *,
        canonical: bool = False,
        source_map: SourceMap = DEFAULT_SOURCE_MAP,
        normalize: bool = True,
    ) -> Counter[str]:
        text = self.text(language)
        lo = 0 if start is None else start
        hi = len(text) if end is None else end
        if lo < 0 or hi < lo or hi > len(text):
            raise IndexError((lo, hi, len(text)))
        weights: Counter[str] = Counter()
        for span in self.spans(language):
            overlap = span.overlaps(lo, hi)
            if overlap:
                label = source_map.canonical(span.source) if canonical else span.source
                if label is not None:
                    weights[label] += overlap
        if normalize and weights:
            total = sum(weights.values())
            return Counter({key: value / total for key, value in weights.items()})
        return weights

    def sources(
        self,
        language: str | None = None,
        *,
        canonical: bool = False,
        source_map: SourceMap = DEFAULT_SOURCE_MAP,
    ) -> tuple[str, ...]:
        spans = (
            self.hebrew_spans + self.english_spans
            if language is None
            else self.spans(language)
        )
        labels = {
            source_map.canonical(span.source) if canonical else span.source for span in spans
        }
        return tuple(sorted((x for x in labels if x), key=source_sort_key))

    def segments(
        self, language: str = "english", *, canonical: bool = False
    ) -> tuple[tuple[str, str], ...]:
        text = self.text(language)
        result: list[tuple[str, str]] = []
        for span in self.spans(language):
            source = DEFAULT_SOURCE_MAP.canonical(span.source) if canonical else span.source
            if source is not None:
                result.append((source, text[span.start : span.end]))
        return tuple(result)

    def grep_english(self, query: Any, **kwargs: Any) -> list[Any]:
        from .normalize import find_english

        return find_english(self.english, query, **kwargs)

    def grep_hebrew(self, query: Any, **kwargs: Any) -> list[Any]:
        from .normalize import find_hebrew

        return find_hebrew(self.hebrew, query, **kwargs)

    def to_dict(self, *, include_raw: bool = True) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "canonical_id": self.canonical_id,
            "book": self.book,
            "chapter": self.chapter,
            "verse": self.number,
            "ordinal": self.ordinal,
            "hebrew": self.hebrew,
            "english": self.english,
            "hebrew_spans": [span.to_dict() for span in self.hebrew_spans],
            "english_spans": [span.to_dict() for span in self.english_spans],
            "path": self.path,
            "metadata": dict(self.metadata),
        }
        if include_raw:
            result["raw_tex"] = self.raw_tex
        return result

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "Verse":
        return cls(
            book=str(value["book"]),
            chapter=int(value["chapter"]),
            number=str(value.get("verse", value.get("number"))),
            hebrew=str(value.get("hebrew", "")),
            english=str(value.get("english", "")),
            hebrew_spans=tuple(Span.from_dict(v) for v in value.get("hebrew_spans", ())),
            english_spans=tuple(Span.from_dict(v) for v in value.get("english_spans", ())),
            path=str(value["path"]) if value.get("path") is not None else None,
            raw_tex=str(value["raw_tex"]) if value.get("raw_tex") is not None else None,
            ordinal=int(value.get("ordinal", 0)),
            metadata=dict(value.get("metadata", {})),
        )

    def __repr__(self) -> str:
        source = "+".join(self.sources(canonical=True)) or "?"
        sample = (self.english or self.hebrew).replace("\n", " ")
        sample = re.sub(r"\s+", " ", sample).strip()
        if len(sample) > 72:
            sample = sample[:69] + "…"
        return paint(f'<Verse {self.ref} [{source}] “{sample}”>', BLUE)


class Verses(list[Verse]):
    """A list with corpus-aware search/frequency conveniences and match metadata."""

    def __init__(
        self,
        values: Iterable[Verse] = (),
        *,
        matches: Mapping[str, Sequence[Any]] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(values)
        self.matches: dict[str, tuple[Any, ...]] = {
            key: tuple(value) for key, value in (matches or {}).items()
        }
        self.metadata: dict[str, Any] = dict(metadata or {})

    def match_info(self, verse: Verse | str) -> tuple[Any, ...]:
        key = verse.id if isinstance(verse, Verse) else verse
        return self.matches.get(key, ())

    def grep(self, query: Any, *, language: str = "english", **kwargs: Any) -> "Verses":
        return self.hebrew(query, **kwargs) if language.lower().startswith("h") else self.english(query, **kwargs)

    def english(self, query: Any, **kwargs: Any) -> "Verses":
        from .search import grep_english

        return grep_english(self, query, **kwargs)

    def hebrew(self, query: Any, **kwargs: Any) -> "Verses":
        from .search import grep_hebrew

        return grep_hebrew(self, query, **kwargs)

    grep_english = english
    grep_hebrew = hebrew

    def frequency(self, language: str = "english", **kwargs: Any) -> Any:
        from .frequency import frequency

        return frequency(self, language=language, **kwargs)

    def frequencies_by_source(self, language: str = "english", **kwargs: Any) -> Any:
        from .frequency import frequencies_by_source

        return frequencies_by_source(self, language=language, **kwargs)

    def source_profile(self, query: str, language: str = "english", **kwargs: Any) -> Any:
        from .statistics import source_profile

        return source_profile(self, query, language=language, **kwargs)

    @property
    def books(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(verse.book for verse in self))

    def to_jsonl(self, path: str | Path, *, include_raw: bool = True) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        opener: Any
        if target.suffix == ".gz":
            import gzip

            opener = gzip.open
        else:
            opener = open
        with opener(target, "wt", encoding="utf-8") as handle:
            for verse in self:
                handle.write(json.dumps(verse.to_dict(include_raw=include_raw), ensure_ascii=False))
                handle.write("\n")
        return target

    def __repr__(self) -> str:
        if not self:
            return "Verses([])"
        if len(self) <= 3:
            return "Verses([" + ", ".join(repr(v) for v in self) + "])"
        return f"Verses({len(self)} verses, {self[0].ref}–{self[-1].ref})"


@dataclass(frozen=True)
class Chapter(Sequence[Verse]):
    book: str
    number: int
    verses: Verses

    @overload
    def __getitem__(self, index: int) -> Verse: ...

    @overload
    def __getitem__(self, index: slice) -> Verses: ...

    def __getitem__(self, index: int | slice) -> Verse | Verses:
        if isinstance(index, slice):
            return Verses(self.verses[index])
        return self.verses[index]

    def __len__(self) -> int:
        return len(self.verses)

    def verse(self, number: int | str) -> Verse:
        needle = str(number)
        for verse in self.verses:
            if verse.number == needle:
                return verse
        raise KeyError(f"{self.book} {self.number}:{needle}")

    def grep_english(self, query: Any, **kwargs: Any) -> Verses:
        return self.verses.english(query, **kwargs)

    def grep_hebrew(self, query: Any, **kwargs: Any) -> Verses:
        return self.verses.hebrew(query, **kwargs)

    def frequency(self, language: str = "english", **kwargs: Any) -> Any:
        return self.verses.frequency(language, **kwargs)

    def frequencies_by_source(self, language: str = "english", **kwargs: Any) -> Any:
        return self.verses.frequencies_by_source(language, **kwargs)

    def __repr__(self) -> str:
        return paint(f"<Chapter {self.book} {self.number}: {len(self)} verses>", RED)


@dataclass(frozen=True)
class Book(Sequence[Chapter]):
    name: str
    chapters: tuple[Chapter, ...]

    @overload
    def __getitem__(self, index: int) -> Chapter: ...

    @overload
    def __getitem__(self, index: slice) -> tuple[Chapter, ...]: ...

    def __getitem__(self, index: int | slice) -> Chapter | tuple[Chapter, ...]:
        return self.chapters[index]

    def __len__(self) -> int:
        return len(self.chapters)

    @property
    def verses(self) -> Verses:
        return Verses(v for chapter in self.chapters for v in chapter)

    def chapter(self, number: int) -> Chapter:
        for chapter in self.chapters:
            if chapter.number == int(number):
                return chapter
        raise KeyError(f"{self.name} {number}")

    def grep_english(self, query: Any, **kwargs: Any) -> Verses:
        return self.verses.english(query, **kwargs)

    def grep_hebrew(self, query: Any, **kwargs: Any) -> Verses:
        return self.verses.hebrew(query, **kwargs)

    def frequency(self, language: str = "english", **kwargs: Any) -> Any:
        return self.verses.frequency(language, **kwargs)

    def frequencies_by_source(self, language: str = "english", **kwargs: Any) -> Any:
        return self.verses.frequencies_by_source(language, **kwargs)

    def __repr__(self) -> str:
        return paint(
            f"<Book {self.name}: {len(self.chapters)} chapters, {len(self.verses)} verses>",
            LIGHT_GREY,
        )
