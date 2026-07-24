#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
font_dir="$root/fonts-master"
out_dir="${1:-$root/fonts-master-pango-test-output}"
sample='abvgdehwzxHT0ijykKl mMnNSoApPcCqrst'
allowed_keys="$("$root/bin/alphabet") "

if [[ ! -d "$font_dir" ]]; then
  echo "missing $font_dir; run tools/build_fonts_master.py first" >&2
  exit 1
fi

mkdir -p "$out_dir"

fontconfig_file="$(mktemp)"
fontconfig_cache="$(mktemp -d)"
trap 'rm -f "$fontconfig_file"; rm -rf "$fontconfig_cache"' EXIT

cat >"$fontconfig_file" <<XML
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>
  <dir>$font_dir</dir>
  <cachedir>$fontconfig_cache</cachedir>
</fontconfig>
XML

export FONTCONFIG_FILE="$fontconfig_file"

fc-cache -f "$font_dir" >/dev/null

status=0
for font in "$font_dir"/*.{ttf,otf}; do
  [[ -e "$font" ]] || continue

  base="$(basename "$font")"
  family="$(fc-scan --format '%{family}\n' "$font" | head -n1)"
  style="$(fc-scan --format '%{style}\n' "$font" | head -n1)"
  matched="$(fc-match --format '%{file}' ":family=$family:style=$style")"

  if [[ "$(realpath "$matched")" != "$(realpath "$font")" ]]; then
    echo "FAIL $family: fontconfig matched $matched" >&2
    status=1
    continue
  fi

  outside="$(
    fontforge -lang=py -c '
import fontforge, sys
from importlib.machinery import SourceFileLoader
import importlib.util

font_path, alphabet_path, allowed_chars = sys.argv[1:4]
spec = importlib.util.spec_from_loader("wtn_alphabet", SourceFileLoader("wtn_alphabet", alphabet_path))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
allowed = set(map(ord, allowed_chars))
f = fontforge.open(sys.argv[1])
bad = []
for g in f.glyphs():
    if g.unicode >= 0 and g.unicode not in allowed and g.unicode not in {0, 13}:
        bad.append("U+%04X" % g.unicode)
if bad:
    print(" ".join(bad))
f.close()
' "$font" "$root/bin/alphabet" "$allowed_keys" 2>/dev/null
  )"

  if [[ -n "$outside" ]]; then
    echo "FAIL $family: glyphs outside configured fonts-master key layer: $outside" >&2
    status=1
    continue
  fi

  png="$out_dir/${base%.*}.png"
  rm -f "$png"
  pango-view \
    --no-display \
    --output="$png" \
    --font="$family 48" \
    --text="$sample" \
    --margin=12 \
    --foreground=black \
    --background=white >/dev/null

  if [[ ! -s "$png" ]]; then
    rm -f "$png"
    pango-view \
      --no-display \
      --output="$png" \
      --font="$family $style 48" \
      --text="$sample" \
      --margin=12 \
      --foreground=black \
      --background=white >/dev/null
  fi

  if [[ ! -s "$png" ]]; then
    echo "FAIL $family: pango-view did not create $png" >&2
    status=1
    continue
  fi

  echo "OK   $family -> $png"
done

exit "$status"
