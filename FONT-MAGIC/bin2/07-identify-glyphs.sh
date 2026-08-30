#!/usr/bin/env bash
set -euo pipefail
RUN=${1:?usage: 07-identify-glyphs.sh RUN}; ROOT=$(cd "$(dirname "$0")/.." && pwd); TMP=$(mktemp "$RUN/manifests/identities.XXXXXX"); trap 'rm -f "$TMP"' EXIT; cd "$ROOT"
lord @repo --quiet <<LORD >"$TMP"
You are stage 07. Inspect $RUN/source/source.png, $RUN/crops/contact-sheet.png, every crops/*/source.png, context.png, metadata.json, and $RUN/manifests/layout.json. Map candidates to exactly these canonical names when supported: aleph bet gimel dalet he waw zayin het tet yod kaf lamed mem nun samekh ayin pe tsade qof resh shin taw. Accept spelling aliases mentally but emit canonical names.

Use shape, visible labels, alphabet sequence, neighbors, row structure, and historically attested forms together; position alone is weak evidence. Preserve multiple variants, damage, alternates, uncertainty, and missing letters. Never manufacture a missing sign or infer invisible strokes. If a label conflicts with the visible form, record it in notes. Return ONLY JSON conforming to $ROOT/schemas/glyph-identities.schema.json with candidate_id, canonical_name (null if unmapped), confidence 0..1, variant_group, source_order, is_default_candidate, damaged, notes, alternates; plus missing and overall confidence. No Markdown.
LORD
"$ROOT/bin/validate-json.py" "$ROOT/schemas/glyph-identities.schema.json" "$TMP" "$RUN/manifests/glyph-identities.json"
