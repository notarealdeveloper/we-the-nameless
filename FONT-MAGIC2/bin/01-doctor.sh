#!/usr/bin/env bash
set -euo pipefail
RUNTIME=0; [[ ${1:-} == --runtime ]] && RUNTIME=1
fatal=0
need(){ if command -v "$1" >/dev/null; then printf 'ok       %s: %s\n' "$1" "$(command -v "$1")"; else printf 'MISSING  %s: %s\n' "$1" "$2"; if [[ $3 == required ]]; then fatal=1; fi; fi; return 0; }
need bash 'install Bash' required; need python3 'install Python 3.10+' required; need fontforge 'install FontForge with Python scripting' required; need magick 'install ImageMagick (proof PDF fallback uses Pillow)' optional; need potrace 'install Potrace for smooth vector outlines; pixel-exact SVG fallback is usable but heavy' optional; need mkbitmap 'install with Potrace for additional preprocessing' optional; need hb-shape 'install HarfBuzz CLI for shaping validation' optional; need ots-sanitize 'install OpenType Sanitizer' optional; need fontbakery 'pip install fontbakery' optional; need lord 'required for AI stages; use --no-ai for deterministic debugging' optional
python3 - <<'PY' || fatal=1
mods={'PIL':'Pillow (required)','numpy':'numpy (required)','fontTools':'fonttools (required)','cv2':'opencv-python-headless (optional)','skimage':'scikit-image (optional)','yaml':'PyYAML (optional; JSON is valid YAML)','jsonschema':'jsonschema (recommended full schema validation)','reportlab':'reportlab (optional)'}
bad=False
for m,desc in mods.items():
 try: __import__(m); print('ok      ',m)
 except Exception: print('MISSING ',desc); bad |= '(required)' in desc
raise SystemExit(1 if bad else 0)
PY
((fatal==0)) || { echo 'Doctor found missing required dependencies. See README.md.' >&2; exit 1; }
