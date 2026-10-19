# Print pipeline internals

The user interface, defaults, parameter mapping, output paths, publisher geometry,
and equivalent CLI calls are documented in [PUBLISH.md](../PUBLISH.md).
The implementation has these boundaries:

- `bin/print_publish_config.py` owns publisher presets, supported trims, and the
  Make target grammar. Make enumerates its suffixes for completion; the CLI parses
  those same suffixes. Resolution finishes before any generation. `--plan` only
  resolves selection/configuration and prints paths; it creates no build directories.
- `bin/book-subset` owns selection and canonical names. Aliases share output paths
  and locks, while case-sensitive source selections remain distinct.
- `bin/kdp-publish` orchestrates both publishers. Each resolved profile records
  artwork, physical construction, trim, and processing separately. It supplies
  explicit print settings to TeX, inspects the actual interior, and builds the
  matching wrap. Construction never selects interior trim. KDP hardcover uses
  premium-color stock; Lulu preserves the selected color stock.
- `master.tex` accepts `ConfigPrintTrimWidth` and `ConfigPrintTrimHeight` together
  in its book geometry. Print builds use book typography with these explicit
  dimensions. The legacy `hard` display mode still works for ordinary builds,
  but publishing no longer relies on it to select trim.
- `bin/kdp_cover_geometry.py` and `bin/lulu_cover_geometry.py` own the distinct
  physical cover models. Neither selects artwork or changes interior typography.
  `bin/kdp-cover` reads page count and dimensions from its input PDF, selects the
  publisher's model, writes dimensions/provenance, then runs two cover TeX passes.
  The shared cover typography renders either plain or illustrated panels. There
  is no alternate-layout branch.
- Font outlining and validation are shared operations, available to both publishers.
  Processing defaults are policy, not restrictions on which operations can run.
  Lulu originals remain originals; no implicit 300-DPI rasterization occurs.

## Files, concurrency, and failure

Public PDFs live at
`pub/<publisher>/<canonical>-<interior|cover>-<style>cover-<trim>-<kind>.pdf`.
Originals, vectors, different trims, cover styles, and publisher models have
separate names. Other custom settings can reuse these names; choose a separate
`--output-dir` to retain variants of paper, construction, spine text, or templates.
The nondefault encoding profiles have their own publisher subdirectory by default.

Every operation locks `build/<publisher>/<canonical>/.lock` before generation or
conversion. Encoding variants share this lock. Two selected presets run under
one parent lock; each has separate run directories, assets, TeX caches, mutable
command records, and disjoint outputs. The parent waits for all workers on failure
before releasing the lock. Concurrent aliases cannot overwrite each other.

Each run records source hashes, configuration, tool versions, commands, inspection
reports, and TeX recorder dependencies. Build rehashes sources at the end and fails
with a source-change report if inputs changed during generation. This prevents
mixed-source builds being reported as successful. It does not impose freshness
requirements on later conversion/check operations: those use the stable PDFs,
without requiring any manifest. Deleting build records does not invalidate them.

Conversion checks that all selected originals exist, outlines fonts with
Ghostscript, then cleans with qpdf. Intermediate `-outlined.pdf` and
`-vectorized-pending.pdf` files stay beside the public originals. A worker publishes
its candidates only after all its selected artifacts pass structural checks,
then removes intermediates. A failed conversion preserves that worker's previous
vectors. The two presets finish independently; replacement of multiple PDFs is
sequential, not an atomic transaction. A failed build may leave partially updated
originals: fix the cause and repeat build before converting.

Logs and reports are under the printed run directory, normally
`build/<publisher>/<canonical>/runs/<run>/`. Failure messages identify the stage,
operation, command, candidate, log, and reports. `make clean` preserves both
publishers' records and public PDFs; `make distclean` preserves public PDFs only.

## Validation boundaries

Build checks even page counts and the selected publisher/construction's supported
range, exact no-bleed interior dimensions, and the cover sheet against the same
geometry model used by rendering. Original inspection records searchable fonts
and PDF features. A matching model is not independent confirmation of a vendor's
cover template: compare with the actual vendor-generated template before upload.

Structural validation checks PDF validity, zero remaining fonts/text operations,
page geometry, new raster placements, and size. Vectorization does not call the
visual validator. Only the explicit `check` stage runs the visual validator's
damaged-image self-test and compares all selected original/vectorized pairs using
MuPDF and Poppler at 300 DPI. Difference crops and HTML/JSON reports stay in that
run's reports directory. Check never rebuilds or alters the PDFs.

An arbitrary pair can be checked with:

```sh
bin/kdp-publish genesis check --provider kdp \
  --reference /path/original.pdf --artifact /path/vectorized.pdf
# Equivalent:
make genesis-kdp-check KDP_REFERENCE=/path/original.pdf KDP_ARTIFACT=/path/vectorized.pdf
```

Synthetic tests use small generated PDFs, mocked book/cover TeX commands, real PDF
inspection/conversion, configuration matrices, and concurrency barriers. They do
not compile the book and cannot establish that current manuscript sources compile
or meet a publisher's editorial/physical requirements.
