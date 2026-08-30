#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
PYTHONPATH="$ROOT" python3 "$ROOT/tests/make_fixture.py" >/dev/null
rm -rf "$ROOT/tests/output"
"$ROOT/bin/00-fontify.sh" "$ROOT/tests/fixtures/synthetic-chart.png" --name SyntheticEpigraphy --output "$ROOT/tests/output" --no-ai --keep-work
for f in SyntheticEpigraphy.sfd SyntheticEpigraphy.otf SyntheticEpigraphy.ttf proof.pdf proof.png report.html manifest.json; do test -s "$ROOT/tests/output/$f"; done
PYTHONPATH="$ROOT" python3 - <<'PY' "$ROOT/tests/output/SyntheticEpigraphy.ttf" "$ROOT/tests/output/manifest.json"
import json,sys
from fontTools.ttLib import TTFont
f=TTFont(sys.argv[1]); assert 'cmap' in f; assert len(f.getBestCmap())>=1
m=json.load(open(sys.argv[2])); assert m['glyphs']; assert all(g['source_sha256'] and g['source_rect'] for g in m['glyphs'])
root=__import__('pathlib').Path(sys.argv[2]).parent
svgs=list((root/'glyphs').glob('*.svg')); assert len(svgs)>=20
import xml.etree.ElementTree as ET
for p in svgs:
 tree=ET.parse(p); tags=[node.tag.rsplit('}',1)[-1] for node in tree.iter()]
 assert tree.getroot().tag.rsplit('}',1)[-1]=='svg' and any(t in {'path','rect'} for t in tags),p
PY
