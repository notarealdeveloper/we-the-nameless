"""Corpus discovery, caching, indexing, selection, and dataset loading."""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence, overload

from .config import cache_dir as default_cache_dir
from .config import find_corpus
from .model import Book, Chapter, Verse, Verses
from .sources import DEFAULT_SOURCE_MAP, SourceMap
from .tex import ParsedFile, discover_source_suffixes, parse_tex_file

TORAH = ("Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy")
PRIMARY_HISTORY = TORAH + ("Joshua", "Judges", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings")
BOOK_ORDER = {book: index for index, book in enumerate(PRIMARY_HISTORY)}


def _natural(value: str) -> tuple[Any, ...]:
    return tuple(int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", value))


def verse_number_key(value: str) -> tuple[int, str]:
    match = re.match(r"\s*(\d+)(.*)", value)
    return (int(match.group(1)), match.group(2)) if match else (10**9, value)


def verse_sort_key(verse: Verse) -> tuple[Any, ...]:
    return (
        BOOK_ORDER.get(verse.book, 1000),
        verse.book,
        verse.chapter,
        verse_number_key(verse.number),
        verse.ordinal,
        _natural(verse.path or ""),
    )


def discover_tex_files(root: str | os.PathLike[str]) -> list[Path]:
    path = Path(root)
    candidates = [path] if path.is_file() else list(path.rglob("*.tex"))
    result: list[Path] = []
    for candidate in candidates:
        try:
            # Skip preambles/master files cheaply; source chapters contain Verse.
            sample = candidate.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "\\Verse" in sample:
            result.append(candidate)
    return sorted(result, key=lambda p: _natural(str(p)))


def corpus_fingerprint(files: Iterable[Path], *, content: bool = False) -> str:
    digest = hashlib.sha256()
    for path in sorted(files, key=lambda p: str(p)):
        stat = path.stat()
        digest.update(str(path.resolve()).encode())
        digest.update(str(stat.st_size).encode())
        digest.update(str(stat.st_mtime_ns).encode())
        if content:
            with path.open("rb") as handle:
                for block in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    code: str
    message: str
    verse_id: str | None = None


class Corpus(Sequence[Verse]):
    """Indexed corpus.

    ``records`` retains every parsed record, including duplicate verse editions.
    Iteration and ``verses`` use one best analytical record per canonical verse.
    ``variants(id)`` recovers all retained records.
    """

    def __init__(
        self,
        records: Iterable[Verse],
        *,
        root: str | None = None,
        source_suffixes: Iterable[str] = (),
        fingerprint: str | None = None,
        warnings: Iterable[Mapping[str, Any] | Any] = (),
    ) -> None:
        raw = sorted(records, key=verse_sort_key)
        by_id: dict[str, list[Verse]] = defaultdict(list)
        normalized_records: list[Verse] = []
        for verse in raw:
            key = verse.canonical_id
            ordinal = len(by_id[key])
            normalized = replace(verse, ordinal=ordinal)
            by_id[key].append(normalized)
            normalized_records.append(normalized)
        analytical: list[Verse] = []
        for variants in by_id.values():
            # Prefer records containing both languages and maximal source coverage.
            analytical.append(max(variants, key=self._record_score))
        self.records = Verses(sorted(normalized_records, key=verse_sort_key))
        self.verses = Verses(sorted(analytical, key=verse_sort_key))
        self.root = root
        self.source_suffixes = tuple(sorted(set(source_suffixes)))
        self.fingerprint = fingerprint
        self.warnings = tuple(warnings)
        self._variants = {key: Verses(value) for key, value in by_id.items()}
        self._canonical = {verse.canonical_id: verse for verse in self.verses}
        self._record_ids = {verse.id: verse for verse in self.records}
        self._books = self._build_books()

    @staticmethod
    def _record_score(verse: Verse) -> tuple[int, int, int, int]:
        both = int(bool(verse.hebrew) and bool(verse.english))
        coverage = sum(span.length for span in verse.hebrew_spans + verse.english_spans)
        return both, coverage, len(verse.hebrew) + len(verse.english), -verse.ordinal

    @classmethod
    def from_tex(
        cls,
        path: str | os.PathLike[str] | None = None,
        *,
        strict: bool = False,
        use_cache: bool = True,
        cache_path: str | os.PathLike[str] | None = None,
        content_fingerprint: bool = False,
    ) -> "Corpus":
        root = find_corpus(path)
        files = discover_tex_files(root)
        if not files:
            raise FileNotFoundError(f"No verse-bearing .tex files under {root}")
        fingerprint = corpus_fingerprint(files, content=content_fingerprint)
        cache_root = default_cache_dir(cache_path) / "corpora" / fingerprint
        cached = cache_root / "corpus.jsonl.gz"
        manifest = cache_root / "manifest.json"
        if use_cache and cached.exists() and manifest.exists():
            corpus = cls.from_jsonl(cached)
            info = json.loads(manifest.read_text(encoding="utf-8"))
            corpus.root = str(root)
            corpus.fingerprint = fingerprint
            corpus.source_suffixes = tuple(info.get("source_suffixes", ()))
            corpus.warnings = tuple(info.get("warnings", ()))
            return corpus

        texts = [file.read_text(encoding="utf-8", errors="replace") for file in files]
        suffixes = discover_source_suffixes(texts)
        parsed: list[ParsedFile] = [
            parse_tex_file(file, source_suffixes=suffixes, strict=strict) for file in files
        ]
        warnings: list[dict[str, Any]] = []
        for item in parsed:
            warnings.extend(
                {"path": warning.path, "offset": warning.offset, "message": warning.message}
                for warning in item.warnings
            )
        corpus = cls(
            (verse for item in parsed for verse in item.verses),
            root=str(root),
            source_suffixes=suffixes,
            fingerprint=fingerprint,
            warnings=warnings,
        )
        if use_cache:
            cache_root.mkdir(parents=True, exist_ok=True)
            corpus.records.to_jsonl(cached)
            manifest.write_text(
                json.dumps(
                    {
                        "root": str(root),
                        "fingerprint": fingerprint,
                        "files": [str(path) for path in files],
                        "source_suffixes": sorted(suffixes),
                        "warnings": warnings,
                        "record_count": len(corpus.records),
                        "verse_count": len(corpus.verses),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
        return corpus

    @classmethod
    def from_jsonl(cls, path: str | os.PathLike[str]) -> "Corpus":
        target = Path(path)
        opener: Any = gzip.open if target.suffix == ".gz" else open
        records: list[Verse] = []
        with opener(target, "rt", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    records.append(Verse.from_dict(json.loads(line)))
        return cls(records, root=str(target))

    @classmethod
    def from_dataset(cls, path: str | os.PathLike[str]) -> "Corpus":
        target = Path(path)
        if target.is_dir():
            candidates = list(target.glob("*.jsonl.gz")) + list(target.glob("*.jsonl"))
            if not candidates:
                raise FileNotFoundError(f"No JSONL dataset found in {target}")
            target = sorted(candidates)[0]
        if target.suffix in {".gz", ".jsonl"} or target.name.endswith(".jsonl.gz"):
            return cls.from_jsonl(target)
        if target.suffix in {".sqlite", ".sqlite3", ".db"}:
            from .dataset import load_sqlite

            return load_sqlite(target)
        raise ValueError(f"Unsupported dataset format: {target}")

    def _build_books(self) -> dict[str, Book]:
        books: dict[str, Book] = {}
        grouped: dict[str, dict[int, list[Verse]]] = defaultdict(lambda: defaultdict(list))
        for verse in self.verses:
            grouped[verse.book][verse.chapter].append(verse)
        for name, chapters in grouped.items():
            chapter_objects = tuple(
                Chapter(name, number, Verses(sorted(values, key=verse_sort_key)))
                for number, values in sorted(chapters.items())
            )
            books[name] = Book(name, chapter_objects)
        return books

    @overload
    def __getitem__(self, key: int) -> Verse: ...

    @overload
    def __getitem__(self, key: slice) -> Verses: ...

    @overload
    def __getitem__(self, key: str) -> Book | Verse: ...

    @overload
    def __getitem__(self, key: tuple[str, int, int | str]) -> Verse: ...

    def __getitem__(self, key: int | slice | str | tuple[str, int, int | str]) -> Any:
        if isinstance(key, int):
            return self.verses[key]
        if isinstance(key, slice):
            return Verses(self.verses[key])
        if isinstance(key, tuple):
            return self.verse(key[0], key[1], key[2])
        if key in self._books:
            return self._books[key]
        if key in self._record_ids:
            return self._record_ids[key]
        if key in self._canonical:
            return self._canonical[key]
        match = re.match(r"(.+?)\s+(\d+):(\S+)$", key)
        if match:
            return self.verse(match.group(1), int(match.group(2)), match.group(3))
        raise KeyError(key)

    def __len__(self) -> int:
        return len(self.verses)

    def __iter__(self) -> Iterator[Verse]:
        return iter(self.verses)

    @property
    def books(self) -> tuple[Book, ...]:
        return tuple(sorted(self._books.values(), key=lambda b: (BOOK_ORDER.get(b.name, 999), b.name)))

    @property
    def book_names(self) -> tuple[str, ...]:
        return tuple(book.name for book in self.books)

    def book(self, name: str) -> Book:
        try:
            return self._books[name]
        except KeyError:
            folded = name.casefold()
            for key, value in self._books.items():
                if key.casefold() == folded:
                    return value
            raise

    def chapter(self, book: str, number: int) -> Chapter:
        return self.book(book).chapter(number)

    def verse(self, book: str, chapter: int, number: int | str) -> Verse:
        key = f"{self.book(book).name}.{int(chapter)}.{number}"
        try:
            return self._canonical[key]
        except KeyError:
            raise KeyError(f"{book} {chapter}:{number}") from None

    def variants(self, reference: str | Verse) -> Verses:
        key = reference.canonical_id if isinstance(reference, Verse) else reference
        if key not in self._variants:
            # Accept human-readable references too.
            value = self[key]
            if isinstance(value, Verse):
                key = value.canonical_id
        return self._variants[key]

    def select(
        self,
        *,
        books: str | Iterable[str] | None = None,
        chapters: Iterable[int] | Mapping[str, Iterable[int]] | None = None,
        sources: str | Iterable[str] | None = None,
        language: str | None = None,
        canonical_sources: bool = True,
        source_map: SourceMap = DEFAULT_SOURCE_MAP,
        records: bool = False,
    ) -> Verses:
        values = self.records if records else self.verses
        wanted_books = None if books is None else ({books} if isinstance(books, str) else set(books))
        wanted_sources = (
            None if sources is None else ({sources} if isinstance(sources, str) else set(sources))
        )
        chapter_map: Mapping[str, Iterable[int]] | None = chapters if isinstance(chapters, Mapping) else None
        chapter_set = set(chapters) if chapters is not None and chapter_map is None else None
        selected: list[Verse] = []
        for verse in values:
            if wanted_books is not None and verse.book not in wanted_books:
                continue
            if chapter_set is not None and verse.chapter not in chapter_set:
                continue
            if chapter_map is not None and verse.chapter not in set(chapter_map.get(verse.book, ())):
                continue
            if wanted_sources is not None:
                labels = set(
                    verse.sources(language, canonical=canonical_sources, source_map=source_map)
                )
                if not labels & wanted_sources:
                    continue
            selected.append(verse)
        return Verses(selected)

    def torah(self) -> Verses:
        return self.select(books=TORAH)

    def primary_history(self) -> Verses:
        available = set(self.book_names)
        return self.select(books=[book for book in PRIMARY_HISTORY if book in available])

    def grep(self, query: Any, *, language: str = "english", **kwargs: Any) -> Verses:
        return self.grep_hebrew(query, **kwargs) if language.lower().startswith("h") else self.grep_english(query, **kwargs)

    def grep_english(self, query: Any, **kwargs: Any) -> Verses:
        from .search import grep_english

        return grep_english(self.verses, query, **kwargs)

    def grep_hebrew(self, query: Any, **kwargs: Any) -> Verses:
        from .search import grep_hebrew

        return grep_hebrew(self.verses, query, **kwargs)

    def frequency(self, language: str = "english", **kwargs: Any) -> Any:
        return self.verses.frequency(language, **kwargs)

    def validate(self) -> tuple[ValidationIssue, ...]:
        issues: list[ValidationIssue] = []
        for verse in self.records:
            if not verse.hebrew and not verse.english:
                issues.append(ValidationIssue("error", "empty", "No extracted text", verse.id))
            elif not verse.hebrew:
                issues.append(ValidationIssue("warning", "missing-hebrew", "No Hebrew", verse.id))
            elif not verse.english:
                issues.append(ValidationIssue("warning", "missing-english", "No English", verse.id))
            for language in ("hebrew", "english"):
                text = verse.text(language)
                spans = verse.spans(language)
                covered = sum(span.length for span in spans)
                if text and covered != len(text):
                    issues.append(
                        ValidationIssue(
                            "error",
                            "span-coverage",
                            f"{language} spans cover {covered}/{len(text)} characters",
                            verse.id,
                        )
                    )
        for canonical_id, variants in self._variants.items():
            if len(variants) > 1:
                issues.append(
                    ValidationIssue(
                        "info", "duplicate", f"{len(variants)} retained records", canonical_id
                    )
                )
        return tuple(issues)

    def summary(self) -> dict[str, Any]:
        raw_sources: Counter[str] = Counter()
        canonical_sources: Counter[str] = Counter()
        for verse in self.verses:
            for span in verse.hebrew_spans:
                raw_sources[span.source] += span.length
                label = DEFAULT_SOURCE_MAP.canonical(span.source)
                if label:
                    canonical_sources[label] += span.length
        return {
            "root": self.root,
            "fingerprint": self.fingerprint,
            "books": self.book_names,
            "analytical_verses": len(self.verses),
            "records": len(self.records),
            "duplicates": len(self.records) - len(self.verses),
            "source_suffixes": self.source_suffixes,
            "source_characters_hebrew": dict(raw_sources),
            "canonical_source_characters_hebrew": dict(canonical_sources),
            "warnings": len(self.warnings),
        }

    def __repr__(self) -> str:
        return (
            f"<Corpus {len(self.verses)} verses, {len(self.records)} records, "
            f"{len(self._books)} books>"
        )
