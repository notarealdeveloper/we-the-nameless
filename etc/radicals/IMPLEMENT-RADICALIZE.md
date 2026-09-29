# Integrate the 100 microbooks as switchable section headings

Implement this in the actual book repository, not merely as a plan or a standalone demonstration. This prompt and its supporting files are in `radicals/`, relative to the repository root. The live `master.tex` is at the repository root.

The editorial work is complete. Add the approved microbook headings to the actual text, controlled by one new configuration option:

- `radicalize = radicalized`: the radicalized headings are present.
- `radicalize = in radicalized`: they compile away completely.

**`in radicalized` is the literal disabled value, including the internal space. Do not silently replace it with `unradicalized`.**

## 1. Read the sources and preserve the approved edition

Read the applicable repository instructions, then inspect the current `master.tex`, build/configuration machinery, and actual chapter includes. Read the revised support files under `radicals/`:

- `Radicalized.json` and `Radicalized.md`.
- `Radicalized.tex`, `radicalized-placement.json`, and `INTEGRATION.md`.
- `Book-emblems.json`, `migration.json`, and `validate_radicalized.py`, where supplied.

Other radical notes and the older integration prompt are background. **This prompt supersedes their deployment paths and unconditional-display behavior.** The current JSON is authoritative for IDs, numbers, characters, titles, and semantic boundaries.

There may be older, similarly named files. Use the revised inventory whose metadata identifies **100 core sections and 70 distinct section characters**, not the original 104-section inventory. If the revised bundle is still zipped, inspect/extract it inside `radicals/` without overwriting existing edits. If it is already nested under `radicals/radicalized-100/`, use that actual path consistently; do not create competing canonical copies. All paths below assume the flat arrangement and should be adjusted to the resolved support directory.

Preserve these invariants:

| Conventional book | Separate emblem | Microbooks | Global numbers |
|---|:---:|---:|---|
| Genesis | 元 | 16 | 001–016 |
| Exodus | 出 | 10 | 017–026 |
| Leviticus | 示 | 10 | 027–036 |
| Numbers | 屯 | 12 | 037–048 |
| Deuteronomy | 申 | 10 | 049–058 |
| Joshua | 土 | 5 | 059–063 |
| Judges | 士 | 9 | 064–072 |
| Samuel | 王 | 12 | 073–084 |
| Kings | 主 | 16 | 085–100 |

Count only `books[].sections[]`. The nine conventional-book emblems are a separate layer; do not turn them into extra microbooks or include them in the 70-sign vocabulary count. Leave conventional book headings and title pages intact. Do not insert the archived Ezra–Nehemiah–Esther units, apocrypha, or interludes into this system.

Preserve stable IDs even where their numeric suffixes have gaps. The display abbreviation Kng does not rename `kgs` IDs. These retired IDs are aliases, **not additional insertion sites**:

```text
gen-12 → gen-11
exo-08 → exo-07
lev-10 → lev-09
sam-04 → sam-03
```

Do not promote `internal_transitions` into headings. Do not resegment, substitute characters, change titles, chase a different vocabulary count, or renumber sections within subset builds.

## 2. Add the configuration option to master.tex

Follow the live repository's configuration conventions. The public option is named `radicalize`; its TeX setting should be `\ConfigRadicalize`, with an externally overridable default alongside the other top-of-file settings:

```tex
% radicalize — choices: radicalized, in radicalized
\ifdefined\ConfigRadicalize\else
    \def\ConfigRadicalize{in radicalized}%
\fi
```

**Default to disabled**, so ordinary existing builds retain their current appearance until explicitly enabled.

Derive one boolean, such as `\ifConfigRadicalizeOn`, from an exact comparison of the resolved setting. Only `radicalized` enables the feature; `in radicalized` disables it. Reject other values with a clear configuration error rather than silently guessing. Do not use a substring test: both valid values contain `radicalized`. Preserve the internal space through TeX tokenization and any build-script argument handling.

Respect external overrides before computing the boolean. Where the existing build/configuration interface exposes other settings as named options, add `radicalize` through that same interface and pass it through to `\ConfigRadicalize`. Do not invent a parallel configuration system or let a support include reset an already selected value. Document the actual supported invocation syntax after inspecting the build scripts.

The configuration is fixed for a build; runtime switching inside the document is unnecessary.

## 3. Reuse the existing marker API, with a genuinely empty disabled branch

Keep the supplied public body marker:

```tex
\RadicalMicrobook{gen-01}
```

The ID resolves the character, English title, reference, and global number from the central declarations. Do not repeat those fields manually at 100 source locations. Reuse and adapt `Radicalized.tex`; do not create a second competing heading system.

Load the support using `\input`, not `\include`, from its actual location under `radicals/`, after the relevant configuration, font commands, and hyperlink support are available. Keep public commands defined in both modes so the same chapter source compiles in either mode.

### Enabled behavior

Render an in-flow section heading with exactly one prominent microbook character, the supplied English title, and restrained number/reference metadata, using the existing support presentation as the starting point. These are section divisions, not 100 new title pages.

Use the existing `\chinese`/Chinese font selection and theme-aware typography. Centralize heading styling in one renderer so it can be adjusted once. Keep fonts, direction, size, and color changes local. Do not add decorative graphics, pinyin, lexical essays, or new font assets. Preserve the exact Unicode characters, including standalone radicals; do not replace them with look-alikes or normalized variants.

Provide modest spacing and keep the heading with the beginning of its following text. Do not force every microbook onto a new page. Place the hyperlink destination after any required page-break decision, so it lands on the heading rather than the preceding page.

Retain the supplied `microbook.<stable-id>` destination scheme. Preserve traditional book/chapter/verse destinations, numbering, footnote counters, and running heads. Do not call `\Chapter` or a counter-changing section command merely to obtain a heading's appearance.

### Disabled behavior — strict requirement

A disabled `\RadicalMicrobook{...}` must consume its argument and have **no effect on the typeset document**. In particular, it must not introduce:

- Text, a space, a paragraph break, a box, glue, a penalty, or a page-break decision.
- `\par`, `\vspace`, `\addvspace`, `\Needspace`, or indentation changes.
- Hyperlink targets, phantom sections, labels, bookmarks, or contents entries.
- Counter changes, marks, auxiliary-file writes, or updates to the seen-ID state.
- Font/color/direction changes, argument expansion, or deferred rendering work.

The supplied marker currently starts with an unconditional `\par` and also creates labels and seen-ID state. **Move all of that behavior behind the gate; hiding just the printed character is not sufficient.** An empty one-argument definition in the disabled mode is acceptable.

Harmless preamble declarations may still exist. No new font or rendering dependency should be exercised solely for disabled headings. Any additional body-level helper must obey the same no-op contract.

Source whitespace matters too: inserting an empty macro between words must not add or remove spaces, and adding blank lines around an otherwise empty marker must not change paragraphing. Do not “fix” this using unconditional `\unskip` or `\ignorespaces`, which can alter existing text.

## 4. Insert all 100 markers at verified text boundaries

Inspect the actual included files and their inclusion order. The support manifest contains **common English/KJV-style references, not verified Hebrew manuscript anchors**. Resolve each boundary against the live text, not merely a similarly numbered filename or an assumed `\CurrentBook` name.

Update the placement manifest, or add a clearly identified resolved companion, recording for each current ID: intended reference, actual source file, actual book/chapter/verse or clause location, placement relative to the text, and verification status. Preserve the original reference fields. Account explicitly for differences in versification and for the repository's combined Samuel/Kings organization.

Insert one current marker at each microbook's actual start, outside the bilingual verse body wherever the boundary is between verses. At chapter-start boundaries, use the correct local position after the existing chapter heading/setup and before the first included verse. Do not put every marker at the beginning of a chapter, wrap whole chapters in a conditional, or move passages between files to make insertion easier.

Preserve the biblical text, translation, commentary, source labels, color/font assignments, figures, and existing references. Most changes should be single marker calls plus centralized support/configuration code. If chapter files are generated, update the responsible source or generator so regeneration preserves the markers. Any insertion tooling must be idempotent.

### The boundary inside 1 Samuel 4:1

Handle `sam-02` explicitly: `sam-01` ends after the sentence saying that Samuel's word reached Israel; `sam-02` begins with Israel going out to battle. Do not approximate this by putting the heading before the whole verse or before verse 2.

The existing verse machinery may render Hebrew and English together and may substitute an external English translation. Inspect that machinery and the actual text before changing it. A heading inserted blindly into just one language argument, a table cell, or a commentary argument is not an implementation of this boundary.

Use the smallest suitable structural helper if a paired intra-verse split is necessary. Preserve the original canonical verse reference and its commentary exactly once, align the boundary in both languages, and retain all original text and styling. When disabled, this helper must use the unchanged original verse-rendering behavior, without residual fragment spacing, extra rules, repeated verse labels, or new pagination. Avoid maintaining two independently editable copies of the verse. Handle external translations deliberately rather than splitting substituted text at an assumed character offset.

### Other boundaries and duplicates

Keep cross-volume microbooks continuous. `sam-07` extends through 2 Samuel 1; `kgs-07` extends through 2 Kings 1. Neither volume boundary creates an extra microbook. Preserve the final `kgs-16` / 100 / 存 at 2 Kings 25:27, not earlier in the destruction narrative.

Do not insert headings again at the four retired merge boundaries. Do not duplicate markers across the Hebrew and English streams or add one for every textual witness. The existing support suppresses repeated destinations but still renders repeated headings; that warning alone is not an adequate duplicate check. Handle genuine repeated witnesses explicitly while preserving their text, and audit the canonical reading sequence separately.

A full unfiltered Genesis–Kings build must have exactly 100 canonical microbook starts. A subset build contains only the relevant starts, retaining their original IDs and global numbers. Do not fabricate another start merely because an excerpt begins in the middle of a microbook.

If a mapping genuinely cannot be established from available sources, complete the other verified placements and report the exact unresolved passage. Never silently relocate a boundary or mark an unresolved placement verified.

## 5. Keep navigation and support files coherent

Keep `\RadicalContents`, `\RadicalBookContents{BOOK}`, and the separate `\RadicalBookEmblem{BOOK}` interface available. Gate radicalized contents output and any newly added emblem/heading presentation with the same configuration; disabled calls must not leave surrounding heading text or spacing.

Preserve the ordinary contents and traditional navigation. If there is already an appropriate radicalized-contents insertion point, wire the supplied helpers into it. Otherwise document their optional insertion; a wholesale contents redesign or an additional front-matter catalogue is not required for this heading-integration task.

Any microbook contents links or bookmarks must address actual emitted destinations, avoid duplicate entries, and respect the selected book/subset. Old auxiliary data must not produce ghost entries or links to omitted sections when switching modes or subsets. Run sufficient passes for links to settle.

Keep the canonical data separate from presentation logic. If the TeX support is regenerated, ensure regeneration preserves the configuration-aware implementation—either by updating its generator/template or separating generated declarations from maintained rendering code. Retain the validator's substantive checks; do not weaken them to conceal a mismatch.

Use repository-relative paths. Do not leave sandbox paths, test-harness font fallbacks, or assumptions that the support lives next to `master.tex` in production code.

## 6. Validate the integration, not just the dataset

Before editing, record the current working-tree state and obtain a reproducible baseline with the existing build tools and available assets. Preserve unrelated work. Use isolated build outputs where appropriate; do not reset the user's tree to obtain a baseline.

Run the supplied dataset validator and add repeatable integration checks covering:

**Inventory and placement.** Exactly 100 current IDs in canonical order, 70 distinct microbook characters, the per-book counts above, and every start matched to its intended verse/clause. Exclude declarations, aliases, documentation, contents rows, coda, and intentional alternate witnesses from the canonical body count. Check for gaps, overlaps, duplicated text, and dropped verses/clauses. Counting raw CJK occurrences or grepping all TeX files for a macro name is not sufficient.

**Configuration.** Verify the default, explicit `radicalized`, explicit `in radicalized`, an externally supplied override, and rejection of an invalid value. Test the disabled marker between sentinel text as well as between paragraphs. Its argument must not execute side effects. Test any split-verse helper separately.

**Builds.** Compile the full canonical text enabled and disabled using the actual book build, plus representative subset builds. Exercise both verse-layout modes and representative light/dark, commentary, and external-translation settings. Preserve the existing KDP/export path; do not change geometry, font mappings, or postprocessing to make a heading test pass.

**Regression.** The disabled output must match the pre-change baseline in text, page count, and rendered layout under identical settings. Inspect page images and/or text coordinates; raw PDF byte identity is not required because metadata may differ. Test enabled → disabled → enabled using the ordinary build path as well, to expose stale auxiliary data. Confirm that no disabled microbook output, targets, or contents entries remain.

**Enabled output.** Inspect real pages, not only a synthetic all-markers specimen: chapter-start and mid-chapter headings, the intra-verse Samuel boundary, repeated signs, a heading near a page break, and the final 存. Check all selected glyphs for missing-character warnings, clipped text, bad direction, or font substitution. Confirm that each heading appears once at the right boundary and that its destination lands correctly.

If dependencies or unavailable source material block a check, report the exact limitation and distinguish verified work from unrun tests. The supplied smoke-test report is not evidence that the integrated manuscript passes.

## 7. Finish the repository change

Leave a focused implementation: the `master.tex` setting, configuration-aware support, actual source markers, resolved placement data, tests, and brief usage documentation. Do not rewrite unrelated text or refactor the book wholesale.

Update the integration TODO only to the extent verified by actual source inspection and builds. Conclude with the files changed, the exact setting/build commands for both modes, the confirmed counts, test results, and any unresolved mappings or blocked tests.

The result should be one manuscript with one switch: **`radicalized` adds the approved reading divisions; `in radicalized` leaves the book as though those additions were absent.**
