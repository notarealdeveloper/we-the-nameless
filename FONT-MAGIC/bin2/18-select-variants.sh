#!/usr/bin/env bash
set -euo pipefail
RUN=${1:?usage: 18-select-variants.sh RUN}; ROOT=$(cd "$(dirname "$0")/.." && pwd); TMP=$(mktemp "$RUN/manifests/variants.XXXXXX"); trap 'rm -f "$TMP"' EXIT; cd "$ROOT"
lord @repo --quiet <<LORD >"$TMP"
You are stage 18. Inspect source contexts, masks, normalized contact sheet, identities, measurements, and normalization. For each canonical letter with multiple attested forms, select the clearest representative default, rank every form, retain damaged forms, and explain briefly. Do not discard unusual variants or replace them with expected shapes. Selection concerns default encoding only; all candidates remain named alternates.

Return ONLY JSON conforming to $ROOT/schemas/variants.schema.json. Each group needs canonical_name, default_candidate_id, ranked_candidates containing every candidate exactly once, damaged_candidates, confidence, rationale. No Markdown.
LORD
"$ROOT/bin/validate-json.py" "$ROOT/schemas/variants.schema.json" "$TMP" "$RUN/manifests/variants.json"
