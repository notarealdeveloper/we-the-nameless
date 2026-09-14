# Publishing: next iteration

The implemented workflow is documented in [doc/publishing.md](doc/publishing.md).
These are opportunities to remove overlapping mechanisms and hidden state, in
rough priority order. None requires weakening the validation thresholds.

1. **Retire the second PDF pipeline.** `make kdp`, `bin/kdp-pdf`, and
   `bin/kdp-preflight` still provide the older searchable PDF 1.3 normalization
   route. Its transparency/font policy and 650 MiB limit differ from the new
   outlined workflow's policy and 650,000,000-byte limit. Preserve existing callers
   for now, then make preflight a profile of the shared `kdp_pdf_lib.py` inspector
   and retire the redundant transformation after migration. Help should eventually
   have one meaning for “KDP.”

2. **Remove publishing-time editorial surgery.** `bin/kdp-source` rearranges
   Genesis 22 and its apocryphon. The consolidated pipeline no longer calls it:
   publishing should consume the subset generator's selection. If that editorial
   decision is still wanted, encode it once in the manuscript or subset system;
   then delete this now-unreferenced helper after checking external users.

3. **Unify configuration data, not build orchestration.** Make's `LATEX_CONFIG`,
   `bin/parallel-build`'s `CONFIG_ENV`, and the explicit KDP print profile describe
   much of the same configuration vocabulary. A small declarative schema could
   supply names/defaults/allowed values to each. Keep the KDP profile explicit;
   inheriting whichever screen theme happens to be active is hidden state. Avoid
   inventing a general build framework to share a dozen option definitions.

4. **Use the existing subset authority for EPUB selection too.** `EBOOK_BOOKS`
   remains a hand-maintained list separate from `bin/book-subset`'s book/chapter
   registry. The publishing targets now use that registry, including case-sensitive
   source subsets and numbered aliases. Let EPUB expose its actual supported
   subset capability through the same interface instead of copying another table.

5. **Make cover templates mostly data.** The simple and fancy TeX projects repeat
   trim/spine geometry and lettering; their tiny Makefiles default to Genesis output
   paths. A shared wrapper plus style-specific panel content would centralize these
   rules and make additional trims practical. The new pipeline rejects unsupported
   trims instead of emitting a wrong wrap. Cover source/artwork were entirely
   excluded by `pub/` in `.gitignore`; narrow exceptions now expose these necessary
   inputs, while publication outputs remain ignored.

6. **Replace upsampling with better originals.** The shared asset cache removes
   repeated conversions and selects derivatives from generated subset content.
   Several inherited Genesis derivatives still upscale images to clear effective
   PPI checks. That is a workaround, not restored detail. Obtain higher-resolution
   sources or choose smaller source-level placements. Longer term, declare asset
   print variants next to the existing `\image` vocabulary so the asset script
   need not maintain reference patterns for raw `\includegraphics` placements.

7. **Use recorded dependencies to narrow freshness checks.** The new conservative
   snapshot catches ignored Lua files, cover inputs, other books and validator
   changes that the old Genesis-only digest missed. It can also invalidate a
   release for an unrelated source edit. TeX's `.fls` recorder already provides a
   dependency graph. Combine it with a small explicit set of subset-generator,
   asset and validator inputs to avoid hashing unrelated books without overlooking
   newly added includes. Do not replace this with modification-time checks.

8. **Retire visual-cache reclassification, then consider a sound cache.**
   `kdp-visual-compare --reclassify` and `--check-cache` remain legacy entry points;
   publishing never uses them. They do not attest renderer/library versions or a
   complete set of engine/page results. A future cache should reuse only a complete
   successful report keyed by both PDF hashes, all renderer/library versions, and
   validator/settings hashes. Reclassification cannot recreate discarded pixels.
   Remove these unused entry points after checking external callers.
   Also remove or clearly label `MAX_TILE_FRACTION`: it is recorded in report
   settings but is not an acceptance criterion in the inherited validator.

9. **Separate cleanup from deletion of publishing evidence.** Global `clean` scans
   every build directory, deleting stage logs as well as TeX auxiliaries;
   `clean-stray-aux` scans the source tree. KDP's isolated runs avoid needing the
   latter. Scope ordinary cleanup to its build, and add explicit run retention or
   garbage collection that preserves current artifacts and their reference runs.
   Do not add automatic deletion until archival expectations are clear.

10. **Extend existing tests before adding more machinery.** Synthetic fixtures now
    exercise outlining, both renderers, damaged text/geometry/PDFs, fail-closed tool
    errors, name/completion resolution, freshness and pair promotion. Next useful
    fixtures are unusual font types, inherited/nested resources, masked images,
    and overprint-heavy pages. An explicitly authorized modest real subset build,
    followed by full Genesis, is still needed to establish TeX and print-layout
    acceptance. No book was built during this implementation.

11. **Reconsider diagnostic encodings after real acceptance evidence.** Soft,
    medium and hard remain compatible aliases of one implementation, with separate
    directories. If KDP consistently accepts the default outlined encoding, retire
    the other two rather than maintaining permanent alternative “fix” pipelines.
    Hard's PDF 1.4 flattening may correctly fail the no-new-raster check.
