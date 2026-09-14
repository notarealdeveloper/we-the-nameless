# KDP publishing subsystem prompt

Implement an organized, reproducible KDP publishing subsystem for every book or
subset accepted by the existing `make $book` targets (`genesis`, `exodus`, `J`,
`P`, and so on). Much of the machinery already exists. Inspect and consolidate
the current Make targets and `bin/kdp-*` scripts instead of creating a competing
pipeline. In particular, preserve the successful all-font outlining and the
MuPDF/Poppler visual validation currently implemented by `bin/genesis-kdp`.

Do not publish or upload anything. Do not combine the cover and interior: KDP
requires separate PDFs. Do not alter ordinary `make $book` behavior. Keep every
KDP build isolated in its own build directory so concurrent or interrupted runs
cannot mix auxiliary files or silently reuse another book's output.

Design the public interface around these predictable targets:

```text
make genesis-kdp-build            # searchable KDP-aware interior + raw cover
make genesis-kdp-vectorize        # outline/clean/validate both PDFs
make genesis-kdp                  # convenient composition of both stages
make genesis-kdp-check            # revalidate recorded final artifacts
```

Equivalent aliases must work for every value supported by the dynamic
`make $book` subset system. Resolve canonical output names through
`bin/book-subset --output-name`; do not duplicate the book-name table. It is
Document them in `make help` and keep existing working aliases compatible.

Separate the implementation into two explicit stages:

1. Build the KDP-aware searchable reference interior using the same subset
   selection as `make $book`, print-safe assets, and the intended print config.
   Build its separate cover from that exact interior so page count and paper
   stock determine the spine correctly. Record the configuration and tool
   versions.
2. Convert every font in both PDFs to equivalent vector paths with Ghostscript
   `pdfwrite -dNoOutputFonts`, perform conservative qpdf cleanup, and validate
   the actual final artifacts. Do not rasterize pages or text, downsample images,
   crop, scale, recolor, or change pagination. Promote candidates atomically only
   after every check passes.

Generalize Genesis-specific paths, source-digest inputs, labels, and cover
metadata. Generalize `bin/kdp-assets` carefully: common assets should be shared,
while book-specific derivatives should be selected declaratively and only made
when that subset needs them. Retain explicit KDP choices for trim, paper, ink,
and bleed; validate unsupported combinations rather than silently substituting
different settings. Preserve the currently successful Genesis defaults of
premium color and no bleed unless the caller explicitly selects another valid
configuration.

The vectorization stage should retain the proven Ghostscript controls from
`bin/genesis-kdp`: `-dNoOutputFonts`, no automatic rotation, unchanged color,
no image downsampling or automatic lossy filtering, preserved JPEG/JPX images
and overprint settings, and removal of annotations. Follow it with qpdf page
extraction/cleanup to discard document navigation and metadata without changing
page content. Reuse `bin/kdp-inspect`, `bin/kdp-validate`, and
`bin/kdp-visual-compare`, improving them generically where necessary.

Validation must fail closed and cover both the interior and cover. At minimum:

- `qpdf --check` succeeds and the PDF is unencrypted.
- `pdffonts` reports zero fonts and `pdftotext` reports no non-whitespace text.
- MuPDF inspection finds no reachable font resources or text-showing operators.
- Page count, order, boxes, rotation, and `UserUnit` match the searchable
  reference; the cover's sheet geometry matches its reference.
- No unexpected page-sized rasterization or new raster assets appear, file size
  remains within KDP's limit, and unresolved low-resolution images or
  transparency are reported accurately.
- Every page of reference versus outlined output is visually compared at 300
  DPI with MuPDF and, independently, Poppler. Run the visual validator self-test
  first, preserve localized failure crops/reports, and do not weaken tolerances
  merely to make a build pass.

Add clear, line-buffered progress messages before and after every meaningful
operation. Use consistent labels containing the book, artifact, stage number,
and operation, for example:

```text
[KDP genesis 1/6 assets] START preparing print assets
[KDP genesis 1/6 assets] PASS  build/kdp/genesis/assets
[KDP genesis 2/6 interior] FAIL LuaLaTeX pass 2; log: .../lualatex.log
```

Capture complete command output in per-stage log files while still showing a
short useful status on the terminal. Error traps must report the failing stage,
exit status, command or operation, candidate path, and exact log/report path.
Never print a success message for stale artifacts. Write a manifest containing
source/config hashes, exact commands or options, tool versions, input/output
SHA-256 hashes, artifact sizes, page counts, font counts, and all report paths.
Make `$book-kdp-check` reject stale artifacts when relevant sources, config, or
validator tooling changed, while allowing an explicitly named artifact to be
checked without rebuilding.

Use a layout such as:

```text
build/kdp/<canonical-book>/
  reference/interior.pdf
  reference/cover.pdf
  work/<stage>/...
  logs/...
  reports/interior/...
  reports/cover/...
  artifacts/<canonical-book>-interior.pdf
  artifacts/<canonical-book>-cover.pdf
  manifest.json
```

Choose one unambiguous final naming convention and document the two upload
files prominently. If compatibility copies such as `01-genesis-kdp.pdf` and
`01-genesis-cover.pdf` remain at repository root, create them only after full
validation and identify them in the manifest.

Add inexpensive automated tests for target/name resolution, stage failure
reporting, stale-manifest detection, and the validator's damaged fixtures. Then
exercise the subsystem on a small representative subset before the expensive
Genesis full-book run. Do not build any book while merely planning or reviewing
this work; actual builds require an explicit user request. Finish by documenting
the commands, outputs, configuration selections, logs/reports, recovery after a
failed stage, and the continuing need for KDP Print Previewer review and a
physical proof.
