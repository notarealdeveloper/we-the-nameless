# Dataset schema

The authoritative portable representation is newline-delimited UTF-8 JSON,
gzip-compressed in release artifacts. One line is one retained source record.
Duplicate canonical references are legal and receive `#2`, `#3`, … record IDs.

## Verse record

| Field | Type | Meaning |
|---|---:|---|
| `id` | string | Unique record ID, e.g. `Genesis.22.1#2`. |
| `canonical_id` | string | Reference without variant ordinal. |
| `book` | string | Canonical or discovered book name. |
| `chapter` | integer | Chapter number. |
| `verse` | string | Verse designator; string permits suffixes/ranges. |
| `ordinal` | integer | Zero-based variant ordinal. |
| `hebrew` | string | Rendered Hebrew with logical whitespace collapsed. |
| `english` | string | Rendered English with logical whitespace collapsed. |
| `hebrew_spans` | span[] | Literal source assignments into `hebrew`. |
| `english_spans` | span[] | Literal source assignments into `english`. |
| `path` | string/null | Original TeX path. |
| `raw_tex` | string/null | Complete TeX slice beginning at `\Verse`. |
| `metadata` | object | Parser/file provenance. |

## Span

A span is half-open: `[start, end)`, measured in Python Unicode code points in the
corresponding rendered string.

| Field | Type | Meaning |
|---|---:|---|
| `start` | integer | Inclusive character offset. |
| `end` | integer | Exclusive character offset. |
| `source` | string | Literal suffix from the `h/e` source macro. |
| `macro` | string/null | Full macro name, such as `hJ` or `eDtr1`. |

Spans are ordered, non-overlapping, and cover every character of non-empty
rendered text. Nested source macros replace the active label over their exact
rendered character range.

## Literal versus canonical source

JSONL spans preserve literal labels only. Canonical source grouping is an
analysis view controlled by `SourceMap`. SQLite adds a convenience
`canonical_source` column while retaining `source` beside it.

## SQLite

- `verses`: one row per retained record, with an `analytical` flag.
- `spans`: one row per source span and language.
- `metadata`: JSON-valued build metadata.
- `verse_fts`: optional FTS5 index when supported by SQLite.

`hebrew_search` strips niqqud and whitespace but retains matres. `english_search`
is casefolded with whitespace collapsed.
