#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
font_dir="$root/fonts-ascii"
out_dir="${1:-$root/fonts-ascii-pango-test-output}"
sample='abvgdehwzxHT0ijykKl mMnNSoApPcCqrst'

if [[ ! -d "$font_dir" ]]; then
  echo "missing $font_dir; run tools/asciify_fonts2.py first" >&2
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
  family="${base%.*}"
  matched="$(fc-match --format '%{file}' ":family=$family")"

  if [[ "$(realpath "$matched")" != "$(realpath "$font")" ]]; then
    echo "FAIL $family: fontconfig matched $matched" >&2
    status=1
    continue
  fi

  outside="$(
    fontforge -lang=py -c '
import fontforge, sys
allowed = set(map(ord, "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0 "))
f = fontforge.open(sys.argv[1])
bad = []
for g in f.glyphs():
    if g.unicode >= 0 and g.unicode not in allowed:
        bad.append("U+%04X" % g.unicode)
if bad:
    print(" ".join(bad))
f.close()
' "$font" 2>/dev/null
  )"

  if [[ -n "$outside" ]]; then
    echo "FAIL $family: glyphs outside ASCII layer: $outside" >&2
    status=1
    continue
  fi

  png="$out_dir/$family.png"
  pango-view \
    --no-display \
    --output="$png" \
    --font="$family 48" \
    --text="$sample" \
    --margin=12 \
    --foreground=black \
    --background=white >/dev/null

  if [[ ! -s "$png" ]]; then
    echo "FAIL $family: pango-view did not create $png" >&2
    status=1
    continue
  fi

  echo "OK   $family -> $png"
done

exit "$status"
