# KDP paperback workflow

Run from the repository root:

```sh
make genesis-kdp             # build, then vectorize; no pixel comparison
make genesis-kdp-build       # build only
make genesis-kdp-vectorize   # convert existing originals; no TeX build
make genesis-kdp-check       # full pixel comparison; no build or conversion
make check-kdp               # synthetic tests; never builds a book
```

The six persistent PDFs are ordinary files:

```text
pub/01-genesis-interior-original.pdf
pub/01-genesis-interior-vectorized.pdf
pub/01-genesis-cover-paperback-original.pdf
pub/01-genesis-cover-hardcover-original.pdf
pub/01-genesis-cover-paperback-vectorized.pdf
pub/01-genesis-cover-hardcover-vectorized.pdf
```

Build writes the originals, including a cover sized from the original interior.
Vectorize reads those exact originals and writes the vectorized set. Check reads
those same six paths. Upload the interior and the chosen binding cover separately.

Every book, chapter, numbered alias, and source subset has the same four targets.
`make exodus-kdp` uses `pub/02-exodus-…`; `make J-kdp` uses `pub/J-…`.
Names come from `bin/book-subset --output-name TARGET`, so aliases share paths
and a lock. Case matters: `J` and `j` are distinct selections.

You can replace an original with your own PDF at the expected filename and run
vectorize, or replace either version and run check. Neither step reads a build
manifest or rejects a file because sources, timestamps, or hashes changed.
All three originals must exist before vectorization; all six PDFs must exist for check.
If an interior's page count changes, supply a correspondingly sized cover.

`check-genesis-kdp` aliases `genesis-kdp-check`. All standard KDP targets use
the soft PDF encoding profile by default. The compatibility `bin/genesis-kdp`
CLI delegates to this pipeline.

## Print configuration

Defaults preserve the successful Genesis print profile:

| Variable | Default | Supported values |
| --- | --- | --- |
| `KDP_PAPER` | `premium-color` | `premium-color`, `standard-color` |
| `KDP_INK` | `premium-color` | Must match `KDP_PAPER` |
| `KDP_BLEED` | `no-bleed` | `no-bleed` |
| `KDP_TRIM` | `7x10` | `7x10` |
| `KDP_COVER_STYLE` | `simple` | `simple`, `fancy` |
| `KDP_SPINE` | `ld` | `ld`, `nameless` |

Paper names follow the existing cover CLI: both color stocks are white paper.
Unsupported combinations fail before generation. Black ink, cream paper, other
trims, and interior bleed need source/template support; no conversion substitutes
for that work. Supply the same configuration on build, vectorize, and check:

```sh
make exodus-kdp KDP_PAPER=standard-color KDP_INK=standard-color
make exodus-kdp-check KDP_PAPER=standard-color KDP_INK=standard-color
```

The PDF timestamp defaults to the current Git commit timestamp. Set the standard
`SOURCE_DATE_EPOCH` environment variable to pin another timestamp (or use the CLI's
`--source-date-epoch`). It is recorded as configuration and supplied to TeX with
`FORCE_SOURCE_DATE=1`; final qpdf IDs are deterministic. Byte-for-byte
reproducibility across different tool installations is not promised.

The searchable interior uses book/lite, horizontal verses, commentary, inline
English, fancy title pages, default colors, apocrypha, uncensored redaction, no
interior cover image, and KDP rules/assets. This print profile is explicit in
`bin/kdp-publish` and recorded in the manifest. Ordinary Make display variables do
not silently change it. The ordinary subset generator selects the text; the old
Genesis-only editorial overlay is not applied.

The cover is generated from that exact searchable interior's page count. Premium
color uses 0.002347 inches per page for its spine. Covers always include their
outer bleed; `KDP_BLEED` describes the interior. Spine lettering is omitted below
79 pages. The supported 7×10 profile checks even page counts of 24–828 for premium
color and 72–600 for standard color. Very short chapter subsets still resolve as
targets but fail the paperback page-count check. These bounds and spine rules
follow KDP's [submission guidelines](https://kdp.amazon.com/en_US/help/topic/G201857950)
and [cover guidance](https://kdp.amazon.com/en_US/help/topic/G201953020), checked
September 14, 2026.

Hardcover geometry, template overrides, artwork provenance, stock, and eligibility
are documented in [PUBLISH.md](../PUBLISH.md#hardcover-covers). The original layouts of both cover styles
share `pub/covers/simple/cover.tex` typography; dimensions come from
`bin/kdp_cover_geometry.py`.

## Working files and recovery

TeX auxiliaries, prepared assets, logs, inspection reports, and build provenance
remain under `build/kdp/<canonical>/runs/<run>/`. Active cover templates and art
live in `pub/covers/`. The archived proof copies in `pub/` are independent.

Stage inputs never depend on PDFs hidden in those run directories. Ghostscript's
intermediate output is `pub/<canonical>-<part>-outlined.pdf`; qpdf writes
`pub/<canonical>-<part>-vectorized-pending.pdf`. After all three parts pass structural
checks, the pending files replace the vectorized files and outlined files are
removed. On conversion/check failure the previous vectorized set stays intact;
intermediate files remain for diagnosis. Replacement of the three files is sequential,
not an atomic set operation. A failed build may leave partially updated originals;
fix the cause and rerun build before converting them.

Every operation prints its log path, and failures identify the command and candidate.
Concurrent operations on the same selection and variant share a lock. Reports live
in the run directory printed by that invocation. `make clean` preserves these
records and `pub/`; `make distclean` deletes build logs/auxiliaries but preserves
the six public PDFs. Vectorize and check still work after deleting `build/`.

To check a different pair explicitly:

```sh
make genesis-kdp-check KDP_ARTIFACT=/path/final.pdf KDP_REFERENCE=/path/original.pdf
```

## Validation

Vectorization uses Ghostscript font outlining followed by qpdf cleanup. Structural
checks cover PDF validity, zero remaining fonts/text, page geometry, new raster
placements, and file size. It does not run the visual validator or its self-test.

Only `-kdp-check` runs the damaged-image self-test and renders every page of all three
pairs at 300 DPI with MuPDF and Poppler for pixel comparison. It also repeats
structural validation. Difference crops and visual HTML/JSON reports stay in that
check's run directory. Check never rebuilds or changes the PDFs.

The synthetic tests exercise conversion and visual comparison without building a
book. They cannot establish that the current book sources compile. Physical layout,
color, gutter, spine and barcode review still require inspection of the output.

Hardcover builds also produce `pub/<canonical>-cover-hardcover-alt-original.pdf`
and, in vectorizing targets, `pub/<canonical>-cover-hardcover-alt-vectorized.pdf`.
The existing covers are retained. The alternate centers “The Nameless” in the
artwork circle and places the ink centers of “We” and the volume title on its arcs.
Adjust `\CoverTitleSeparation` in `pub/covers/fancy/cover.tex` (default `0.212`,
a fraction of panel height): larger spreads the titles farther apart. Rerun the
relevant target, e.g. `make genesis-kdp-hardcover` or `make J-kdp-hardcover`.
