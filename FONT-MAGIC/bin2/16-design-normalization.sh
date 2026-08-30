#!/usr/bin/env bash
set -euo pipefail
RUN=${1:?usage: 16-design-normalization.sh RUN}; ROOT=$(cd "$(dirname "$0")/.." && pwd); TMP=$(mktemp "$RUN/manifests/norm.XXXXXX"); trap 'rm -f "$TMP"' EXIT; cd "$ROOT"
lord @repo --quiet <<LORD >"$TMP"
You are stage 16, making paleographic font-design judgments. Inspect the entire source, metrics contact sheet, cleaned/repaired traces, crops, and measurements.json. Turn the coherent source set into a usable font while retaining original relative geometry.

Normalize the common 1000-UPM canvas (ascent 800, descent 200), never every glyph to one height/width/mass/slant/stroke. Preserve relative scale when the chart makes it meaningful; ignore editorial cell padding. Decide a common body scale, real source baseline if any, relative offsets and widths, sidebearings, and genuine outliers. Avoid per-glyph rotation unless source-image skew is strongly evidenced. Do not normalize stroke weight by default. Return ONLY JSON conforming to $ROOT/schemas/normalization.schema.json: font metrics and an entry for every candidate with canonical_name, scale, translate_x, translate_y, advance_width, confidence, rationale. No Markdown.
LORD
"$ROOT/bin/validate-json.py" "$ROOT/schemas/normalization.schema.json" "$TMP" "$RUN/manifests/normalization.json"
