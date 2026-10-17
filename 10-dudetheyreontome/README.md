# Dudetheyreontome

The reading order and the contents page share `contents.tex`:

1. **On The Lamb**: Foreword; Dudetheyreontome and its unwritten first-exile
   placeholder; arrival in Edom; pharmacy; night; tablets (including the Syriac
   2 Esdras ending “And We did so.”); the Plane of Edom; notes on the church.
2. **Esther**, chapters 1–10, with its original verse numbering and text.
3. **Ezra**, chapters 1–10, with its original verse numbering and text.
4. **Nehemiah**, chapters 1–13, with its original verse numbering and text.
5. **Epistles**, currently 1 Jephesians.

All Son of J narrative chapters belong to On The Lamb. They must not be
interspersed with the canonical books or labeled as additions to them.
On The Lamb has eight chapters, numbered in its own reference namespace.
New prose uses `\Sentence{original}{English}{commentary}`; the canonical
chapters retain `\Verse{number}{original}{English}{commentary}` unchanged.

`structure.tex` replays the assembly using the same sub-book heading and
chapter-list commands as Samuel, for both plain and fancy contents pages.
`\HistoryBook` supplies a body heading and navigation target;
`\HistorySource` selects the chapter/verse namespace. The sub-book names
are On The Lamb, Esther, Ezra, Nehemiah, and Epistles.

The PART TWO: DIASPORA poster in `title.tex` is unchanged.

Sects / Acts (1 NHS) is retained only as a manuscript in
[eng/sects-acts/nhs/NHS.md](eng/sects-acts/nhs/NHS.md), outside the TeX assembly.

Epistles are discovered from numbered directories under `epistles/`.
See `epistles/1-jephesians/README.md`. The Python source readers expand
`contents.tex` through `bin/history_structure.py`; no build is needed to
inspect the reading order.
