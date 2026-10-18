# EPUB renderer

This directory contains the book-specific EPUB 3 renderer for *We The Nameless*.
It reads the same `master.tex` include sequence and chapter files as the print
renderer; it is not a second manuscript. `build.py` parses the project's
semantic TeX commands, produces a temporary structured Markdown/HTML
intermediate document, asks Pandoc 3 to package semantic XHTML, CSS, fonts,
images, navigation, and metadata, and then validates the resulting archive.

## Building

Start with [PUBLISH.md](PUBLISH.md) for the complete command sequence.
From the repository root:

```sh
make genesis-ebook-release     # Build + internal validation + required EPUBCheck.
make J-ebook-release           # Any print subset, including case-sensitive J/j and P/p.
make genesis-1-ebook-release   # Chapter selection.
make genesis-ebook-check       # Check the existing file; no rebuild.
make ebook-release            # Active complete master selection.
make genesis-ebook             # Development build; EPUBCheck optional.
make check-ebook               # Renderer regression tests; no PDF/EPUB build.
```

`bin/book-subset` supplies the registry and source/chapter filtering for all
subset editions. Numbered book aliases share the existing `ebook/genesis.epub`,
`ebook/exodus.epub`, etc. Source/chapter editions use their canonical names,
e.g. `ebook/J.epub` and `ebook/genesis-1.epub`. The active complete edition is
`ebook/we-the-nameless.epub`. Apocrypha follows `ConfigApocrypha` in `master.tex`, just like print. Override
it with `APOCRYPHA=canonical` on either Makefile or `--apocrypha canonical`
on `build.py`. Full Genesis and Exodus editions retain their apocrypha,
including introductions, fragment headings, notes, and trailing dialogue;
source/chapter subsets follow the print selector’s exclusions. Print-only
frontispieces remain excluded; alternate verses within chapters remain included.
The Genesis apocrypha's print title/index pages become a linked contents list;
its introduction and apocryphon headings retain destinations without exposing
TeX layout settings or page references. Conditional KDP comic paths resolve to
the original colour images for the ebook.
Original `\Sentence` prose is rendered alongside numbered `\Verse` material.

Direct interfaces remain: `make -C ebook genesis`, `make -C ebook J`, and
`make -C ebook validate-genesis`. Checks now require EPUBCheck and never build.
`--book Genesis` remains available on `build.py` for the legacy active-master
selection; prefer `--subset genesis` to select independently of commented master
includes, like print. Use `EBOOK_COVER=<basename>` at the root or `COVER=<basename>`
in `ebook/` to select from `img/covers`; `none` omits it.

Builds stage their EPUB and replace the destination only after validation passes.
Release targets fail immediately if EPUBCheck is unavailable. Development targets
run it when installed and propagate its failures. Do not build the same edition
concurrently; different editions have separate output paths.

Each independently publishable edition has a deterministic `urn:uuid` package
identifier. The complete edition and each single-book edition use different
identifiers, but rebuilding the same edition preserves its identity. This is
required when a store such as Google Play Books receives a new content file as
an update to an existing listing. Do not replace these identifiers for routine
releases; changing one creates a new publication in distributors' catalogs.
Single-book packages also carry their book name in `dc:title`, so stores and
Kindle libraries do not display every volume under an indistinguishable title.
A build requires Pandoc 3. `--keep-markdown` on `build.py` preserves
`manuscript.generated.md` for debugging; otherwise it is temporary.

The publication notices (including the Genesis 1 warning), author legend, and
source-font explanations are read from their current definitions in `master.tex`.
The reusable manuscript substitutions are read there too, including `Er` and
the Reuben face. Midrash boundaries and RA/RB/RC redactor distinctions survive
conversion. Canadian syllabics, Anatolian hieroglyphs, and the inline
Proto-Sinaitic helper have embedded specialist fonts. The primeval font legend
includes historical alphabet specimens using the glyph-slot maps in
`master.tex`. The Isaiah-scroll alphabet below each apocryphon title uses the
same face and lowercase sequence as print.

## Source-to-EPUB mapping

- `\Book`, `\BookPart`, `\Chapter`, and the include order establish the book
  hierarchy. `\ChapterSummaryLink` supplies the same editorial labels shown in
  the print contents page.
- Every `\Verse` becomes a `.verse` component with a stable
  `<book>-<chapter>-<verse>` ID, Hebrew, English, and commentary regions.
  Intentional duplicate recensions receive explicit `-alternate-N` IDs.
- J/E/P, redactors, records, Deuteronomists, composite sources, and primeval
  sources become labeled source spans with centralized classes. Priest/bold and
  redactor-highlight distinctions remain independent of hue.
- Commentary voices retain distinct classes inside a commentary region. Print
  indentation becomes spacing and voice color rather than fake margins; no
  border is added because `\Verse` adds none around commentary.
- Footnote macros become EPUB noteref links and `epub:type="footnote"` asides
  with backlinks. Print-only material nested inside a note is reflowed in note
  order: wrapped figures become bounded block images and nested quotations
  become indented, left-aligned quotation regions instead of leaking TeX
  placement arguments into the text.
- `\Table` becomes a genuine table with header/body cells, wrapping, and a
  horizontally scrollable last-resort container. Tables are not rasterized.
- Quotes and lists use native structures; source images become responsive
  figures. TeX math Pandoc understands becomes MathML. Unusual stacked
  editorial readings become accessible stacked text rather than a bitmap.
- Print-only `tabular`/`minipage` scaffolding around multiple semantic tables
  is removed while the inner tables remain in reading order. Positive 2/4/6-em
  indentation in rhetorical diagrams is retained as bounded relative spacing;
  it never changes the paragraph's left alignment.
- The recurring Jacob-family TikZ scene in Genesis 48 becomes a compact,
  reflowable Egyptian-glyph figure. Its people, crossed-hands state, caption,
  and reading order survive without exposing TikZ commands or freezing a PDF
  page into an image.
- Language helpers carry explicit `lang` and `dir` attributes. Base bidi
  direction is never established with CSS.

## LaTeX → EPUB component mapping

`master.tex` is the authority for these components. The renderer keeps their
editorial relationships while replacing paper geometry with reflow-safe HTML.

- `\Verse{number}{Hebrew}{English}{commentary}` maps to `.verse`, containing a
  ruled, centered `.verse-reference`, followed by `.verse-translation`,
  `.verse-source`, and (when nonempty) `.verse-commentary`. This is the exact
  document order of `\VerseVertical`: ragged-left English first, a medium gap,
  then right-aligned RTL Hebrew. The commentary follows after another medium
  gap. EPUB always uses this vertical mode; it does not reproduce
  `\VerseColumns` or its paper-only center rule.
- `\Table[setup]{columns}{rows}` maps to `.wtn-table` with semantic `thead`,
  `tbody`, `th`, and `td` elements. It preserves the print component's blue
  definition color, compact default scale and cell padding, centered table box,
  column alignment, and only the rules explicitly requested by the TeX column
  preamble or `\hline`. On narrow screens cells wrap; horizontal overflow is a
  fallback. A custom setup is represented by `.wtn-table-custom`, which inherits
  the surrounding type size because arbitrary TeX setup cannot be portable CSS.
- `\Def{term}[qualifier]{body}` maps to `.definition`, with a
  `.definition-heading`, semantic `dfn`, optional parenthesized
  `.definition-qualifier`, terminal period, and `.definition-body`. Like
  `\DefBlock`, the whole unit is blue, normal roman text, indented by two em;
  the term alone is bold and the body starts on the following line. There is no
  decorative border or background because the LaTeX component has neither.
  `\DefA`, `\DefB`, and `\DefC` retain black, red, and blue voice colors.
- `\aA`, `\aB`, and `\aC` map to `.annotation-a`, `.annotation-b`, and
  `.annotation-c`: normal-size roman commentary in black, red, and blue.
  The generated `l/c/r` shortcut forms retain their intentional alignment;
  ordinary commentary is not centered or artificially indented.
- `\fA`, `\fB`, and `\fC` become EPUB noterefs and footnote asides whose note
  content retains the corresponding annotation voice. This mirrors the LaTeX
  definition: each is a colored commentary wrapper around `\footnote`.
- `\eJ`/`\hJ` and the other `e*`/`h*` source-profile pairs map to shared
  `.source-*` identities applied independently to English and Hebrew spans.
  Hue, language-specific weight, source-specific face, and consonantal
  conversion follow the profile bundles in `master.tex`; backgrounds appear
  only on profiles that actually invoke `\Redactor` (merely setting a latent
  `\SourceBgColor` does not paint text). Hebrew spans also
  carry `lang="he" dir="rtl"` in markup.
- `\paleo` and historical source profiles use embedded Paleo-Hebrew faces.
  Unicode-backed text carries explicit RTL language/direction metadata; legacy
  ASCII-slotted Paleo fonts use semantic `<bdo dir="rtl">` overrides so both
  character order and wrapped-line progression remain Hebrew RTL. `\egypt`,
  Hebrew, Arabic, Syriac, Ugaritic, and cuneiform helpers carry matching
  language/direction metadata and specialist faces.

The palette uses literal RGB definitions from `master.tex` and marks
source-critical colours as important author styles. This deliberately favors
reliable source notation in the light theme used by Kindle and phone readers;
dark and sepia themes may suppress or remap the colours. Ordinary English prose
and the page background remain reader-controlled.

## Type and color

Normal prose uses the reading system's serif book face and foreground/background.
Front-matter prose and apocrypha use the same relative scale and line spacing as
the main verses; containers apply that scale once. Heading type, hiding, and
page-break rules target heading elements explicitly because Pandoc also copies
their classes onto enclosing sections. All English headings and title lettering
use serif. Source-key descriptions flow left-aligned without the print column's
forced line breaks. The apocrypha index is left-aligned, and each apocryphon
starts on a new page with its contents destination attached to the title.
Publisher fonts are embedded only where script identity
or repertoire is editorial information: the project's Hebrew and historical
Paleo-Hebrew faces plus the display face. Confirm redistribution rights before
adding any font.

The source palette uses conservative, literal CSS 2.1 colours rather than CSS
custom properties. Hue, weight, and highlight shape jointly encode source
identity, so the text remains intelligible if a reader suppresses colour.

## Validation and QA

The October ebook fixes were checked with renderer regression tests and isolated
Pandoc note fixtures, without building a PDF or EPUB. Adjacent-note regression
coverage scans verse fragments throughout the manuscript, including nested book
directories. Markdown superscript shorthand is disabled in the packaging reader
because it otherwise consumes adjacent inline footnotes; explicit HTML
superscripts remain supported. A fresh release
build and reading-system inspection are still needed before publication.


Every build runs `validate.py`. It verifies EPUB ZIP ordering/mimetype,
container and package XML, unique identifiers, manifest completeness,
well-formed XHTML, duplicate IDs, local links/fragments, nav presence, missing
assets, leaked filesystem paths, and visible TeX/Markdown/layout debris.
`make -C ebook test` also runs focused conversion regressions, including nested
footnotes, stacked multilingual readings, and the left-aligned commentary
default. Pandoc
structural warnings also fail the build. If `epubcheck` is on `PATH`, it runs
and errors fail the build; otherwise the build explicitly reports that it was
unavailable. Install EPUBCheck before release publication.

Genesis is the torture test: mixed sources, pointed/unpointed Hebrew,
Paleo-Hebrew and primeval scripts, nested commentary, hundreds of notes, large
critical tables, diagrams, poetry, math, and an alternate Genesis 22. Inspect
the generated nav and chapters 1, 10, 22, 31, and 49 in a standards-oriented
reader and Kindle Previewer before release. Test phone width, large type, light,
sepia, and dark themes. Kindle Previewer is not installed in this environment.

## Compatibility policy

The baseline is semantic XHTML, document-order reflow, HTML bidi attributes,
simple tables, relative sizing, legacy and modern break properties, and real
note links. Enhancements include columns on the visible contents page and
horizontal table overflow. Their absence does not remove meaning.

Title, alphabet, and publication-notice pages use percentage padding rather
than viewport-height or flexbox-based vertical positioning. This keeps their
reading order and spacing predictable through Kindle conversion while
remaining reflowable at large reader font sizes.

EPUB 3.3 permits modern CSS but prohibits CSS `direction` and `unicode-bidi`,
so direction lives in markup. See the [EPUB 3.3 CSS requirements](https://www.w3.org/TR/epub-33/#sec-css).
Kindle accepts EPUB and its Enhanced Typesetting supports embedded fonts, HTML
tables, MathML, semantic note links, and break controls. Amazon specifically
recommends leaving ordinary body typography reader-controlled and using
`aside` plus `epub:type` for notes; this renderer follows that policy. See the
[Kindle reflowable text guidelines](https://kdp.amazon.com/en_US/help/topic/GH4DRT75GWWAGBTU).
Kindle may still ignore columns, publisher fonts, or overflow. Google Play
Books likewise documents multi-column layout and MathML as unsupported, so
neither is required for the primary reading flow.
Fixed/absolute positioning, viewport-dependent normal layout, negative table
margins, nested tables, and fixed-layout pagination are avoided.

The visible contents intentionally follows the print book's editorial chapter
index; the EPUB nav exposes the same book/chapter hierarchy to readers. Page
numbers, running heads, literal margins, and two-column paper geometry are
intentionally omitted because they do not survive reflow.
