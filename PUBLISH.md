```table-of-contents
```

## Basics

```sh
make help
# Show the make interface; no build.

make list
# List available selections; no build.

make check-kdp
# Run synthetic PDF pipeline tests; no book build.

make check-kdp-validator
# Test that visual damage is detected; no book build.

make check-ebook
# Run renderer regressions; no PDF or EPUB build.

make clean
# Remove ordinary TeX auxiliaries; preserve build/kdp and pub evidence.
```

`make distclean` deletes build logs and auxiliaries, but keeps the publication
PDFs in `pub/`. Vectorize and check use those PDFs directly.

Legacy `make kdp KDP_INPUT=...`, `kdp-preflight`, and standalone `*-cover` targets
remain for compatibility. They do not replace the outlined, validated pair above.
For internals and recovery details, see [doc/publishing.md](doc/publishing.md).

## Paperback

### Dependencies

Building the book for physical publication requires:
- python with pillow and numpy,
- LuaLaTeX,
- the fonts in the repo's `fonts/` directory,
- ghostscript (`gs`),
- qpdf,
- mupdf (`mutool`),
- poppler utilities, and
- imagemagick (`magick`).

Once you have the dependencies, run the commands below **from the repository root**.

These commands create local files; nothing uploads or publishes automatically.

Replace `genesis` with `exodus`, `J`, `P`, `j`, `p`, `court`, `1-samuel`, `genesis-1`, or another name from `make list`.

**Case matters:** `J` and `j` select different editions. Numbered aliases work too.

### Build the paperback step by step

Run these two commands **in order**:

```sh
make genesis-kdp-build
# 1. Build searchable reference interior and a cover sized from its page count.

make genesis-kdp-vectorize
# 2. Convert fonts to paths, clean, and structurally check all four PDFs.
```

`make genesis-kdp-vectorize` uses the existing originals; it does not rebuild
them. Neither command runs the optional pixel comparison described below.

Build writes `pub/<canonical>-{interior,cover}-{paperback,hardcover}-original.pdf`. Vectorize reads
those files and writes `pub/<canonical>-{interior,cover}-{paperback,hardcover}-vectorized.pdf`.
You can copy replacement PDFs to the expected paths and rerun vectorize or
check; no build manifest is required.

Failures print log/report paths under `build/kdp/<canonical>/runs/<run>/`.
Fix TeX/assets and repeat build, or fix an original PDF and repeat vectorize.
A failed conversion preserves older vectorized files; wait for the command's PASS.

Defaults: **7×10-inch paperback, premium color on white paper, no interior bleed,
simple cover, LD spine**. Use those settings in the publisher's setup. Alternatives:

```sh
make genesis-kdp KDP_COVER_STYLE=fancy
# Use the illustrated wrap.

make genesis-kdp KDP_SPINE=nameless
# Use the title instead of LD on the spine.

make genesis-kdp KDP_PAPER=standard-color KDP_INK=standard-color
# Use standard color white stock.
```

Repeat the same options on every separate build/vectorize/check command. The
pipeline currently enforces even page counts of 24–828 (premium) or 72–600
(standard). Short chapter selections may fail these limits; large selections
may need smaller editions. Other trims, black ink, cream paper, interior bleed,
need additional layout support. Other printers may accept these
PDFs, but verify their trim, stock, spine, bleed, and file requirements first.

After upload, inspect KDP Print Previewer, order a proof while the listing is
still a draft, and inspect the physical copy before publishing. Check gutters,
small scripts, images, color, spine, and barcode placement. Passing comparisons
means faithful conversion; it does not replace editorial or physical review.

### Build the paperback with one command

```sh
make genesis-kdp
# Build and vectorize both bindings, including the alternate hardcover cover.
```

`make genesis-kdp` combines the stages from `make genesis-kdp-build` and
`make genesis-kdp-vectorize`. Paperback and hardcover run concurrently, each
building its interior and covers before vectorizing them. The same applies to
other subset targets, and the standalone build and vectorize stages also run
both bindings concurrently. Each binding has separate working directories,
assets, TeX caches and logs; terminal messages interleave as complete lines
labelled `paperback` or `hardcover`. The publication lock stays held until both
workers finish, including on failure. It **does not include
`make genesis-kdp-check`**. Structural checks are included; the full pixel
comparison is a separate, optional command.

When that command finishes successfully, upload these **two separate files**:

```sh
pub/01-genesis-interior-paperback-vectorized.pdf
pub/01-genesis-cover-paperback-vectorized.pdf
```

For another selection, use the same command pattern:

```sh
make exodus-kdp
# Upload pub/02-exodus-interior-paperback-vectorized.pdf and the paperback cover (use the hardcover interior with the hardcover cover).

make J-kdp
# Upload pub/J-interior-paperback-vectorized.pdf and the paperback cover (use the hardcover interior with the hardcover cover).

make P-kdp
# Upload pub/P-interior-paperback-vectorized.pdf and the paperback cover (use the hardcover interior with the hardcover cover).

bin/book-subset --output-name genesis
# Print the canonical filename stem: 01-genesis.
```

Upload the interior as the manuscript and the selected binding cover separately.

The searchable `-original.pdf` files remain alongside the vectorized files for comparison.

### Optionally compare the paperback PDFs

After either the step-by-step build or the combined command, run:

```sh
make genesis-kdp-check
# Compare existing originals and vectorized PDFs; do not build or vectorize.
```

This separate target compares both interior and cover pairs in `pub/`, rendering
every page using both MuPDF and Poppler at 300 DPI. The full pixel comparison can
take a long time and runs only when explicitly requested; `make genesis-kdp`
does not run it. Both the original and vectorized PDFs must already exist.

### Hardcover interiors and covers

Use `make genesis-kdp-paperback` or `make genesis-kdp-hardcover` to build and
vectorize only that binding's interior and cover. These suffixes work for every
subset and chapter, including `exodus` and `J`. `make genesis-kdp` builds both.
All outputs go directly in `pub/`. Each binding uses its own interior:
`<canonical>-interior-paperback-{original,vectorized}.pdf` at 7×10 inches and
`<canonical>-interior-hardcover-{original,vectorized}.pdf` at 8.25×11 inches.
Hardcover uses `ConfigOutputMode=hard`, keeping book typography and margins.
Old unqualified `interior` PDFs are untouched archives, not current outputs.

Every combined KDP subset build also produces `pub/<canonical>-cover-hardcover-original.pdf`
and `-vectorized.pdf`. Paperback covers now have `cover-paperback` in their basename;
old `cover-original` / `cover-final` files are untouched archives, not current outputs.
There are eight current PDFs per subset (four originals and four vectorized). `KDP_COVER_STYLE` selects the paperback style;
the hardcover always uses the illustrated artwork with shared simple-cover typography.
The LD mark remains on the spine. No new author line is invented.

Cover geometry comes from the actual interior's page count and page dimensions in
`bin/kdp_cover_geometry.py`. With trim W×H in inches and N pages:

- Paperback: spine = N × paper caliper; sheet = (2W + spine + 0.25) × (H + 0.25).
- Hardcover: spine = N × 0.002347 + 4.8/25.4; panel = (W + 5/25.4) × (H + 6/25.4);
  sheet = (2 × panel width + spine + 30/25.4) × (panel height + 30/25.4).
  Hinges occupy the inner 10 mm of each panel, not an additional strip outside it.

The hardcover model is inferred from a [recorded KDP calculator template](https://github.com/hackerbay/twenty-minute-table/blob/main/book/cover.py):
224 premium-color pages at 8.25×11 give approximately 18.790×12.417 inches,
with a 0.715-inch spine. This is not an Amazon-published formula. Amazon's
[hardcover help](https://kdp.amazon.com/en_US/help/topic/GDTKFJPNQCBTMRV6)
requires wrap and hinges, but inconsistently labels its wrap “0.51 inch (15 mm)”.
The model uses 15 mm, matching the recorded calculator dimensions. Compare against
[Amazon's exact template](https://kdp.amazon.com/cover-calculator) before upload.
To use exact measurements instead, save a JSON file with these fields, in inches:

```json
{"pages":224,"trim_width":8.25,"trim_height":11,"paper":"premium-color",
 "spine":0.715,"wrap":0.591,"hinge":0.394,"panel_width":8.447,"panel_height":11.236}
```

Pass `KDP_HARDCOVER_TEMPLATE=/absolute/path/template.json`. The pipeline rejects a
page count, trim, or stock mismatch and records the template hash. Update these
values from the calculator for the actual subset; the example is not a Genesis template.

Hardcover color uses premium white stock even if paperback uses standard color.
KDP hardcover requires 76–550 even pages. Out-of-range selections still get covers
for review, with an explicit console warning and `kdp_eligible: false` in provenance.
The larger hardcover trim is intended to bring Genesis within this limit; verify
the actual page count after building. The supplied 1024×1536 illustrations have limited native print
resolution (roughly 140 dpi at this trim); outlining preserves artwork and makes
text vector paths, but cannot add image detail. Higher-resolution original artwork
is needed to meet Amazon's 300 dpi image recommendation.

The text-free front asset is `pub/covers/fancy/assets/front-textless.png`, edited
with the built-in image generation tool from `cover-front.png` and `cover-back.png`.
Its prompt is preserved in `pub/covers/fancy/assets/front-textless-prompt.txt`.
Publication builds use the saved PNG and deterministic TeX only; no AI calls occur.

## Ebook

### Dependencies

Building the ebook requires:
- python
- pandoc 3,
- the repository;s fonts and images, and
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

