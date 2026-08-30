#!/usr/bin/env bash
set -euo pipefail
RUN=${1:?usage: 05-understand-layout.sh RUN}; ROOT=$(cd "$(dirname "$0")/.." && pwd); TMP=$(mktemp "$RUN/manifests/layout.XXXXXX")
trap 'rm -f "$TMP"' EXIT
cd "$ROOT"
lord @repo --quiet <<LORD >"$TMP"
You are stage 05 of an image-to-epigraphic-font pipeline. Inspect $RUN/source/source.png, $RUN/preprocess/preprocessing-contact-sheet.png, every $RUN/segmentation/hypothesis-*.png and its JSON/contact sheet. These hypotheses are deterministic suggestions, not truth.

Decide which regions are ancient glyphs, labels, rules, borders, captions, or noise; identify alphabet rows and variants; select the closest hypothesis; and correct/merge/split boxes only where the pixels support it. A disconnected stroke may belong to one glyph and touching glyphs may need separation. Source chart order is not necessarily Unicode RTL order. Do not draw, beautify, hallucinate strokes, or confuse Hebrew/English labels with ancient signs. State uncertainty through 0..1 confidence and short rationales.

Return ONLY JSON conforming to $ROOT/schemas/layout.schema.json. Stable glyph IDs must look like g-row01-col03-v01. bbox is [x,y,width,height] in source pixels. Include chosen_hypothesis, alphabets, default_alphabet, glyph_regions, ignored_regions, confidence, rationale. The source pixels outrank paleographic expectations. No Markdown fences.
LORD
"$ROOT/bin/validate-json.py" "$ROOT/schemas/layout.schema.json" "$TMP" "$RUN/manifests/layout.json"
