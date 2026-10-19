```table-of-contents
```

## Print: quick start

Run from the repository root. These commands create local PDFs; they do not
upload or publish anything.

```sh
make genesis-kdp
# Equivalent: bin/kdp-publish genesis all --provider kdp

make genesis-lulu
# Equivalent: bin/kdp-publish genesis all --provider lulu
```

Both commands produce two matching interior/cover pairs. Their complete defaults
are:

| Target | Cover artwork | Cover construction | Interior trim (inches) | Interior and cover processing |
| --- | --- | --- | --- | --- |
| `[book]-kdp` | simple | paperback | 7 × 10 | vectorized |
| `[book]-kdp` | fancy | hardcover casewrap | 8.25 × 11 | vectorized |
| `[book]-lulu` | simple | perfect-bound paperback | 7 × 10 | original |
| `[book]-lulu` | fancy | hardcover casewrap | 7 × 10 | original |

All use color on white paper, premium color by default, no interior bleed,
LD spine lettering, the shared print typography, and the soft PDF encoding
profile. Each pair has its own interior; the cover is measured from that exact
interior's page count and trim. The two pairs run concurrently with isolated
assets, TeX caches, work directories, and logs. There is no alternate fancy cover.

Replace `genesis` with any book, chapter, numbered alias, or source subset from
`make list`: `exodus`, `genesis-1`, `1-samuel`, `1-samuel-1`, `J`, `P`, `j`,
`court`, etc. Case matters: `J` and `j` are different editions. Aliases share the
canonical filename stem returned by `bin/book-subset --output-name genesis`
(`01-genesis`). Every selection has the same print interface for both publishers.
Very short or long selections can resolve successfully but exceed page limits.

To inspect the exact configuration and filenames without building:

```sh
make genesis-kdp PRINT_PLAN=1
bin/kdp-publish genesis all --provider kdp --plan
make exodus-lulu-fancycover-vectorized-8.25x11 PRINT_PLAN=1
```

## Print target parameters

The grammar is:

```text
make [book]-[publisher][-cover][-processing][-trim][-stage]
```

Brackets denote optional components, except book and publisher. Keep components
in this order; each optional component can be omitted independently.

| Component | Values | What it controls when supplied | When omitted |
| --- | --- | --- | --- |
| book | Any selection from `make list` | Text selection and canonical output stem | Required |
| publisher | `kdp`, `lulu` | Cover geometry policy, eligibility checks, output namespace, and preset defaults | Required in Make; CLI defaults to KDP |
| cover | `simplecover`, `fancycover` | Select one cover preset and its corresponding interior | Both presets |
| processing | `original`, `vectorized` | Both the interior and cover: keep searchable PDFs, or also outline their fonts | KDP: vectorized; Lulu: original |
| trim | `7x10`, `8.25x11`, `default` | Interior page width and height, in inches; cover dimensions follow automatically | Preset trim from the defaults table |
| stage | `build`, `vectorize`, `check` | Run only the named operation on the selected presets | Build and apply selected processing (`all` in the CLI) |

`-default` and no trim suffix are exactly equivalent, including when a Make
variable supplies the trim. Explicit `-7x10` or `-8.25x11` overrides that
variable and the preset's trim. Explicit cover and processing qualifiers likewise
override their Make variables and publisher defaults. Specifying processing or
trim without a cover applies that override to **both** presets.

Examples, with equivalent script calls:

| Make target | Equivalent command |
| --- | --- |
| `make genesis-kdp-simplecover` | `bin/kdp-publish genesis all --provider kdp --cover-style simple` |
| `make genesis-kdp-fancycover` | `bin/kdp-publish genesis all --provider kdp --cover-style fancy` |
| `make genesis-lulu-original` | `bin/kdp-publish genesis all --provider lulu --processing original` |
| `make genesis-lulu-vectorized` | `bin/kdp-publish genesis all --provider lulu --processing vectorized` |
| `make genesis-kdp-7x10` | `bin/kdp-publish genesis all --provider kdp --trim 7x10` |
| `make genesis-kdp-default` | `bin/kdp-publish genesis all --provider kdp` |
| `make genesis-kdp-simplecover-original-8.25x11` | `bin/kdp-publish genesis all --provider kdp --cover-style simple --processing original --trim 8.25x11` |
| `make exodus-lulu-fancycover-vectorized-7x10` | `bin/kdp-publish exodus all --provider lulu --cover-style fancy --processing vectorized --trim 7x10` |

This table composes: `simplecover` maps to `--cover-style simple`, `fancycover`
to `--cover-style fancy`, processing to `--processing VALUE`, and a concrete trim
to `--trim VALUE`. A stage suffix replaces positional `all` with that stage.
For **every** print target, the following is also its exact equivalent, using the
same resolver as Make:

```sh
bin/kdp-publish --make-target genesis-lulu-fancycover-vectorized-8.25x11
# Replace that target with any supported print target; add --plan to inspect it.
```

When passing both `--make-target` and flags, explicit target qualifiers win over
flags, just as they do over Make variables. `-default` contributes no override.

### Stages and existing PDFs

| Make target pattern | Equivalent script call | Effect |
| --- | --- | --- |
| `[book]-[publisher]` | `bin/kdp-publish BOOK all --provider PUBLISHER` | Build both originals; outline them only if selected processing is vectorized |
| `[book]-[publisher]-build` | `bin/kdp-publish BOOK build --provider PUBLISHER` | Build originals only |
| `[book]-[publisher]-vectorize` | `bin/kdp-publish BOOK vectorize --provider PUBLISHER` | Outline existing originals; never rebuild |
| `[book]-[publisher]-check` | `bin/kdp-publish BOOK check --provider PUBLISHER` | Compare existing originals with vectors; never build or convert |

Insert any cover, processing, and trim qualifiers before the stage suffix.
For example:

```sh
make genesis-kdp-fancycover-original-7x10
# bin/kdp-publish genesis all --provider kdp --cover-style fancy --processing original --trim 7x10
make genesis-kdp-fancycover-7x10-vectorize
# bin/kdp-publish genesis vectorize --provider kdp --cover-style fancy --trim 7x10
make genesis-kdp-fancycover-7x10-check
# bin/kdp-publish genesis check --provider kdp --cover-style fancy --trim 7x10
```

`-original` builds originals only; `-vectorized` builds originals and converts
both files. The **noun** `-vectorized` selects output processing; the **verb**
`-vectorize` runs conversion on existing files. Explicit stages take precedence
over processing: `-vectorized-build` still only builds originals,
`-original-vectorize` still converts existing originals, and `-check` always needs
both versions. No build/vectorize command runs the optional full pixel comparison.
Lulu originals are used directly by default; there is no automatic raster
flattening or `-final.pdf` generation. Outlining remains an explicit Lulu option
while its upload requirements are evaluated.

## Output filenames

```text
pub/[publisher]/[canonical]-{interior,cover}-[simplecover|fancycover]-[trim]-[original|vectorized].pdf
```

The resolved numeric trim is always in the filename, including when omitted or
spelled `-default`. Publisher directories prevent different spine geometries from
overwriting each other. A different style or trim also has distinct paths.
There are no `paperback`, `hardcover`, or alternate-cover names in current outputs.

The default Genesis upload pairs are:

| Command | Interior PDF | Cover PDF |
| --- | --- | --- |
| `make genesis-kdp` (simple) | `pub/kdp/01-genesis-interior-simplecover-7x10-vectorized.pdf` | `pub/kdp/01-genesis-cover-simplecover-7x10-vectorized.pdf` |
| `make genesis-kdp` (fancy) | `pub/kdp/01-genesis-interior-fancycover-8.25x11-vectorized.pdf` | `pub/kdp/01-genesis-cover-fancycover-8.25x11-vectorized.pdf` |
| `make genesis-lulu` (simple) | `pub/lulu/01-genesis-interior-simplecover-7x10-original.pdf` | `pub/lulu/01-genesis-cover-simplecover-7x10-original.pdf` |
| `make genesis-lulu` (fancy) | `pub/lulu/01-genesis-interior-fancycover-7x10-original.pdf` | `pub/lulu/01-genesis-cover-fancycover-7x10-original.pdf` |

KDP also retains four searchable originals; Lulu's default produces four original
PDFs. Upload the interior as the manuscript and its matching cover separately.
Older publication PDFs are left in place as archives. Rebuilding originals does
not delete previously vectorized files: rerun vectorization after changing originals.
Vectorize/check accept replacements at these paths without requiring a manifest.
If an interior's page count changes, its cover must be regenerated too.

## Artwork, construction, and publisher geometry

Artwork, interior geometry, and physical cover construction are separate inputs.
`simplecover` selects typography on a plain cover; `fancycover` adds the saved
illustrated artwork with the same typography. They default to paperback and
hardcover construction respectively to make the short commands useful, but
neither artwork determines interior dimensions. Either supports either trim and
either processing choice. The CLI's `--binding paperback|hardcover` overrides
construction independently, for example:

```sh
bin/kdp-publish genesis all --provider lulu --cover-style fancy \
  --binding paperback --trim 7x10 --processing original --output-dir pub/lulu-fancy-soft
# Illustrated paperback; choose a separate output directory for this variant.
```

This distinction is necessary: physical hardcover wraps need board overhang,
wrap, hinges, and a different spine calculation even at the same interior trim.
Custom stock, construction, spine lettering, or encoding variants are not all
encoded in basenames. Use a separate `--output-dir` when retaining such variants.

**KDP and Lulu currently do use different spine math.** For N pages, trim W×H,
and dimensions in inches, the implemented policies are:

| Publisher / construction | Spine | Panel size | Outer bleed / wrap |
| --- | --- | --- | --- |
| KDP paperback | N × caliper (premium: 0.002347; standard: 0.002252) | W × H | 0.125 on each outside edge |
| KDP hardcover | N × 0.002347 + 4.8/25.4 | (W + 5/25.4) × (H + 6/25.4) | 15/25.4 on each outside edge |
| Lulu paperback, 60# white | N / 444 + 0.06 | W × H | 0.125 on each outside edge |
| Lulu hardcover casewrap | Page-count lookup in `bin/lulu_cover_geometry.py` | (W + 0.125) × (H + 0.25) | 0.75 on each outside edge |

Sheet width is twice panel width plus spine plus twice wrap; sheet height is
panel height plus twice wrap. Hinges are inside the panels, not extra strips
added to sheet width. The KDP model uses a 10 mm hinge and Lulu's existing model
reserves 0.5 inch inside each panel. For example, at 600 pages and 7×10 Lulu's
paperback spine is 1.411351 inches; its hardcover spine is 1.625 inches.

KDP paperback calipers follow its [cover guidance](https://kdp.amazon.com/en_US/help/topic/G201953020).
The KDP hardcover formula is an inferred model from a
[recorded calculator template](https://github.com/hackerbay/twenty-minute-table/blob/main/book/cover.py),
not an Amazon-published formula. At 224 pages and 8.25×11 it gives approximately
18.790×12.417 inches and a 0.715-inch spine. Compare with the actual
[KDP cover calculator template](https://kdp.amazon.com/cover-calculator).
Lulu's [spine formula and table](https://help.api.lulu.com/en/support/solutions/articles/64000254616-how-is-spine-width-calculated-)
and [casewrap allowances](https://help.lulu.com/en/support/solutions/articles/64000308572-creating-your-hardcover-casewrap-cover)
are separate policies. Both publisher namespaces remain even where a future
parameter happens to have identical behavior; they provide a place for future
stock, geometry, PDF-processing, and other upload differences.

An exact KDP hardcover template can override the inferred model:

```json
{"pages":224,"trim_width":8.25,"trim_height":11,"paper":"premium-color",
 "spine":0.715,"wrap":0.591,"hinge":0.394,"panel_width":8.447,"panel_height":11.236}
```

Use `--hardcover-template /absolute/path/template.json` or
`KDP_HARDCOVER_TEMPLATE=/absolute/path/template.json`. These are example
measurements, not a Genesis template. The pipeline rejects page-count, stock,
or trim mismatches and records the template hash. Lulu rejects KDP templates.

## Further configuration and limits

These variables apply to **both** publishers. The `KDP_` prefix is retained for
existing invocations; the explicit publisher selects the geometry policy.

| Make variable | Script option | Default / supported values |
| --- | --- | --- |
| `KDP_PAPER` | `--paper` | `premium-color`; also `standard-color` |
| `KDP_INK` | `--ink` | `premium-color`; must match paper |
| `KDP_BLEED` | `--bleed` | Only `no-bleed` for the interior |
| `KDP_TRIM` | `--trim` | `default`; also `7x10`, `8.25x11` |
| `KDP_COVER_STYLE` | `--cover-style` | Unset (both); `simple` or `fancy` |
| `PRINT_PROCESSING` | `--processing` | Unset (publisher preset); `original` or `vectorized` |
| `PRINT_BINDING` | `--binding` | Unset (cover preset); `paperback` or `hardcover` |
| `KDP_SPINE` | `--spine` | `ld`; also `nameless` |
| `KDP_HARDCOVER_TEMPLATE` | `--hardcover-template` | Unset; exact KDP hardcover JSON |
| `PRINT_OUTPUT_DIR` | `--output-dir` | `pub/<publisher>/` |
| `PRINT_PLAN=1` | `--plan` | Off; read-only resolved plan when enabled |
| `KDP_ARTIFACT`, `KDP_REFERENCE` | `--artifact`, `--reference` | Unset; explicit existing pair for `check` |
| `SOURCE_DATE_EPOCH` (environment) | `--source-date-epoch` | Current Git commit timestamp for builds |
| CLI only | `--variant` | `soft`; also `medium`, `hard` PDF encoding profiles |

For medium/hard encoding, default outputs are under
`pub/<publisher>/<variant>/`. An explicit output directory replaces that entire
path. Encoding `hard` is unrelated to physical hardcover construction. Ordinary
Make display settings (`OUTPUT_MODE`, `THEME`, etc.) do not change the print
profile. Print uses book/lite typography, horizontal verses, commentary, inline
English, fancy title pages, default colors, apocrypha, uncensored redaction,
no interior cover image, and print-safe assets/rules. Trim changes page geometry
without scaling a completed PDF or changing typography.

KDP hardcover always uses premium-color stock even if the paperback uses
standard color. Lulu supports premium or standard color on 60# white uncoated;
80# coated, magazines/comics, linen covers, and dust jackets need other geometry
policies. Black ink, cream paper, arbitrary trims, and interior bleed are not
implemented. Supported page-count checks require even counts:

| Profile | Pages |
| --- | --- |
| KDP paperback, premium color | 24–828 |
| KDP paperback, standard color | 72–600 |
| KDP hardcover | 76–550 |
| Lulu paperback | 32–800 |
| Lulu hardcover | 24–800 |

Out-of-range builds fail. Spine text is omitted below 79 pages for KDP and through
80 pages for Lulu. A supported layout combination generates geometry; it does
not promise availability of every stock/trim/binding combination in a publisher's
catalog or distribution program. Compare the resulting cover with the publisher's
custom template after uploading the interior and review its preview before
ordering a proof.

The fancy cover uses `pub/covers/fancy/assets/front-textless.png`; its saved
image-generation prompt is alongside it. Builds use saved assets and deterministic
TeX, without AI calls. The 1024×1536 artwork has limited native print resolution;
font outlining does not add detail to raster illustrations. PDF timestamps are
pinned, but byte-for-byte reproducibility across tool installations is not promised.

## Dependencies, checks, and recovery

Print builds need Python with Pillow and NumPy, LuaLaTeX, repository fonts,
Ghostscript (`gs`), qpdf, MuPDF (`mutool`), Poppler utilities, and ImageMagick
(`magick`). Font outlining preserves images and converts text to vector paths;
original PDFs retain searchable text. Conversion includes structural checks
but no full pixel comparison. `-check` additionally renders all selected pairs
with MuPDF and Poppler at 300 DPI, which can take a long time. It requires
original and vectorized PDFs even for Lulu, whose normal output is original.

```sh
make help                    # Show interface; no build.
make list                    # List selections; no build.
make check-kdp               # Synthetic KDP + Lulu tests; no book build.
make check-kdp-validator     # Synthetic visual damage detection; no book build.
make check-ebook             # Renderer regressions; no PDF/EPUB build.
# Equivalent validation commands:
python3 -m unittest discover -s tests -p 'test_kdp*.py' -v
python3 -m unittest discover -s tests -p 'test_lulu.py' -v
python3 bin/kdp-visual-compare --self-test
make -C ebook test
```

Logs, reports, assets, TeX caches, and provenance are under
`build/<publisher>/<canonical>/runs/<run>/`. A publication lock for each canonical
selection/publisher remains held until every worker finishes, including on
failure. Aliases and encoding variants share this lock. Errors print the command,
candidate, log, and report paths. Successful conversion replaces a pair only
after both files pass; a failed conversion preserves its older vectorized pair.
Two presets finish independently, and file replacements are sequential rather
than atomic across an entire publication set. A failed build can leave partially
updated originals; rerun the build after fixing its source or tool failure.

`make clean` removes ordinary TeX auxiliaries but preserves both publishers'
build records and `pub/`. `make distclean` removes build records but keeps `pub/`;
vectorize/check work from those stable PDFs without a build manifest. Inspect
publisher previews and physical proofs for gutters, scripts, artwork, color,
spine, and barcode placement. PDF checks establish conversion fidelity, not
editorial completeness or print quality.

Legacy `make kdp KDP_INPUT=...` (`bin/kdp-pdf INPUT OUTPUT`) and
`make kdp-preflight KDP_INPUT=...` (`bin/kdp-preflight INPUT`) remain separate
conversion/preflight tools. Standalone `make cover` and `[book]-cover` call
`bin/kdp-cover INTERIOR PAPER OUTPUT BUILD_DIR STYLE VOLUME SPINE [BINDING [TEMPLATE [PUBLISHER]]]`
with the corresponding `COVER_*` variables. They do not build an interior.
The old `*-paperback`, `*-hardcover`, and `make-genesis-lulu-paperback` targets
have been removed; use `*-simplecover` and `*-fancycover` and an explicit trim
when needed. `bin/genesis-kdp` still delegates to the shared Genesis pipeline.
For implementation and recovery details, see [doc/publishing.md](doc/publishing.md).

## Ebook

### Dependencies

Building the ebook requires:
- python
- pandoc 3,
- the repository's fonts and images, and
- EPUBCheck somewhere in the PATH (with its Java runtime).

### Build the ebook with one command

```sh
make genesis-ebook-release       # Build ebook/genesis.epub; internal validation and EPUBCheck must pass.
make exodus-ebook-release        # Build ebook/exodus.epub with the same checks.
make J-ebook-release             # Build ebook/J.epub using the print selector's J filtering.
make P-ebook-release             # Build ebook/P.epub using the print selector's P filtering.
make genesis-1-ebook-release     # Build ebook/genesis-1.epub for one chapter.
make ebook-release              # Build ebook/we-the-nameless.epub from the active master include sequence.
```

Choose **one** command for the edition you want. Then preview that `.epub` in
Kindle Previewer and an EPUB reader; check navigation, notes, Hebrew direction,
source fonts, tables, phone width, and large type. Upload the `.epub` as the ebook
manuscript. The paperback wrap is not an ebook cover; use a front-cover image for
the store listing. The default embedded cover is `img/covers/we-cover-8.*`.

```sh
make genesis-ebook-release EBOOK_COVER=we-cover-8  # Choose an image basename from img/covers (no extension).
make genesis-ebook-check         # Recheck an existing EPUB; never rebuild it; EPUBCheck is required.
make ebook-check                 # Recheck the existing complete EPUB (also called ebook-validate).
make genesis-ebook               # Development build; EPUBCheck runs if installed, but is optional.
make ebook                      # Development build of the active complete edition.
```

An EPUB release command rebuilds from source and replaces the output only after
validation succeeds. A check validates the existing archive, not its freshness;
rerun the release command after edits. Aliases share filenames and stable store
identifiers; `J` and `j` have distinct identifiers. Avoid concurrent builds of the
same edition. `EBOOK_COVER=none` omits the embedded cover for development.

**EPUB remains a work in progress.** Selection uses the print subset authority,
including source filtering, but the renderer reflows semantic verses/sentences,
not printed pages. It retains its existing omission of standalone print apocrypha
and frontispiece files; alternate verses inside chapters remain. Do not treat
successful validators as proof of complete editorial fidelity. Review the selected
content and [renderer notes](ebook/README.md) before a public release.
