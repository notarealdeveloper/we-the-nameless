# EPUB renderer

This directory contains the book-specific EPUB 3 renderer for *We The Nameless*.
It reads the same `master.tex` include sequence and chapter files as the print
renderer; it is not a second manuscript. `build.py` parses the project's
semantic TeX commands, produces a temporary structured Markdown/HTML
intermediate document, asks Pandoc 3 to package semantic XHTML, CSS, fonts,
images, navigation, and metadata, and then validates the resulting archive.

## Building

From the repository root:

```sh
make ebook
make ebook-genesis
make ebook-samuel
make ebook-validate
```

The original interfaces remain available:

```sh
make -C ebook
make -C ebook genesis
make -C ebook samuel
make -C ebook validate-genesis
```

Outputs are written to `ebook/we-the-nameless.epub` and `ebook/<book>.epub`.
A build requires Pandoc 3. `--keep-markdown` on `build.py` preserves
`manuscript.generated.md` for debugging; otherwise it is temporary.

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
- Commentary voices retain distinct classes inside a bordered commentary
  region. Print indentation becomes spacing and voice color rather than fake
  margins.
- Footnote macros become EPUB noteref links and `epub:type="footnote"` asides
  with backlinks.
- `\Table` becomes a genuine table with header/body cells, wrapping, and a
  horizontally scrollable last-resort container. Tables are not rasterized.
- Quotes and lists use native structures; source images become responsive
  figures. TeX math Pandoc understands becomes MathML. Unusual stacked
  editorial glyph constructions degrade to text rather than a bitmap.
- Language helpers carry explicit `lang` and `dir` attributes. Base bidi
  direction is never established with CSS.

## Type and color

Normal prose uses the reading system's book face, size, line spacing, and
foreground/background. Publisher fonts are embedded only where script identity
or repertoire is editorial information: the project's Hebrew and historical
Paleo-Hebrew faces plus the display face. Confirm redistribution rights before
adding any font.

The source palette is centralized with CSS custom properties and conservative
fallbacks. Hue, weight, and highlight shape jointly encode source identity, so
the text remains legible under light, sepia, dark, monochrome, and user themes.
The dark-mode query is progressive enhancement; body colors are not forced.

## Validation and QA

Every build runs `validate.py`. It verifies EPUB ZIP ordering/mimetype,
container and package XML, unique identifiers, manifest completeness,
well-formed XHTML, duplicate IDs, local links/fragments, nav presence, missing
assets, and leaked filesystem paths. Pandoc structural warnings also fail the
build. If `epubcheck` is on `PATH`, it runs and errors fail the build; otherwise
the build explicitly reports that it was unavailable. Install EPUBCheck before
release publication.

Genesis is the torture test: mixed sources, pointed/unpointed Hebrew,
Paleo-Hebrew and primeval scripts, nested commentary, hundreds of notes, large
critical tables, diagrams, poetry, math, and an alternate Genesis 22. Inspect
the generated nav and chapters 1, 10, 22, 31, and 49 in a standards-oriented
reader and Kindle Previewer before release. Test phone width, large type, light,
sepia, and dark themes. Kindle Previewer is not installed in this environment.

## Compatibility policy

The baseline is semantic XHTML, document-order reflow, HTML bidi attributes,
simple tables, relative sizing, legacy and modern break properties, and real
note links. Enhancements include CSS variables, columns on the visible contents
page, `prefers-color-scheme`, and horizontal table overflow. Their absence does
not remove meaning.

EPUB 3.3 permits modern CSS but prohibits CSS `direction` and `unicode-bidi`,
so direction lives in markup. Kindle accepts EPUB and supports embedded OTF/TTF
fonts, HTML tables, MathML, note links, and break controls, but may ignore
dark-mode queries, columns, custom properties, publisher fonts, or overflow.
Fixed/absolute positioning, viewport-dependent normal layout, negative table
margins, nested tables, and fixed-layout pagination are avoided.

The visible contents intentionally follows the print book's editorial chapter
index; the EPUB nav exposes the same book/chapter hierarchy to readers. Page
numbers, running heads, literal margins, and two-column paper geometry are
intentionally omitted because they do not survive reflow.
