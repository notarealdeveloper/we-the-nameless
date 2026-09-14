# KDP paperback workflow

The **two separate upload files** for Genesis are:

- `build/kdp/01-genesis/artifacts/01-genesis-interior.pdf`
- `build/kdp/01-genesis/artifacts/01-genesis-cover.pdf`

These paths appear only after both candidates pass validation. They resolve through
one atomic release pointer. Nothing uploads, opens a viewer, combines the PDFs, or
writes compatibility PDFs at the repository root.

## Commands

```sh
make help
make genesis-kdp-build       # searchable print interior and separate raw cover
make genesis-kdp-vectorize   # outline, clean, validate, and promote; no TeX build
make genesis-kdp             # both stages in sequence
make genesis-kdp-check       # fresh validation of both recorded PDFs; no build
make check-kdp               # synthetic PDF tests; never builds a book
make check-kdp-validator     # visual validator's damaged-image self-test
```

Every book, chapter, numbered alias, and source subset from `bin/book-subset` gets
all four targets. They are enumerated in Make's target database for normal shell
Make completion, rather than hidden behind a catch-all rule. Examples include
`exodus-kdp`, `01-genesis-kdp-build`, `J-kdp-check`, and `genesis-1-kdp-build`.
Canonical directory and PDF names come exclusively from
`bin/book-subset --output-name TARGET`; aliases therefore share a lock and release.
Ordinary `make genesis`, `make J`, etc. retain their existing behavior.

`check-genesis-kdp` aliases `genesis-kdp-check`; `genesis-kdp-soft` aliases
`genesis-kdp`. The legacy `bin/genesis-kdp [--check] soft|medium|hard PAPER INK BLEED`
CLI delegates to the same system. Medium and hard diagnostic encodings have their
own subdirectories, `build/kdp/01-genesis/medium/` and `hard/`. They must pass the
same checks; PDF 1.4 flattening in hard mode can legitimately fail raster checks.
Old Genesis artifacts are not silently adopted into the new manifest format.

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
`FORCE_SOURCE_DATE=1`; final qpdf IDs are deterministic. Use the same timestamp
when checking an archived release after changing commits. Byte-for-byte
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

## Layout, provenance, and failure recovery

```text
build/kdp/<canonical>/
  .lock
  build.json                     # last successfully prepared reference pair
  reference -> runs/<build>/reference
  current -> runs/<validated-release>
  artifacts -> current/artifacts
  manifest.json -> current/manifest.json
  runs/<unique-id>/
    reference/                   # build run: interior.pdf and cover.pdf
    assets/assets.json           # selected derivatives and exact options
    work/interior/ and work/cover/
    logs/                        # complete command output, separate operations
    reports/<artifact>/          # inspection, structural JSON, visual HTML/JSON
    artifacts/                   # vectorization run: final candidate pair
    build.json or manifest.json
build/kdp/assets/                # shared, content-addressed print derivatives
```

Each operation prints a flushed START/PASS line with book, stage, artifact and log.
Failures identify the exit status, command/operation, candidate, log and report
location. Failed/interrupted runs remain available for diagnosis; neither a stale
TeX PDF nor one successfully validated half of a pair can become a release.
A concurrent operation on the same canonical book exits with the lock location;
other books use independent auxiliary directories. Locks release on process exit.

After an asset, TeX or cover failure, fix the cause and repeat `-kdp-build`.
After conversion or validation failure, inspect that run's logs/reports and repeat
`-kdp-vectorize` if sources/configuration are unchanged. Otherwise rebuild first.
A successful new build does not replace the previously validated release until
vectorization succeeds. Check validates the recorded release, even if a newer
reference build exists. Never manually copy a candidate into the upload paths.

The manifest records source/config hashes, exact command arrays, versions of TeX,
Ghostscript, qpdf, MuPDF, Poppler, ImageMagick, Python, Pillow and NumPy; recorded
TeX input hashes; reference/final SHA-256, sizes, page/font counts; upload locations;
and report paths. It embeds the reference build record and its asset provenance.
Source hashing is deliberately conservative across repository TeX/code/assets,
including ignored local inputs, so unrelated source edits may require rebuilding.
Check rejects changed sources, configuration, tool versions, dependencies or PDFs.

To compare an explicitly named artifact with its reference without a manifest or
rebuild, use either interface below. This performs fresh structural and visual
checks, but makes no claim about current source freshness or paperback eligibility:

```sh
make genesis-kdp-check KDP_ARTIFACT=/path/final.pdf KDP_REFERENCE=/path/reference.pdf
bin/kdp-publish genesis check --artifact /path/final.pdf --reference /path/reference.pdf
```

Retain runs needed by `current`, `build.json`, and the current manifest's reference
path. `make clean` removes TeX logs/auxiliary files, including historical logs;
`make distclean` removes all build outputs and publishing evidence. Archive the
referenced runs before either if the evidence must be retained.

## Validation and remaining review

Both PDFs use identical Ghostscript no-font, no-downsampling, unchanged-color,
JPEG/JPX-preserving, overprint-preserving controls, followed by conservative qpdf
page extraction. Validation requires successful tools, valid unencrypted PDFs,
zero fonts/extractable text, MuPDF resource/content inspection, unchanged page
geometry including ArtBox and UserUnit (the established 0.01-point box tolerance), no new raster placements, and a
650,000,000-byte limit. MuPDF and Poppler independently compare every page at 300
DPI after the damaged-image self-test. Neither renderer aligns, scales, or shifts
pages. Failures retain localized before/after/difference crops and reports.
Checks rerender rather than trusting the older visual cache/reclassification tools.

Live transparency and remaining images below 300 PPI are recorded as human-review
items, not concealed or automatically flattened. Upsampled legacy assets retain
an explicit warning: a higher effective PPI does not restore source detail.
Read each structural report even after a PASS. A visual match establishes fidelity
to the reference, not that the reference is itself well designed or acceptable.

KDP Print Previewer review and a physical proof remain necessary for gutters,
trim safety, color, spine lettering, barcode placement, and readability. For a
future authorized book-build trial, start with a modest subset that meets the
minimum page count, then run full Genesis. Implementation tests use synthetic
fixtures only and do not establish that current book sources compile or pass.
