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

`make distclean` deletes **all of build/**, including print releases and evidence.
Archive the entire `build/kdp/<canonical>/` directory before removing it; its
release pointers depend on retained runs. Print manifests also record the Git
commit timestamp; when checking an archived release after a commit, preserve its
recorded timestamp with `SOURCE_DATE_EPOCH` as described in
[doc/publishing.md](doc/publishing.md).

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

Run these first two commands **in order**, with unchanged sources and options:

```sh
make genesis-kdp-build           # 1. Build searchable reference interior and a cover sized from its page count.
make genesis-kdp-vectorize       # 2. Convert fonts to paths, clean, check both PDFs, then release the pair.
make genesis-kdp-check           # Optional later: recheck the released pair; no TeX build, but a full visual rerun.
```

`-kdp` already runs stages 1 and 2; you do not need both routes. The long step is
`-kdp-vectorize`: every page of both PDFs is rendered at 300 DPI by **both MuPDF
and Poppler** and compared with its reference. The two-pixel Gaussian blur
allows font/path edge differences; it is not permission to move pages by two
pixels. Tile error, lost ink, page differences, geometry, zero remaining fonts,
and other structural checks still must pass. Do not skip it for upload files.

Failures print the log/report paths. Fix TeX/assets and repeat `-kdp-build`;
repeat `-kdp-vectorize` alone only if the reference, sources, tools, and settings
are unchanged. A failed run preserves the previous release, so **do not upload
an old artifact merely because the path exists**. Wait for the new command's PASS.
Reports are under `build/kdp/<canonical>/current/reports/`; read the structural
reports' human-review items and visual `index.html` files.

Defaults: **7×10-inch paperback, premium color on white paper, no interior bleed,
simple cover, LD spine**. Use those settings in the publisher's setup. Alternatives:

```sh
make genesis-kdp KDP_COVER_STYLE=fancy    # Use the illustrated wrap.
make genesis-kdp KDP_SPINE=nameless       # Use the title instead of LD on the spine.
make genesis-kdp KDP_PAPER=standard-color KDP_INK=standard-color  # Use standard color white stock.
```

Repeat the same options on every separate build/vectorize/check command. The
pipeline currently enforces even page counts of 24–828 (premium) or 72–600
(standard). Short chapter selections may fail these limits; large selections
may need smaller editions. Other trims, black ink, cream paper, interior bleed,
and hardcover need additional layout support. Other printers may accept these
PDFs, but verify their trim, stock, spine, bleed, and file requirements first.

After upload, inspect KDP Print Previewer, order a proof while the listing is
still a draft, and inspect the physical copy before publishing. Check gutters,
small scripts, images, color, spine, and barcode placement. Passing comparisons
means faithful conversion; it does not replace editorial or physical review.

### Build the paperback with one command

```sh
make genesis-kdp
# 1. Build interior + cover
# 2. Outline all fonts
# 3. Validate
# 4. Then release both PDFs.
```

When that command finishes successfully, upload these **two separate files**:

```sh
build/kdp/01-genesis/artifacts/01-genesis-interior.pdf
build/kdp/01-genesis/artifacts/01-genesis-cover.pdf
```

For another selection, use the same command pattern:

```sh
make exodus-kdp
# Upload build/kdp/02-exodus/artifacts/02-exodus-{interior,cover}.pdf.

make J-kdp
# Upload build/kdp/J/artifacts/J-{interior,cover}.pdf.

make P-kdp
# Upload build/kdp/P/artifacts/P-{interior,cover}.pdf.

bin/book-subset --output-name genesis
# Print the canonical filename stem: 01-genesis.
```

The braces above abbreviate two filenames. Upload the interior as the manuscript
and the cover as the paperback wrap. Do not combine them.

Old PDFs in `pub/`, root PDFs, and the searchable references are **not** this pipeline'supload files.

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

