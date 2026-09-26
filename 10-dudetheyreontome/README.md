# Dudetheyreontome

The volume is **Dudetheyreontome**, also called the **Dudetheyreonamystic
History**. Its first book is also **Dudetheyreontome**. This is a compilation
of older documents with later framing, additions, and interpolations by the
historian. An addition belongs inside the book being edited; it is not a new
book simply because its voice or date differs.

The present reading order is:

- **On The Lamb**: the Foreword and map, before the history.
- **Dudetheyreontome**, the history:
  - **Dudetheyreontome**: opening words, wilderness / Cow Dish Barn image,
    YHWH's promise, the unwritten speech, then “Dudetheyreontome” and
    “He was, from that day foreword, On The Lamb.”
  - **On The Lamb 1: Esther**: an intentionally unwritten first exile account.
  - **On The Lamb 2: Esther**: arrival in Edom, pharmacy, night, tablets,
    then the inherited Esther text, within the same book.
  - **On The Lamb 3: Ezra**: inherited Ezra, ready for later additions.
  - **On The Lamb 4: Nehemiah**: the Plane of Edom and AAA material,
    then inherited Nehemiah.
  - **Sects / Acts**.
  - **Epistles**, a separate collection within the history.

Both Esther titles are intentional: the requested first account remains a
placeholder; the existing Esther text appears once, in the second book.
Ezra and Nehemiah retain their names and text. Numbers describe the current
exile sequence, not dates of composition.

## Editing the assembly

`contents.tex` is the single ordered list for both the body and the history's
contents panel (plain and fancy). Move a `\HistoryBook` declaration together
with its following layers and includes to reorder a book. Change its title
without changing the first argument, which is its stable navigation ID.

```tex
\HistoryBook{esther-two}{On The Lamb 2: Esther}
\HistoryAddition{Esther II additions}
\include{10-dudetheyreontome/exile/esther/additions/arrival}
% More additions can go here.
\HistorySource{Esther}
\include{10-dudetheyreontome/exile/esther/01}
% Switch back to HistoryAddition here to insert a later passage, then return
% to HistorySource{Esther} for the next inherited chapter.
```

`\HistoryAddition` and `\HistorySource` change the reference namespace, not
the book. The assembled title stays in chapter headings, running heads, and
the table of contents. Additions are labeled “Addition”; source chapters
retain their original numbers. The underlying `Esther`, `Ezra`, and
`Nehemiah` identities stay intact for verse references and translation lookup.
Within a chapter, `\HistoryInterpolation{...}` uses the existing redactor
voice without resetting any counters or changing the book.

New prose uses `\Sentence{original}{English}{commentary}`. Inherited text
continues to use `\Verse{number}{original}{English}{commentary}` with fixed
source numbers. Each chapter file starts with `\Chapter{number}`; give
chapters unique numbers within each reference namespace. A passage inserted
with `\input` inside a chapter, such as `dudetheyreontome/wilderness.tex`,
has no chapter command and continues sentence numbering across the seam.

`\HistoryPlaceholder{...}` marks an unwritten passage without claiming it is
an inherited verse. Replace the speech placeholder in `dudetheyreontome/01.tex`
as the speech takes shape; the attribution to the Son of J or J stays open.

`structure.tex` owns the presentation. The frontmatter images are in
`frontmatter/include`; the wilderness images belong to
`dudetheyreontome/include`. Add an image-directory declaration in `master.tex`
for any new reference namespace that uses `\image`.

Epistles continue to be discovered from numbered directories under `epistles/`.
They are older documents available for the same editorial treatment, outside
the numbered On The Lamb sequence. See `epistles/1-jephesians/README.md`.

The Python source readers expand this same assembly through
`bin/history_structure.py`. No build is needed to edit or reorder it.
