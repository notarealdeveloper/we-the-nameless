#!/usr/bin/env bash
set -euo pipefail
RUN=${1:?usage: 09-choose-masks.sh RUN}; ROOT=$(cd "$(dirname "$0")/.." && pwd); TMP=$(mktemp "$RUN/manifests/masks.XXXXXX"); trap 'rm -f "$TMP"' EXIT; cd "$ROOT"
lord @repo --quiet <<LORD >"$TMP"
You are stage 09. For every candidate inspect crops/*/source.png and context.png, masks/*/contact-sheet.png and components.json, plus glyph-identities.json. Compare actual ink to raw, otsu, adaptive, sauvola, conservative, and clean masks.

Choose the mask that preserves the source, list exact component IDs to keep/drop/mark uncertain, and report lost thin strokes, incorporated noise, or repair need. Small or weird strokes may be historically decisive: never remove one merely because a familiar letter looks prettier without it. Damage and ambiguous ink should be preserved or flagged, not silently corrected. Return ONLY JSON conforming to $ROOT/schemas/mask-decisions.schema.json. Every candidate needs confidence and rationale. No Markdown or invented component IDs.
LORD
"$ROOT/bin/validate-json.py" "$ROOT/schemas/mask-decisions.schema.json" "$TMP" "$RUN/manifests/mask-decisions.json"
