#!/usr/bin/env bash
set -euo pipefail
RUN=${1:?usage: 21-qa-font.sh RUN}; ROOT=$(cd "$(dirname "$0")/.." && pwd); TMP=$(mktemp "$RUN/manifests/qa.XXXXXX"); trap 'rm -f "$TMP"' EXIT; cd "$ROOT"
lord @repo --quiet <<LORD >"$TMP"
You are stage 21, final font proofreader and paleographic fidelity reviewer. Inspect proofs/proof.png and proof.pdf, the source, crops, masks, normalized glyphs, identity and normalization manifests. Score source fidelity, completeness, identity confidence, scale, spacing, trace quality, noise, and omissions, plus each glyph 0..100.

Find outliers, not excuses to redesign the alphabet. Allowed actions only: accept, adjust_scale, adjust_y, adjust_sidebearing, choose_variant, redo_mask, redo_trace, manual_review. Small affine/spacing adjustments must be modest and numeric in adjustment. Fundamentally ambiguous reconstruction is manual_review. Never invent missing strokes or modernize odd forms. Return ONLY JSON conforming to $ROOT/schemas/final-qa.schema.json. No Markdown.
LORD
"$ROOT/bin/validate-json.py" "$ROOT/schemas/final-qa.schema.json" "$TMP" "$RUN/manifests/final-qa.json"
