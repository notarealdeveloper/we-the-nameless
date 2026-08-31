"""Machine-readable JSONL/SQLite dataset export and import."""
from __future__ import annotations

import gzip
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable

from .attribution import SourceAttributor
from .corpus import Corpus, PRIMARY_HISTORY, TORAH, verse_sort_key
from .frequency import frequencies_by_source
from .model import Span, Verse
from .normalize import normalize_english, normalize_hebrew
from .sources import DEFAULT_MODEL_SOURCES, DEFAULT_SOURCE_MAP

SCHEMA_VERSION = 1

DATASET_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "yhwh source-aware verse record",
    "type": "object",
    "required": [
        "id",
        "canonical_id",
        "book",
        "chapter",
        "verse",
        "hebrew",
        "english",
        "hebrew_spans",
        "english_spans",
    ],
    "properties": {
        "id": {"type": "string"},
        "canonical_id": {"type": "string"},
        "book": {"type": "string"},
        "chapter": {"type": "integer"},
        "verse": {"type": "string"},
        "ordinal": {"type": "integer"},
        "hebrew": {"type": "string"},
        "english": {"type": "string"},
        "path": {"type": ["string", "null"]},
        "raw_tex": {"type": ["string", "null"]},
        "hebrew_spans": {"$ref": "#/$defs/spans"},
        "english_spans": {"$ref": "#/$defs/spans"},
    },
    "$defs": {
        "span": {
            "type": "object",
            "required": ["start", "end", "source"],
            "properties": {
                "start": {"type": "integer", "minimum": 0},
                "end": {"type": "integer", "minimum": 0},
                "source": {"type": "string"},
                "macro": {"type": ["string", "null"]},
            },
        },
        "spans": {"type": "array", "items": {"$ref": "#/$defs/span"}},
    },
}


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_jsonl(
    corpus: Corpus,
    path: str | Path,
    *,
    include_raw: bool = True,
    records: bool = True,
) -> Path:
    values = corpus.records if records else corpus.verses
    return values.to_jsonl(path, include_raw=include_raw)


def write_sqlite(corpus: Corpus, path: str | Path, *, include_raw: bool = True) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.unlink()
    connection = sqlite3.connect(target)
    try:
        connection.executescript(
            """
            PRAGMA journal_mode=WAL;
            PRAGMA synchronous=NORMAL;
            CREATE TABLE metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE verses (
                id TEXT PRIMARY KEY,
                canonical_id TEXT NOT NULL,
                analytical INTEGER NOT NULL,
                book TEXT NOT NULL,
                book_order INTEGER NOT NULL,
                chapter INTEGER NOT NULL,
                verse TEXT NOT NULL,
                ordinal INTEGER NOT NULL,
                path TEXT,
                hebrew TEXT NOT NULL,
                english TEXT NOT NULL,
                hebrew_search TEXT NOT NULL,
                english_search TEXT NOT NULL,
                raw_tex TEXT,
                metadata_json TEXT NOT NULL
            );
            CREATE TABLE spans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                verse_id TEXT NOT NULL REFERENCES verses(id) ON DELETE CASCADE,
                language TEXT NOT NULL CHECK(language IN ('hebrew','english')),
                start_offset INTEGER NOT NULL,
                end_offset INTEGER NOT NULL,
                source TEXT NOT NULL,
                canonical_source TEXT,
                macro TEXT
            );
            CREATE INDEX verse_reference ON verses(book_order, book, chapter, verse, ordinal);
            CREATE INDEX verse_canonical ON verses(canonical_id);
            CREATE INDEX span_source ON spans(source, language);
            CREATE INDEX span_canonical_source ON spans(canonical_source, language);
            """
        )
        analytical_ids = {verse.id for verse in corpus.verses}
        from .corpus import BOOK_ORDER

        for verse in corpus.records:
            connection.execute(
                """
                INSERT INTO verses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    verse.id,
                    verse.canonical_id,
                    int(verse.id in analytical_ids),
                    verse.book,
                    BOOK_ORDER.get(verse.book, 1000),
                    verse.chapter,
                    verse.number,
                    verse.ordinal,
                    verse.path,
                    verse.hebrew,
                    verse.english,
                    normalize_hebrew(verse.hebrew, niqqud=False, spaces=False),
                    normalize_english(verse.english),
                    verse.raw_tex if include_raw else None,
                    json.dumps(dict(verse.metadata), ensure_ascii=False),
                ),
            )
            for language, spans in (
                ("hebrew", verse.hebrew_spans),
                ("english", verse.english_spans),
            ):
                connection.executemany(
                    """
                    INSERT INTO spans
                    (verse_id, language, start_offset, end_offset, source, canonical_source, macro)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            verse.id,
                            language,
                            span.start,
                            span.end,
                            span.source,
                            DEFAULT_SOURCE_MAP.canonical(span.source),
                            span.macro,
                        )
                        for span in spans
                    ],
                )
        metadata = {
            "schema_version": SCHEMA_VERSION,
            "corpus_fingerprint": corpus.fingerprint,
            "root": corpus.root,
            "records": len(corpus.records),
            "analytical_verses": len(corpus.verses),
            "source_suffixes": corpus.source_suffixes,
        }
        connection.executemany(
            "INSERT INTO metadata(key, value) VALUES (?, ?)",
            [(key, json.dumps(value, ensure_ascii=False)) for key, value in metadata.items()],
        )
        try:
            connection.executescript(
                """
                CREATE VIRTUAL TABLE verse_fts USING fts5(
                    id UNINDEXED,
                    english,
                    hebrew,
                    content='verses',
                    content_rowid='rowid'
                );
                INSERT INTO verse_fts(rowid, id, english, hebrew)
                    SELECT rowid, id, english, hebrew FROM verses;
                """
            )
        except sqlite3.OperationalError:
            # Some minimal SQLite builds omit FTS5; all ordinary indexes remain.
            pass
        connection.commit()
    finally:
        connection.close()
    return target


def load_sqlite(path: str | Path) -> Corpus:
    connection = sqlite3.connect(Path(path))
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            "SELECT * FROM verses ORDER BY book_order, chapter, CAST(verse AS INTEGER), ordinal"
        ).fetchall()
        grouped: dict[str, dict[str, list[Span]]] = {}
        for row in connection.execute(
            "SELECT verse_id, language, start_offset, end_offset, source, macro FROM spans ORDER BY id"
        ):
            grouped.setdefault(row["verse_id"], {"hebrew": [], "english": []})[row["language"]].append(
                Span(row["start_offset"], row["end_offset"], row["source"], row["macro"])
            )
        verses = [
            Verse(
                book=row["book"],
                chapter=row["chapter"],
                number=row["verse"],
                ordinal=row["ordinal"],
                path=row["path"],
                hebrew=row["hebrew"],
                english=row["english"],
                hebrew_spans=tuple(grouped.get(row["id"], {}).get("hebrew", ())),
                english_spans=tuple(grouped.get(row["id"], {}).get("english", ())),
                raw_tex=row["raw_tex"],
                metadata=json.loads(row["metadata_json"]),
            )
            for row in rows
        ]
        metadata = {
            row["key"]: json.loads(row["value"])
            for row in connection.execute("SELECT key, value FROM metadata")
        }
        return Corpus(
            verses,
            root=str(path),
            source_suffixes=metadata.get("source_suffixes", ()),
            fingerprint=metadata.get("corpus_fingerprint"),
        )
    finally:
        connection.close()


def _write_gzip_json(value: Any, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", compresslevel=9) as handle:
        json.dump(value, handle, ensure_ascii=False, separators=(",", ":"))
    return path


def build_dataset(
    corpus: Corpus,
    output_dir: str | Path,
    *,
    name: str = "primary-history",
    include_raw: bool = True,
    with_sqlite: bool = True,
    with_frequencies: bool = True,
    with_models: bool = True,
) -> dict[str, Path]:
    """Build the complete portable dataset and return all generated paths."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    generated: dict[str, Path] = {}
    jsonl = write_jsonl(corpus, out / f"{name}.jsonl.gz", include_raw=include_raw, records=True)
    generated["jsonl"] = jsonl
    if with_sqlite:
        generated["sqlite"] = write_sqlite(
            corpus, out / f"{name}.sqlite3", include_raw=include_raw
        )
    schema_path = out / "schema.json"
    schema_path.write_text(json.dumps(DATASET_SCHEMA, indent=2), encoding="utf-8")
    generated["schema"] = schema_path

    labels = {
        "literal_labels": list(corpus.source_suffixes),
        "default_canonical_map": {
            label: DEFAULT_SOURCE_MAP.canonical(label) for label in corpus.source_suffixes
        },
        "default_model_sources": list(DEFAULT_MODEL_SOURCES),
        "note": "Literal labels are ground truth and are never overwritten by canonical groupings.",
    }
    labels_path = out / "source-labels.json"
    labels_path.write_text(json.dumps(labels, ensure_ascii=False, indent=2), encoding="utf-8")
    generated["source_labels"] = labels_path

    if with_frequencies:
        scopes = {
            "torah": corpus.select(books=[book for book in TORAH if book in corpus.book_names]),
            "primary-history": corpus.select(
                books=[book for book in PRIMARY_HISTORY if book in corpus.book_names]
            ),
        }
        for scope, verses in scopes.items():
            for language in ("hebrew", "english"):
                raw = frequencies_by_source(
                    verses,
                    language=language,
                    canonical_sources=False,
                    attribution="fractional",
                    niqqud=False if language == "hebrew" else None,
                )
                canonical = frequencies_by_source(
                    verses,
                    language=language,
                    canonical_sources=True,
                    attribution="fractional",
                    niqqud=False if language == "hebrew" else None,
                )
                raw_path = out / "frequencies" / f"{scope}-{language}-literal.json.gz"
                canonical_path = out / "frequencies" / f"{scope}-{language}-canonical.json.gz"
                generated[f"frequency_{scope}_{language}_literal"] = _write_gzip_json(
                    raw.to_dict(), raw_path
                )
                generated[f"frequency_{scope}_{language}_canonical"] = _write_gzip_json(
                    canonical.to_dict(), canonical_path
                )
    if with_models:
        for language in ("hebrew", "english"):
            model = SourceAttributor.train(corpus, scope="torah", language=language)
            model_path = out / "models" / f"torah-{language}-hybrid.json.gz"
            generated[f"model_{language}"] = model.save(model_path)

    validation = [issue.__dict__ for issue in corpus.validate()]
    validation_path = out / "validation.json"
    validation_path.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    generated["validation"] = validation_path

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "name": name,
        "corpus_fingerprint": corpus.fingerprint,
        "records": len(corpus.records),
        "analytical_verses": len(corpus.verses),
        "duplicates_retained": len(corpus.records) - len(corpus.verses),
        "books": list(corpus.book_names),
        "source_suffixes": list(corpus.source_suffixes),
        "normalization": {
            "dataset_text": "TeX rendered and Unicode whitespace collapsed",
            "hebrew_search_default": "niqqud and spaces ignored; matres retained",
            "word_boundary": "Unicode whitespace only",
        },
        "files": {},
    }
    for key, path in generated.items():
        manifest["files"][key] = {
            "path": str(path.relative_to(out)),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
    manifest_path = out / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    generated["manifest"] = manifest_path
    return generated
