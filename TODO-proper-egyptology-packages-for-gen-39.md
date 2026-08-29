#!/usr/bin/env bash

lord --verbose << "EOF"

Modify `master.tex` and `01-genesis/39.tex` so the Egyptian in Genesis 39:7–9 is typeset with genuine Egyptian hieroglyphic quadrat/layout behavior rather than flat Unicode strings or manual `\raisebox`/`\kern` hacks.

The goal is twofold:

1. Add proper reusable Egyptian hieroglyph support to `master.tex`.
2. Rewrite the Egyptian passages in `01-genesis/39.tex` so their signs are arranged in realistic Egyptian groupings: stacked, nested, tucked into available spaces, and grouped into quadrats in a way an Egyptologist would consider typographically plausible.

Inspect the existing project before changing anything. Integrate with the current LuaLaTeX/LuaHBTeX, `fontspec`, Hebrew, bidi, and commentary setup rather than replacing unrelated configuration.

## `master.tex`

Keep LuaLaTeX/LuaHBTeX as the engine.

Use `fontspec` and define a dedicated Egyptian font family. Prefer `NewGardiner` if available, with HarfBuzz shaping:

```latex
\newfontfamily\egyptfont[
	Renderer=HarfBuzz
]{NewGardiner}
```

If `Script=Egyptian Hieroglyphs` works with the installed `fontspec`/HarfBuzz stack, it may be added, but compilation should not depend on that option if it is unsupported.

Define or update `\egypt{...}` so Egyptian is explicitly isolated from surrounding Hebrew bidi state and rendered left-to-right.

The installed Egyptian font displays people, birds, animals, etc. facing left, so the intended reading direction here is LTR: the reader reads into the faces.

Use the safest LuaTeX-compatible mechanism already appropriate for this project, e.g. conceptually:

```latex
\newcommand{\egypt}[1]{%
	{\egyptfont\textdir TLT #1}%
}
```

but inspect the existing bidi/polyglossia setup and choose the implementation that actually compiles cleanly.

Do not disturb Hebrew directionality elsewhere.

## Use genuine Egyptian Hieroglyph Format Controls

Support the actual Unicode Egyptian Hieroglyph Format Controls:

```text
U+13430 EGYPTIAN HIEROGLYPH VERTICAL JOINER
U+13431 EGYPTIAN HIEROGLYPH HORIZONTAL JOINER
U+13432 EGYPTIAN HIEROGLYPH INSERT AT TOP START
U+13433 EGYPTIAN HIEROGLYPH INSERT AT BOTTOM START
U+13434 EGYPTIAN HIEROGLYPH INSERT AT TOP END
U+13435 EGYPTIAN HIEROGLYPH INSERT AT BOTTOM END
U+13436 EGYPTIAN HIEROGLYPH OVERLAY MIDDLE
U+13437 EGYPTIAN HIEROGLYPH BEGIN SEGMENT
U+13438 EGYPTIAN HIEROGLYPH END SEGMENT
```

Expose readable commands in `master.tex`, e.g.:

```latex
\egV
\egH
\egTS
\egBS
\egTE
\egBE
\egO
\egBegin
\egEnd
```

Use a LuaLaTeX-safe way to emit these supplementary-plane Unicode characters.

Do not blindly use `^^^^13430` etc. unless you verify that this syntax actually emits the desired Unicode code point under this engine.

Literal Unicode control characters, `\char"13430`, or Lua-generated characters are acceptable if they are safer.

The intended authoring syntax should allow things like:

```latex
\egypt{𓈖\egV𓎡}
```

for vertical joining,

```latex
\egypt{𓈖\egH𓎡}
```

for horizontal joining,

and recursive grouped structures such as:

```latex
\egypt{\egBegin𓈖\egH𓎡\egEnd\egV𓇋}
```

as well as the four insertion controls for placing small signs into cavities of larger signs.

## Do not use fake quadrat macros

Do not add or use manual geometry macros such as:

```latex
\egstack
\egtop
\egbottom
\egtuck
\egsmall
```

or implementations based on:

```latex
\raisebox
\scalebox
\makebox
\kern
```

for the internal composition of hieroglyphic groups.

If such macros already exist, search the repository before removing them. Do not break other chapters.

The goal here is genuine Unicode/OpenType Egyptian layout, not visual approximation.

## Check font support

Check whether `NewGardiner` is installed and discoverable.

Useful commands include:

```bash
fc-list | rg -i 'NewGardiner|Gardiner'
```

and a minimal LuaLaTeX test.

Do not silently replace it with an unrelated Egyptian font merely because it is missing.

If it is unavailable, report that clearly.

If NewGardiner is present but ordinary HarfBuzz shaping does not correctly render recursive quadrat expressions, investigate the `NewGardiner` + `opentypehiero` workflow rather than falling back to manual TeX positioning.

The likely serious pipeline is:

```text
Unicode Egyptian text
+ Egyptian Hieroglyph Format Controls
→ opentypehiero
→ generated NewGardiner-based OpenType font
→ LuaHBTeX / HarfBuzz
→ PDF
```

If a generated project-specific font is required, integrate that only if it can be done cleanly and reproducibly. Otherwise prepare `master.tex` for it and document exactly what remains.

## Now fix `01-genesis/39.tex`

The Egyptian in verses 7, 8, and 9 currently exists as flat strings.

Find these passages and replace only the Egyptian strings/layout with properly grouped hieroglyphic Unicode sequences.

Do not rewrite the Hebrew, English translation, commentary, or footnotes except where necessary to accommodate the Egyptian layout.

The current Egyptian material is:

### Verse 7

```latex
\aB{\egypt{𓈖𓎡 𓈖𓇋 𓂺}}%
```

Its intended rough transliteration is:

```text
nk n=i
```

with `𓂺` functioning as the explicit sexual determinative/sign at the end.

Lay this out as genuine Egyptian rather than simply:

```text
𓈖𓎡 𓈖𓇋 𓂺
```

Use appropriate vertical/horizontal grouping so the short/wide signs form compact quadrats.

A likely conceptual starting point is something of the form:

```text
𓈖
𓎡
```

for `nk`, and similarly compact grouping for `n=i`, but do not mechanically stack signs merely because they are adjacent.

Use Egyptological judgment.

### Verse 8

Current material:

```latex
\aB{\egypt{𓅓𓎡!}}

\aB{\egypt{𓈖 𓂋𓐍 𓈖𓃀𓇋}}

\aB{\egypt{𓐍𓏏 𓈖𓃀𓏏 𓅓 𓉐𓏤!}}

\aB{\egypt{𓂧𓇋 𓐍𓏏 𓈖𓃀𓏏 𓅓 𓂝𓇋! 𓂺}}
```

Preserve the wording/sign inventory unless there is an obvious encoding/layout mistake.

Recompose the signs into realistic quadrats.

Specifically:

* avoid Western-style equal-width linear spacing;
* stack short/wide signs where Egyptian orthography would naturally do so;
* use horizontal joins for signs that belong beside each other within one quadrat;
* use vertical joins for signs arranged one above another;
* use BEGIN/END SEGMENT where a grouped subexpression is itself joined to another sign;
* use insertion controls where a small sign naturally occupies a cavity in a larger sign;
* keep determinatives and larger signs visually distinct where appropriate;
* preserve word grouping but do not create huge Latin-style word spaces.

Do not insert exclamation marks inside a hieroglyphic group in a way that disrupts shaping. If punctuation needs separation, put it outside the shaped Egyptian cluster.

### Verse 9

Current material:

```latex
\aB{\egypt{𓈖𓏏𓏭 𓂋𓅱𓏏𓊖 𓂝𓂝 𓂋𓇋!}}

\aB{\egypt{𓈖 𓐍𓂋𓎡𓆑 𓐍𓏏 𓈖𓃀𓏏 𓈖 𓂋𓇋 𓇋𓈖𓎡!}}

\aB{\egypt{𓂝𓂝 𓅓𓂝𓏏 𓏏𓈖! 𓂺}}%
```

Again, retain the intended wording/sign inventory unless there is a clear error, but recombine the signs into realistic Egyptian quadrats.

Pay particular attention to groups like:

```text
𓈖𓏏𓏭
𓂋𓅱𓏏𓊖
𓂝𓂝
𓐍𓂋𓎡𓆑
𓈖𓃀𓏏
𓇋𓈖𓎡
𓅓𓂝𓏏
𓏏𓈖
```

Decide how each should actually occupy quadrat space instead of applying one generic stacking rule.

Treat this as Egyptian writing, not as a sequence of Unicode icons.

## Important Egyptological requirement

Before rewriting the three passages, reason about each Egyptian word/group individually.

Use the sign shapes and conventional hieroglyphic layout principles:

* tall signs tend to occupy vertical space;
* low/wide signs frequently take upper or lower subdivisions;
* two small signs may share a row;
* small phonetic complements may fit into remaining quadrat space;
* grammatical signs should not be arbitrarily separated from the word they belong to;
* determinatives generally follow the phonetic spelling and may occupy their own visual space;
* groups should seek roughly rectangular/quadrat proportions rather than a rigid baseline;
* do not stack signs solely to save horizontal space;
* recursive grouping is preferred over manual scaling.

If a particular group cannot be confidently positioned from the current spelling, choose the most plausible conventional arrangement and document the uncertainty in your final report. Do not add explanatory comments to the published Genesis text unless needed for the TeX implementation.

## Preserve LTR orientation

The hieroglyph font currently has living signs facing left.

Therefore the Egyptian passages should remain LTR.

Do not reverse the sign order merely to imitate right-to-left monumental Egyptian.

Do not mirror the font.

The goal is:

```text
LTR encoded text
+
left-facing glyphs
=
read from left toward the faces
```

## Test it

Compile the actual project after the changes.

Use the project's existing build command if one exists.

Verify at least:

* Genesis 39 compiles;
* Hebrew is still correct;
* Egyptian runs LTR;
* ordinary Egyptian signs render;
* U+13430–U+13438 do not appear as tofu or visible control boxes;
* vertical and horizontal grouping actually occurs;
* recursive grouping works;
* insertions work if used;
* punctuation does not break shaping;
* the Genesis 39 Egyptian is visibly compact and quadrat-like rather than a flat run of signs.

If possible, render the page containing Genesis 39 and inspect the PDF visually.

If the project outputs a PDF, inspect the relevant page rather than relying only on a successful compiler exit status.

## If format-control shaping fails

Do not declare success merely because the document compiles.

If the controls are ignored and the signs still display in a flat line, explicitly treat that as failure.

Investigate whether `opentypehiero` should generate a project-specific font from the actual hieroglyphic sequences used in `01-genesis/39.tex`.

If needed, set up or document a reproducible workflow such as:

```text
01-genesis/39.tex
        ↓
extract hieroglyphic expressions
        ↓
opentypehiero
        ↓
generated GenesisEgyptian.otf
        ↓
master.tex loads GenesisEgyptian.otf
        ↓
LuaLaTeX
```

Do not replace the hieroglyphs with SVG, PNG, TikZ drawings, or manually positioned glyph boxes unless there is absolutely no viable Unicode/OpenType route and you explicitly report that limitation.

## Scope

Modify:

```text
master.tex
01-genesis/39.tex
```

and only additional build/font-support files that are genuinely necessary.

Do not make unrelated stylistic edits.

Do not alter the prose merely because you notice wording you would prefer.

## Final report

When finished, show:

* the exact diff for `master.tex`;
* the exact diff for `01-genesis/39.tex`;
* any additional files added or changed;
* which Egyptian font is actually being used;
* whether `NewGardiner` was found;
* whether genuine Unicode format-control shaping worked;
* whether `opentypehiero` was necessary;
* the build command used;
* whether the final PDF was visually inspected;
* any Egyptian groups whose positioning remains uncertain.

Most importantly: do not optimize merely for “compiles.” Optimize for actual hieroglyphic composition that looks plausibly like professionally typeset Egyptian.

EOF
