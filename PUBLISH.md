# Building and publishing

`bin/build` is the general build command. The Makefile retains short targets as
abbreviations for specific calls to it, plus fully specified print targets.
Partial combinations use independent script arguments. Commands create local
files; they never upload to KDP, Lulu, or an ebook store.

## Contents

- [Make abbreviations](#make-abbreviations)
- [Selection](#selection)
- [Preset](#preset)
- [Publisher](#publisher)
- [Stage](#stage)
- [Output mode](#output-mode)
- [Theme](#theme)
- [Verse layout](#verse-layout)
- [Commentary](#commentary)
- [Translation](#translation)
- [Title page style](#title-page-style)
- [Colors](#colors)
- [Apocrypha](#apocrypha)
- [Redactor](#redactor)
- [Interior or ebook cover](#interior-or-ebook-cover)
- [Print cover artwork](#print-cover-artwork)
- [Spine lettering](#spine-lettering)
- [Print safety](#print-safety)
- [Trim](#trim)
- [Binding](#binding)
- [Processing](#processing)
- [Paper](#paper)
- [Ink](#ink)
- [Bleed](#bleed)
- [PDF encoding](#pdf-encoding)
- [Hardcover template](#hardcover-template)
- [Asset directory](#asset-directory)
- [Output directory](#output-directory)
- [Build directory](#build-directory)
- [Workflow](#workflow)
- [Reproducible timestamp](#reproducible-timestamp)
- [Artifact](#artifact)
- [Reference](#reference)
- [Make target resolution](#make-target-resolution)
- [Read-only plan](#read-only-plan)
- [Selection list](#selection-list)
- [Help and completion](#help-and-completion)
- [Dependencies and checks](#dependencies-and-checks)
- [Logs and recovery](#logs-and-recovery)
- [Compatibility commands](#compatibility-commands)

## Make abbreviations

Run Make from the repository root. `bin/build` also works from other directories;
relative path arguments are resolved against the caller's directory.

| Make job | Exactly equivalent script call with default Make variables |
| --- | --- |
| `make genesis-kdp` | `bin/build genesis kdp` |
| `make exodus-lulu` | `bin/build exodus lulu` |
| `make genesis-kdp-paperback` | `bin/build genesis kdp-paperback` |
| `make genesis-kdp-hardcover` | `bin/build genesis kdp-hardcover` |
| `make exodus-lulu-paperback` | `bin/build exodus lulu-paperback` |
| `make exodus-lulu-hardcover` | `bin/build exodus lulu-hardcover` |
| `make genesis-kdp-simplecover-vectorized-7x10` | `bin/build genesis kdp --cover-style simple --processing vectorized --trim 7x10` |
| `make J-lulu-fancycover-original-8.25x11` | `bin/build J lulu --cover-style fancy --processing original --trim 8.25x11` |
| `make genesis-kdp-build` | `bin/build genesis kdp --stage build` |
| `make exodus-lulu-hardcover-check` | `bin/build exodus lulu-hardcover --stage check` |
| `make genesis-kdp-simplecover-vectorized-7x10-check` | `bin/build genesis kdp --cover-style simple --processing vectorized --trim 7x10 --stage check` |
| `make genesis-ebook` | `bin/build genesis ebook` |
| `make genesis-ebook-release` | `bin/build genesis ebook --stage release` |
| `make genesis-ebook-check` | `bin/build genesis ebook --stage check` |
| `make ebook` / `make ebook-release` / `make ebook-check` | The corresponding ebook command with selection `all` |

A publisher-only print job produces **two** matched interior/cover pairs. A
publisher-binding job produces **one**. Their complete print defaults are:

| Preset | Artwork | Binding | Interior inches | Processing |
| --- | --- | --- | --- | --- |
| `kdp` (first pair), `kdp-paperback` | simple | paperback | 7 × 10 | vectorized |
| `kdp` (second pair), `kdp-hardcover` | fancy | hardcover | 8.25 × 11 | vectorized |
| `lulu` (first pair), `lulu-paperback` | simple | paperback | 7 × 10 | original |
| `lulu` (second pair), `lulu-hardcover` | fancy | hardcover | 7 × 10 | original |

All print presets use book mode, lite theme, horizontal verses, commentary,
inline English, fancy title pages, default colors, apocrypha, uncensored
redaction, no interior cover image, print safety, LD spine lettering,
matching premium-color paper/ink, no interior bleed, and soft PDF encoding.
KDP retains searchable originals alongside vectors. The two pairs run concurrently
with independent work directories, assets, caches, and logs.

Only these print suffixes are enumerated for each selection:

```text
PUBLISHER[-STAGE]
PUBLISHER-paperback[-STAGE]
PUBLISHER-hardcover[-STAGE]
PUBLISHER-STYLEcover-PROCESSING-TRIM[-STAGE]
```

The last form requires **every** field: publisher `kdp|lulu`, style `simple|fancy`,
processing `original|vectorized`, and numeric trim `7x10|8.25x11`.
Stage is optional: `build`, `vectorize`, or `check`; omission runs `all`.
There are 22 base print suffixes, or 88 including stages, reduced from 288.
Intermediate targets
such as `genesis-kdp-fancycover`, `genesis-lulu-original`, `genesis-kdp-7x10`,
are removed. Their operations remain available directly:

```sh
bin/build genesis kdp --cover-style fancy
bin/build genesis lulu --processing original
bin/build genesis kdp --trim 7x10
bin/build genesis kdp --stage build
bin/build genesis kdp --stage vectorize
bin/build genesis kdp --stage check
```

The ordinary reading targets (`make pdf`, `make genesis`, chapter and source
names, mode/theme shortcuts, and `make parallel`) remain available. New script
calls never open a viewer automatically. For example, `bin/build genesis` creates
`01-genesis.pdf`; `bin/build all` creates `master.pdf`.

## Selection

Positional `BOOK`, default `all`. `all` uses the active include sequence in
`master.tex`; book, chapter, and source selections use `bin/book-subset`.
Examples: `genesis`, `01-genesis`, `1-genesis`, `genesis-1`, `1-samuel`,
`1-samuel-1`, `J`, `E`, `I`, `P`, `D`, `R`, `M`, `A`, `court`, `j`, `e`, `i`,
`p`, `r`. Case matters. Numbered aliases share canonical filenames and print locks.
Run `bin/build --list` or `make list` to inspect selections.

Any selection can use either publisher. Resolving a selection does not guarantee
its page count falls within the chosen publisher/binding limits.

## Preset

Positional `PRESET`, default `pdf`. Choices: `pdf`, `ebook`, `kdp`, `lulu`,
`kdp-paperback`, `kdp-hardcover`, `lulu-paperback`, `lulu-hardcover`.

`pdf` follows the active settings at the top of `master.tex`. Print presets use
the stable defaults above. `ebook` creates reflowable EPUB with cover `we-cover-8`
and the active apocrypha setting. Explicit options override only their own field.
For example, the following are equivalent:

```sh
bin/build exodus lulu-hardcover
bin/build exodus lulu --cover-style fancy --binding hardcover --trim 7x10 --processing original
```

Overriding artwork on a binding preset keeps its binding and trim:
`bin/build genesis kdp-paperback --cover-style fancy` is an illustrated 7×10
paperback. On a publisher-only preset, `--cover-style fancy` selects its existing
fancy profile, including that profile's binding and default trim.

## Publisher

`--publisher kdp|lulu` (alias `--provider`) selects the corresponding print
preset. Thus `bin/build genesis --publisher lulu` equals `bin/build genesis lulu`.
An explicit publisher must agree with a positional publisher preset.

Publisher chooses cover geometry, eligibility checks, default processing, and
output namespace. It does not upload files. KDP and Lulu use separate geometry
implementations in `bin/kdp_cover_geometry.py` and `bin/lulu_cover_geometry.py`.
KDP paperback uses page-count/caliper spine math; Lulu paperback uses
`pages / 444 + 0.06` inches for the implemented 60# white stock. Hardcover models
include different board overhang, hinges, wrap, and spine calculations. Lulu uses
a page-count table. The KDP hardcover model is inferred from a recorded template;
use an exact template when preparing a production hardcover.

These are implemented policies, not a live catalog of publisher products. Check
the publisher's current calculator and proof before ordering:
[KDP calculator](https://kdp.amazon.com/cover-calculator),
[Lulu print resources](https://www.lulu.com/publishing-toolkit).

## Stage

`--stage all|build|vectorize|check|release`, default `all`.

| Format | Stage | Operation |
| --- | --- | --- |
| Print | `all` | Build originals, then vectorize profiles whose processing is vectorized |
| Print | `build` | Build searchable originals and matching wraps only |
| Print | `vectorize` | Convert existing originals; never rebuild |
| Print | `check` | Compare existing original/vector pairs structurally and at 300 DPI with MuPDF and Poppler |
| Reading PDF | `all`, `build` | Compile until cross-references settle (up to five passes) |
| EPUB | `all`, `build` | Development build; internal validation and optional EPUBCheck |
| EPUB | `release` | Rebuild with mandatory EPUBCheck before replacing output |
| EPUB | `check` | Validate the existing archive with both validators; never rebuild |

Explicit print stages control the operation even if processing says otherwise:
`--processing original --stage vectorize` converts; `--processing vectorized
--stage build` only builds originals. `check` requires both versions even for
Lulu. Normal conversion runs structural checks; full pixel comparison is a
separate `check` operation. A check establishes fidelity to its reference, not
freshness relative to current sources.

## Output mode

`--output-mode book|hard|tech|even` → `ConfigOutputMode`.

`book` uses 7×10 inches and binding margins; `hard` uses 8.25×11 with book
typography; `even` uses 7×10 with equal margins; `tech` uses a 7×14.68 screen
layout and larger typography. Explicit trim changes page dimensions independently
of typography, including tech mode. Print presets default to `book`; ordinary
PDF defaults follow `master.tex`.

## Theme

`--theme lite|dark` → `ConfigTheme`. Print presets use `lite`; ordinary PDF
uses the active theme. Explicit overrides also select the corresponding asset
theme. Choosing dark is an editorial choice; publisher checks do not assess
ink coverage or reading comfort.

## Verse layout

`--verse-layout horizontal|vertical` → `ConfigVerseLayout`.
Print default: `horizontal`. Controls verse arrangement independently of format,
trim, and cover.

## Commentary

`--commentary true|false` → `ConfigCommentary`. Print default: `true`.
Changes interior pagination, so rebuild its cover with the interior.

## Translation

`--translation default|NAME` → `ConfigEnglishTranslation`.
`default` uses inline English. Other names must identify a directory under
`translations/`, such as `kjv`. The build generates a private translation Lua
file and passes `ConfigEnglishTranslationLuaFile` to TeX. Print default: `default`.
Completion lists the installed translation directories.

## Title page style

`--title-page-style plain|fancy` → `IndividualBookTitlePageStyle`.
Print default: `fancy`. This controls individual interior title pages separately
from print cover artwork.

## Colors

`--colors default|lighter` → `ConfigColors`. Print default: `default`.
`lighter` selects the lighter lite-theme palette; theme remains a separate choice.

## Apocrypha

`--apocrypha apocryphal|canonical` → `ConfigApocrypha`.
Print default: `apocryphal`; ordinary PDF and EPUB follow `master.tex` unless
overridden. Make print jobs accept explicit `APOCRYPHA=canonical`.

EPUB is still a work in progress: it retains the renderer's omission of
standalone print apocrypha and frontispiece files. Alternate verses inside chapters
remain. Review [ebook/README.md](ebook/README.md) for editorial limitations.

## Redactor

`--redactor censored|uncensored` → `ConfigRedactor`.
Print default: `uncensored`. Controls the existing redaction policy in the text.

## Interior or ebook cover

`--cover none|BASENAME` → `ConfigCover` for PDFs; embedded cover image for EPUB.
Choose a basename without extension from `img/covers/`; completion lists images.
Print default: `none`. EPUB default: `we-cover-8`. Ordinary PDF follows
`master.tex`. This image is separate from the measured print wrap.

## Print cover artwork

`--cover-style simple|fancy` → `ConfigCoverStyle` and print profile artwork.
`simple` uses cover typography; `fancy` adds saved illustrated artwork with the
same typography. On a publisher-only call, selecting a style selects that
profile. Omitting it builds both profiles. Binding presets select one profile.

Either artwork can be combined with either binding, trim, or processing:

```sh
bin/build genesis lulu-paperback --cover-style fancy --trim 8.25x11 --processing vectorized
```

Fancy artwork comes from `pub/covers/fancy/assets/front-textless.png` and its
saved prompt. Building uses saved assets and deterministic TeX, without AI calls.
The saved 1024×1536 illustration has limited native print resolution; outlining
text cannot add detail to it.

## Spine lettering

`--spine ld|nameless` → `ConfigSpine` and cover lettering. Print default: `ld`.
Spines too short for lettering are left unlettered (KDP below 79 pages; Lulu at
80 pages or fewer). Geometry still follows the exact interior page count.

## Print safety

`--print-safe true|false` → the historical `ConfigKDP` TeX switch. It applies
to **both** publishers: print-safe image derivatives, heavier rules, and a blank
final page when needed to end on a complete sheet. Print presets use `true`;
ordinary PDFs follow `master.tex` (currently `false`). It can also be enabled for
a serial reading PDF. Disabling it does not disable geometry or page-count checks.

## Trim

`--trim default|7x10|8.25x11`. Values are interior dimensions in inches.
`default` preserves the selected preset's numeric trim, or the natural reading
PDF layout. Print dimensions pass to `ConfigPrintTrimWidth` and
`ConfigPrintTrimHeight`; matching wrap dimensions come from the resulting PDF.
Changing trim reflows source; it does not scale a finished PDF.

On a publisher-only call an override applies to both profiles. A binding preset
keeps its own default trim even when artwork is overridden. Custom arbitrary
trims are not implemented.

## Binding

`--binding paperback|hardcover`, print only. Overrides physical construction
independently of artwork. On a publisher-only call with both profiles, this
changes the construction of **both** pairs; select a binding preset or explicit
artwork to create one pair. Paperback is perfect bound; hardcover is casewrap.
Linen covers and dust jackets need other geometry policies.

```sh
bin/build genesis kdp-hardcover --cover-style simple
bin/build genesis lulu --cover-style fancy --binding paperback --trim 7x10
```

## Processing

`--processing original|vectorized`, print only. `original` preserves searchable
text. `vectorized` also outlines all fonts in **both** interior and cover using
Ghostscript and cleans the PDFs with qpdf, without rasterizing pages. The default
is vectorized for KDP and original for Lulu. Lulu has no implicit flattening or
`-final.pdf` step. Original illustrations remain raster images.

## Paper

`--paper premium-color|standard-color`, default `premium-color`.
KDP hardcover always uses premium color even when the selected paperback stock
is standard. Lulu implements color on 60# white uncoated stock. Black ink, cream
paper, and 80# coated stock are not implemented.

Current implemented eligibility checks require even page counts:

| Publisher / binding / stock | Pages |
| --- | --- |
| KDP paperback, premium | 24–828 |
| KDP paperback, standard | 72–600 |
| KDP hardcover | 76–550 |
| Lulu paperback | 32–800 |
| Lulu hardcover | 24–800 |

## Ink

`--ink premium-color|standard-color`, default selected paper. Must match paper;
KDP hardcover's effective paper and ink are premium color. The two arguments are
retained for compatibility; mismatches fail before building.

## Bleed

`--bleed no-bleed`. Only no-bleed interiors are implemented. This is independent
of the measured outer cover bleed/wrap required by each construction model.

## PDF encoding

`--variant soft|medium|hard`, print only, default `soft`.
All outline fonts. `soft` uses PDF 1.7 and generated object streams; `medium`
uses PDF 1.7 without object streams or content normalization; `hard` uses PDF 1.4,
no object streams, normalized content, and linearization. `hard` has no relation
to hardcover binding. Nondefault variants use `pub/PUBLISHER/VARIANT/` unless an
output directory is supplied.

## Hardcover template

`--hardcover-template PATH`, KDP hardcover only. A JSON file can replace the
inferred model with exact calculator measurements. It must match the built
interior's page count, trim, and effective paper. The pipeline records its hash.
Lulu rejects KDP templates. Example schema (illustrative measurements):

```json
{"pages":224,"trim_width":8.25,"trim_height":11,"paper":"premium-color",
 "spine":0.715,"wrap":0.591,"hinge":0.394,"panel_width":8.447,"panel_height":11.236}
```

## Asset directory

`--asset-dir PATH` overrides `KDPAssetDir`. Normally each print run prepares its
own derivative links through `bin/print-assets`, backed by a shared
content-addressed cache at `build/print/assets/`. Serial reading PDFs with print
safety enabled also prepare derivatives automatically. Supplying a directory
selects its existing derivatives for TeX.

## Output directory

`--output-dir PATH`. Default reading PDFs go to the repository root; print pairs
go to `pub/PUBLISHER/` (or its encoding subdirectory); EPUB goes to `ebook/`.
The default print naming convention is:

```text
pub/PUBLISHER/CANONICAL-{interior,cover}-STYLEcover-NUMERICTRIM-{original,vectorized}.pdf
```

For example, `make genesis-kdp` creates upload pairs ending in
`simplecover-7x10-vectorized.pdf` and `fancycover-8.25x11-vectorized.pdf` under
`pub/kdp/`, plus their originals. Lulu uses its own namespace and geometry.
Upload the interior manuscript and its matching cover separately.

Stock, binding overrides, typography, spine lettering, and templates are not
encoded in these filenames. Choose a separate output directory to retain such
variants. Aliases share stems. Existing archived PDFs are not deleted. EPUB
single-book outputs retain names such as `ebook/genesis.epub`; source/chapter
editions retain their case-sensitive edition names.

## Build directory

`--build-dir PATH`, reading PDFs only. Default:
`build/editions/CANONICAL/CONFIG-HASH/`. Separate configuration caches prevent
stale auxiliaries from leaking between reading editions. Print runs manage their
own isolated directories under `build/PUBLISHER/CANONICAL/runs/`.

## Workflow

`--workflow serial|parallel`, reading PDFs only, default `serial`.
Serial supports every selection and PDF setting. Parallel uses the existing
chapter workflow (`bin/parallel-build --plain`), requires selection `all`, and
uses natural trim and original assets. It supports the display and translation
settings. Print profiles already run concurrently and do not accept this flag.
EPUB uses its own renderer. Neither script workflow opens the result automatically.

## Reproducible timestamp

`--source-date-epoch INTEGER` or environment `SOURCE_DATE_EPOCH`.
Must be nonnegative. Print builds default to the current Git commit timestamp;
ordinary PDFs use the toolchain's normal timestamp unless supplied. The pipeline
exports `FORCE_SOURCE_DATE=1` when pinning a timestamp. This does not promise
byte-identical output across tool installations. EPUB rejects this PDF option.

## Artifact

`--artifact FINAL.pdf`, print `--stage check` only. Selects an explicit final PDF
instead of the preset's stable paths. Requires `--reference`; structural
validation and both visual renderers still run.

## Reference

`--reference ORIGINAL.pdf`, print `--stage check` only. Selects the searchable
original against which the explicit artifact is compared. Requires `--artifact`.

```sh
bin/build genesis lulu --stage check --reference /tmp/original.pdf --artifact /tmp/final.pdf
```

## Make target resolution

`--make-target TARGET` resolves the same fields as Make. For example:

```sh
bin/build --make-target genesis-kdp-simplecover-vectorized-7x10 --plan
```

Explicit target fields override flags and Make variables. A short target leaves
unspecified fields available for overrides. The script resolver also understands
legacy partial spellings, but Make only enumerates the abbreviated and complete
forms described above. Use normal arguments for new partial combinations.

Neutral Make variables are `PRINT_PAPER`, `PRINT_INK`, `PRINT_BLEED`,
`PRINT_TRIM`, `PRINT_COVER_STYLE`, `PRINT_SPINE`, `PRINT_HARDCOVER_TEMPLATE`,
`PRINT_BINDING`, `PRINT_PROCESSING`, `PRINT_OUTPUT_DIR`, and `PRINT_PLAN`.
The corresponding historical `KDP_*` variables remain fallbacks, as do
`KDP_ARTIFACT` and `KDP_REFERENCE` for the compatibility check target.
Explicit `OUTPUT_MODE`, `THEME`, `VERSE_LAYOUT`, `COMMENTARY`, `TRANSLATION`,
`TITLE_PAGE_STYLE`, `COLORS`, `APOCRYPHA`, `REDACTOR`, or `COVER` overrides also
reach print builds. Active master settings alone do not change print presets.
Ebook Make jobs use `EBOOK_COVER` and `APOCRYPHA`.

## Read-only plan

`--plan` prints resolved configuration and paths as JSON without creating work
or output directories, probing build-tool versions, or compiling anything.
For reading PDFs and EPUB it also prints argument arrays for the commands.
For print jobs it lists every selected profile and original/vector path.

```sh
bin/build exodus lulu-hardcover --plan
make genesis-kdp PRINT_PLAN=1
```

A plan checks argument compatibility and selection names, not installed build
dependencies, actual pagination, template measurements, or publisher eligibility.

## Selection list

`--list` lists books, aliases, and source selections without building.
Chapter names are also available through tab completion and
`bin/book-subset --make-chapter-targets`.

## Help and completion

`bin/build --help` explains presets, stages, defaults, and every public option.
Read the local manual with `man -l man/pages/build.1`.

For Bash completion, source the file from the repository root:

```sh
source bin/completions/build.sh
```

It completes `bin/build` and `build` on PATH: options, preset names, publishers,
configuration values, live selections/chapters, translations, cover images, and
path arguments. The completion file asks the CLI for values so it cannot drift
from its choices. `--complete` is its internal read-only protocol.

At a new argument it offers the current positional choices together with options;
`--` as a prefix shows only long options. After an option that takes a value,
it offers that option's choices, including with `--option=value`. Directory
options complete directories, and file options complete paths, with shell quoting
for spaces. Invalid choices and free-form numbers never fall back to filenames.

## Dependencies and checks

Reading PDFs need Python, LuaLaTeX, repository fonts/assets, and the selected
translation data. Print builds additionally use Pillow, NumPy, Ghostscript, qpdf,
MuPDF, Poppler utilities, and ImageMagick. EPUB needs Python, pandoc 3, fonts,
and images; release/check require EPUBCheck and Java. EPUB reflows semantic text
and rejects PDF-only typography arguments instead of silently ignoring them.

```sh
make check-build             # CLI routing + KDP/Lulu synthetic PDF tests; no book build
make check-kdp-validator     # Synthetic visual validator self-test
make check-ebook             # EPUB renderer tests
make help                   # Interfaces only
```

Review publisher previews and physical proofs for gutters, scripts, artwork,
color, spine, and barcode placement. PDF checks establish conversion fidelity;
they do not establish editorial completeness or print quality. Before releasing
EPUB, review navigation, notes, Hebrew direction, source fonts, tables, phone
width, large type, and selected content in a reader and Kindle Previewer.

## Logs and recovery

Print runs record source hashes, effective configuration, tool versions,
commands, dependencies, and reports under
`build/PUBLISHER/CANONICAL/runs/RUN/`. Source changes during generation cause a
failure with a source-change report. A publisher/selection lock covers all
workers, including failure cleanup. Errors name the operation, candidate, log,
and report paths. Reading PDF scratch directories have their own build lock.

Vectorization uses existing public originals without requiring a manifest.
Each worker replaces vectors after all of its candidates pass structural checks;
failed conversion preserves its older vectors. Replacements across multiple
files are sequential. Two profiles finish independently; a failed build may
leave some new originals. Fix the cause, rebuild originals, then vectorize again.
Changing an interior's page count requires rebuilding its matching cover.

`make clean` preserves print records and `pub/`; `make distclean` deletes build
records while retaining `pub/`. Subsequent vectorize/check operations can still
use the public PDFs. See [doc/publishing.md](doc/publishing.md) for internals.

## Compatibility commands

`bin/kdp-publish BOOK [STAGE] --provider kdp|lulu ...` remains a compatibility
entry point for the old print interface. `bin/genesis-kdp` retains its positional
encoding/stock interface. New work should use `bin/build`.

Shared operations have neutral names: `bin/print-assets`, `bin/print-cover`,
`bin/print-inspect`, `bin/print-validate`, and `bin/print-visual-compare`.
The old `bin/kdp-*` counterparts delegate to them. Publisher-specific geometry
modules keep publisher names. `bin/kdp-source` remains a separate historical
Genesis overlay; normal builds do not apply it.

Standalone `make cover` and `make genesis-cover` use an existing interior and
`COVER_*` variables. Their script is
`bin/print-cover INTERIOR PAPER OUTPUT BUILD_DIR STYLE VOLUME SPINE [BINDING [TEMPLATE [PUBLISHER]]]`.
Legacy `make kdp KDP_INPUT=...` (`bin/kdp-pdf INPUT OUTPUT`) and
`make kdp-preflight KDP_INPUT=...` remain separate conversion/font checks.
These legacy tools are not aliases for a source build.
