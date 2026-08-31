# yhwh

`yhwh` is a source-aware lexical workbench for the Hebrew Bible files in this project. It parses the project's TeX source assignments into a machine-readable verse dataset, searches English or Hebrew without flattening mixed-source verses, computes source-conditioned frequency tables, plots them, and scores novel text against source language learned from the Torah.

The important rule is simple: **the TeX assignments are ground truth for the corpus layer.** Statistical attribution is a separate layer. By default authorship evidence is trained only on Genesis–Deuteronomy, while Joshua–Kings can be treated as material to test rather than labels to trust.

## Install

```bash
pip install -e '.[dev]'
export YHWH_DATA_DIR=/path/to/primary-history
```

If the generated dataset shipped in `data/primary-history.jsonl.gz` is present, `yhwh.load()` can use it directly. Otherwise it looks for `$YHWH_DATA_DIR`, `./primary-history`, or a compatible chapter tree in the current directory.

## Python API

```python
import yhwh

bible = yhwh.load()

bible.book("Genesis")
bible.book("Genesis")[30]
bible.book("Genesis")[30][1]

# English: case-insensitive by default, spaces remain significant.
verses = bible.english("give me children")
verses = bible.english(r"give .* children", regex=True)

# Hebrew: niqqud and whitespace are ignored by default.
# This can match across a supplied word boundary.
verses = bible.hebrew("באש")
verses = bible.hebrew("ב אש")
verses = bible.hebrew("ב אש", spaces=True)
verses = bible.hebrew(r"באש.*בער", regex=True)

# Per-call or global niqqud behavior.
yhwh.set_niqqud(True)
yhwh.get_niqqud()
yhwh.set_niqqud(False)

# Optional mater normalization. We conservatively treat ו/י as matres.
bible.hebrew("...", matres="internal")
bible.hebrew("...", matres="all")

# Frequency analysis. Word boundaries are whitespace only.
f = bible.frequency("english")                  # Primary History by default
jep = bible.frequency("english", books=yhwh.TORAH_BOOKS,
                       by_source=True, sources=["J", "E", "P"])
hebrew = bible.frequency("hebrew", books=["Genesis", "Exodus"])

# A source-conditioned count for one word.
yhwh.word_by_source(bible.subset(yhwh.TORAH_BOOKS), "dream", language="english")

# Long-tail lexical source evidence, trained on the Torah by default.
result = bible.evidence("וַיֹּאמֶר יְהוָה אֶל מֹשֶׁה")
result.best
result.posteriors
result.table()
```

`Book`, `Chapter`, and `Verse` reprs are ANSI light-grey, red, and blue respectively. A `Verse` stores both whole-language strings and exact `SourceSpan`s with source, raw source label, text, and character offsets. `Verses` is a `list` subclass; `Frequency` is a `collections.Counter` subclass; `Word` is a `str` subclass.

## Source labels

Raw TeX labels are never discarded. Current corpus labels include J, E, P, R, RJE, JE, JP, PR, Other, several Proto families, BookOfRecords, and Deuteronomistic labels such as Dtn, DtrA, DtrB, and DtrH. Analysis exposes a canonical `D` family that groups the Deuteronomistic labels while retaining their raw labels in every span. This makes it possible to ask a broad authorship question without making the dataset itself less precise.

## Tokenization and Hebrew normalization

Search and frequency tokenization are intentionally separate. English frequency tokens end **only at whitespace**: apostrophes, hyphens, Unicode dashes, and other punctuation do not create a boundary. Hebrew frequency analysis also uses supplied whitespace, as a concordance normally would.

Hebrew grep is deliberately more permissive. By default it strips Unicode Hebrew marks and all whitespace from both query and verse, so a string can be found even when the manuscript/transcription puts a word boundary inside it. `spaces=True` restores space sensitivity. `niqqud=True` preserves marks. `matres="internal"` removes internal ו/י; `matres="all"` removes ו/י everywhere. א/ה are not blindly removed because they are too often consonantal.

## Evidence model

`yhwh.evidence` implements a smoothed multinomial Naive Bayes model over the **entire observed token vocabulary**, not a hand-curated list of diagnostic terms. Each Torah source span contributes its full token counts. A novel text is scored under each requested source language model with additive smoothing and an empirical source-size prior; log-scores are normalized with softmax into posterior probabilities. The result includes training-token totals and per-token log-likelihood contributions so conclusions can be audited.

The default classes are J, E, P, R, and canonical D. A requested class with no training text is omitted rather than assigned fabricated evidence. Small classes (especially R) naturally have greater uncertainty; posterior numbers are evidence under this lexical model, not a claim that authorship can be reduced to vocabulary alone.

For exploratory work on Joshua, for example, concatenate the Hebrew of a `Verses` selection and score it against a Torah-trained model:

```python
model = yhwh.train(bible, language="hebrew")
joshua_late = yhwh.Verses(v for v in bible.book("Joshua").verses if v.chapter >= 13)
text = " ".join(v.hebrew for v in joshua_late)
model.score(text)
```

## Plotting

Plotting is optional (`pip install -e '.[plot]'`). Functions return Matplotlib axes and do not call `show()`:

```python
from yhwh import plot
ax = plot.frequency(jep["P"], n=40)
ax.figure.savefig("p-frequency.png", bbox_inches="tight")

ax = plot.sources(jep, "offering")
ax = plot.evidence(result)
```

## CLI

```bash
yhwh --data /path/to/primary-history grep dream -l english
yhwh --data /path/to/primary-history grep 'באש' -l hebrew
yhwh --data /path/to/primary-history grep 'באש' -l hebrew --spaces
yhwh --data /path/to/primary-history freq -l english --source J --source E --source P -n 50 --json
yhwh --data /path/to/primary-history word dream -l english
yhwh --data /path/to/primary-history evidence 'וַיֹּאמֶר יְהוָה אֶל מֹשֶׁה' --json
yhwh --data /path/to/primary-history dataset data/primary-history.jsonl.gz
yhwh cache-clean
```

## Dataset schema

`data/primary-history.jsonl.gz` is UTF-8 gzip JSON Lines, one object per verse. Each object has `book`, `chapter`, `verse`, `hebrew`, `english`, `hebrew_spans`, and `english_spans`. A span has `source`, `raw_source`, `text`, `start`, and `end`. The dataset is generated from the TeX files in this run; it is not derived from the earlier frequency experiments.

## Development

```bash
make test
make check DATA=/path/to/primary-history
make dataset DATA=/path/to/primary-history
```

The TeX parser lives in `yhwh.tex`; normalization/tokenization lives in `yhwh.normalize`; search, frequency, evidence, plotting, and models are separate modules. This is intentional so the text-analysis pieces can be used on strings or manually constructed `Verse`/`Verses` objects without adopting the project's TeX format.
