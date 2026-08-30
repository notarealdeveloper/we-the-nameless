#!/usr/bin/env bash
set -euo pipefail
RUN=${1:?usage: 13-judge-traces.sh RUN}; ROOT=$(cd "$(dirname "$0")/.." && pwd); TMP=$(mktemp "$RUN/manifests/traces.XXXXXX"); trap 'rm -f "$TMP"' EXIT; cd "$ROOT"
lord @repo --quiet <<LORD >"$TMP"
You are stage 13. Compare each crops/*/source.png, masks/final/*.png and overlay, traces/raw/*.svg, traces/clean/*.svg and previews. Detect missing strokes, invented blobs, merged strokes, accidental holes, filled counters, damaged corners, over-smoothing, pixel jaggedness, noise-as-ink, and ink-as-noise.

Do not edit Beziers or redesign glyphs. Prefer finite deterministic repairs: alternate_mask, restore_component, remove_component, dilate, erode, close, or retrace; otherwise manual_review. Use accept when faithful. A strange stroke is evidence, not ugliness. Return ONLY JSON conforming to $ROOT/schemas/trace-repairs.schema.json with action, supported operations, confidence and concise rationale per candidate. No Markdown.
LORD
"$ROOT/bin/validate-json.py" "$ROOT/schemas/trace-repairs.schema.json" "$TMP" "$RUN/manifests/trace-repairs.json"
