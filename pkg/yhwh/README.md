# yhwh

`yhwh` turns the source-colored Hebrew/English LaTeX corpus into a lossless,
machine-readable dataset and a Python library for concordance search, complete
long-tail frequency analysis, visualization, and quantified source attribution.

The TeX source assignments are treated as ground truth **at parse time**. Literal
labels such as `J`, `E`, `P`, `RJE`, `Dtr1`, `Dtr2`, `Dtn`, `Other`, and the
various proto-poetic labels remain in every record. Canonical groupings (`RJE →
R`, the Deuteronomistic labels → `D`, and so on) are a configurable analysis
view, never a destructive rewrite.

## What is included

- A balanced-brace TeX parser for paired `\hSOURCE{}` / `\eSOURCE{}` macros.
- Character-offset source spans, including nested source changes inside a verse
  or even inside a whitespace token.
- `Corpus`, `Book`, `Chapter`, `Verse`, and `Verses` objects with useful colored
  reprs: Book light grey, Chapter red, Verse blue.
- English literal/phrase/regex search, case-insensitive by default.
- Hebrew literal/regex search that ignores niqqud and spaces by default, while
  projecting each match back onto original text offsets.
- Module-level and context-local niqqud settings.
- Whitespace-only `Word` tokenization: apostrophes, hyphens, maqaf, punctuation,
  and unusual Unicode characters do **not** terminate a word.
- Complete source counters with majority, all, composite, or character-
  fractional treatment of mixed-source words.
- Per-word counts, rates, surprisal, PMI, shrinkage-adjusted log-odds z-scores,
  enrichment, and information contribution.
- A Torah-trained hybrid lexical/character n-gram attribution model reporting
  model posteriors, log evidence, log2 Bayes factors, coverage, and token-by-token
  contributions. All vocabulary—including the long tail—is used.
- Portable gzip JSONL, SQLite, precomputed frequency JSON, serialized models,
  schema, manifest, checksums, and validation output.
- Optional matplotlib plots, an argparse CLI, tests, a Makefile, and cache tools.

## Install

```bash
python -m pip install -e .
# plotting support
python -m pip install -e '.[plots]'
```

Point the library at the extracted TeX tree:

```bash
export YHWH_CORPUS=/path/to/primary-history
```

Or point it at a built dataset:

```bash
export YHWH_DATASET=/path/to/dataset/primary-history.jsonl.gz
```

Parsed corpora are cached under `${XDG_CACHE_HOME:-~/.cache}/yhwh`. Disable the
CLI cache with `--no-cache`, call `yhwh.clean_cache()`, or run
`yhwh cache clean`.

## Python quick start

```python
from yhwh import Corpus

corpus = Corpus.from_tex("/path/to/primary-history")

# English: a one-token literal is a whitespace-delimited word by default.
fire = corpus.grep_english("fire")

# Hebrew: niqqud and spaces are ignored by default. This can find באש even when
# the corpus has ב + אש as separately spaced material.
be_esh = corpus.grep_hebrew("באש")
for verse in be_esh:
    print(verse, be_esh.match_info(verse))

# Literal phrase and regex searches.
corpus.grep_english("and he said")
corpus.grep_english(r"\btabernacl\w*", regex=True)
corpus.grep_hebrew(r"בער.*אש", regex=True)

# Make Hebrew spaces or niqqud significant for one operation.
corpus.grep_hebrew("בְּאֵשׁ", niqqud=True, spaces=True)
```

### Global niqqud behavior

```python
from yhwh import get_niqqud, niqqud, set_niqqud

set_niqqud(True)
assert get_niqqud()

with niqqud(False):
    # Temporarily ignore niqqud in this context.
    ...
```

### Objects and source spans

```python
verse = corpus.verse("Genesis", 1, 1)
print(verse.hebrew)
print(verse.english)
print(verse.hebrew_spans)          # literal source labels and offsets
print(verse.sources(canonical=True))
print(verse.segments("english"))

book = corpus.book("Genesis")
chapter = book.chapter(22)
all_genesis = book.verses
```

`Corpus.records` retains every parsed record, including duplicate editions.
Normal iteration uses one best analytical record per canonical reference.
`corpus.variants("Genesis.22.1")` returns every retained version.

## Search semantics

The pure string functions are separate from corpus parsing and work on arbitrary
text:

```python
from yhwh import find_english, find_hebrew, frequency_text

find_english("Fire and firewood", "fire")
find_hebrew("בְּ אֵשׁ", "באש")
frequency_text("father-in-law God's", language="english")
```

English text is Unicode-normalized and casefolded by default. Extracted corpus
whitespace is collapsed to ordinary spaces; a literal English phrase therefore
cares about its spaces. Hebrew search removes niqqud and all whitespace by
default. Regexes run against that normalized stream, and match offsets are mapped
back to the original verse.

Matres can be retained (default), ignored only inside whitespace tokens, or
ignored everywhere:

```python
corpus.grep_hebrew("שלם", matres="internal")
corpus.grep_hebrew("שלם", matres="all")
```

## Complete frequency analysis

```python
from yhwh import frequencies_by_source

# Any subset can be analyzed. The default top-level `frequency()` loader uses
# all available Primary History books; source-attribution training does not.
torah = corpus.torah()

english = torah.frequency("english")
hebrew_by_source = torah.frequencies_by_source(
    "hebrew",
    canonical_sources=True,
    attribution="fractional",
)

print(hebrew_by_source["J"].most_common(25))
print(hebrew_by_source["P"].total_tokens)

profile = torah.source_profile("אלהים", language="hebrew")
for row in profile.evidence:
    print(row.source, row.count, row.log_odds_z, row.enrichment_log2)
```

The default tokenizer splits only on Unicode whitespace. It does not silently
strip commas, apostrophes, dashes, maqaf, brackets, or editorial marks. This is
intentional and follows the corpus rule; callers can perform alternative
standalone tokenization before constructing a `Frequency` when desired.

Mixed-source tokens can be handled four ways:

- `fractional`: divide one count according to source-character overlap.
- `majority`: assign the token to its largest span.
- `all`: give one count to every overlapping source.
- `composite`: assign it to a label such as `J+R`.

`characteristic_words()` ranks every eligible type, not a hand-picked vocabulary,
using shrinkage-adjusted log odds or another requested metric.

## Source attribution

```python
from yhwh import SourceAttributor

# The trusted default: train only on Genesis–Deuteronomy assignments.
model = SourceAttributor.train(corpus, scope="torah", language="hebrew")
result = model.attribute("וַיֹּאמֶר יְהוָה אֶל מֹשֶׁה")

print(result.posterior)
print(result.log2_bayes_factor)
print(result.coverage)
for token in result.strongest_tokens(limit=10):
    print(token.original, token.contribution_vs_mean_bits[result.winner])
```

The model is a smoothed multinomial Naive Bayes classifier over the **entire**
Torah vocabulary. Known words use source-conditional lexical frequencies.
Unknown words back off to averaged, smoothed 2–5-character n-grams, so a novel
sentence remains scoreable without pretending an unseen token has no evidence.
The default source classes are `J`, `E`, `P`, `R`, and combined `D`; they can be
changed.

A posterior of 0.9 means “0.9 inside this specified lexical model and its
assumptions,” not “a 90% historical probability that this author wrote the
passage.” Token independence, translation choices, topic, genre, editorial
mixture, corpus size, and uncertain training labels can all make raw Naive Bayes
posteriors overconfident. The result therefore also exposes raw evidence in bits,
coverage, token contributions, model fingerprint, and training scope.

To test a hypothesis such as Priestly material in Joshua, train on Torah and
score Joshua passages without adding Joshua labels to the training data:

```python
model = SourceAttributor.train(corpus, scope="torah", language="hebrew")
joshua_13_on = corpus.select(books="Joshua", chapters=range(13, 25))
for verse in joshua_13_on:
    result = model.attribute(verse)
    print(verse.ref, result.winner, result.evidence_for("P"))
```

## Dataset format

```bash
yhwh --corpus /path/to/primary-history build dataset/
```

This writes:

```text
dataset/
├── primary-history.jsonl.gz
├── primary-history.sqlite3
├── manifest.json
├── schema.json
├── source-labels.json
├── validation.json
├── frequencies/
│   ├── torah-hebrew-literal.json.gz
│   ├── torah-hebrew-canonical.json.gz
│   └── ...
└── models/
    ├── torah-hebrew-hybrid.json.gz
    └── torah-english-hybrid.json.gz
```

Every JSONL record contains paired text, reference data, raw TeX, file provenance,
and half-open source spans. SQLite stores the same records and spans in normalized
tables, plus normalized search columns and FTS5 when the local SQLite build
supports it. `manifest.json` gives checksums and exact counts.

## CLI examples

```bash
# Inspect corpus
 yhwh --corpus primary-history info

# Hebrew cross-boundary search
 yhwh --corpus primary-history search באש -l hebrew --segments

# English regex
 yhwh --corpus primary-history search 'tabernacl\w*' --regex -l english

# Full Torah source counters
 yhwh --corpus primary-history freq --scope torah -l hebrew --by-source --top 100

# Evidence profile
 yhwh --corpus primary-history profile אלהים -l hebrew --scope torah

# Long-tail P vocabulary
 yhwh --corpus primary-history characteristic -l hebrew --source P --limit 200

# Novel text attribution, trained on Torah only
 yhwh --corpus primary-history attribute 'וַיֹּאמֶר יְהוָה' -l hebrew --json
```

## Development

```bash
make test
make dataset CORPUS=/path/to/primary-history
make dist
```

See `docs/dataset-schema.md` for the record contract and
`docs/methodology.md` for normalization, mixed spans, and attribution details.
