#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
font_dir="$root/fonts-ascii"
out="${1:-$root/fonts-ascii-catalog.png}"
sample="${2:-abgdhwzxTyklmnSopcqrst}"
label_font="$(fc-match --format '%{file}' 'DejaVu Sans')"
label_bold_font="$(fc-match --format '%{file}' 'DejaVu Sans:style=Bold')"

if [[ ! -d "$font_dir" ]]; then
  echo "missing $font_dir; run tools/asciify_fonts2.py first" >&2
  exit 1
fi

work="$(mktemp -d)"
fontconfig_file="$(mktemp)"
fontconfig_cache="$(mktemp -d)"
trap 'rm -rf "$work"; rm -f "$fontconfig_file"; rm -rf "$fontconfig_cache"' EXIT

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

i=0
rows=()
for font in "$font_dir"/*.{ttf,otf}; do
  [[ -e "$font" ]] || continue
  base="$(basename "$font")"
  i=$((i + 1))
  label_png="$(printf '%s/label-%03d.png' "$work" "$i")"
  glyph_png="$(printf '%s/glyph-%03d.png' "$work" "$i")"
  row_png="$(printf '%s/row-%03d.png' "$work" "$i")"

  magick -size 900x92 xc:white \
    -gravity west \
    -font "$label_font" \
    -pointsize 24 \
    -fill '#202020' \
    -annotate +18+0 "$base" \
    "$label_png"

  magick -size 1300x92 xc:white \
    -gravity west \
    -font "$font" \
    -pointsize 42 \
    -fill black \
    -annotate +18+0 "$sample" \
    "$glyph_png"

  magick "$label_png" "$glyph_png" +append -background white -gravity center -extent 2200x110 "$row_png"
  rows+=("$row_png")
done

if [[ "${#rows[@]}" -eq 0 ]]; then
  echo "no font files found in $font_dir" >&2
  exit 1
fi

header="$work/header.png"
magick -size 2200x130 xc:white \
  -gravity northwest \
  -font "$label_bold_font" \
  -pointsize 34 \
  -fill '#111111' \
  -annotate +18+18 "ASCII ancient-script font catalog" \
  -font "$label_font" \
  -pointsize 24 \
  -fill '#333333' \
  -annotate +18+72 "Sample: $sample" \
  "$header"

if [[ "${out,,}" == *.pdf ]]; then
  catalog_png="$work/catalog.png"
  magick "$header" "${rows[@]}" -append "$catalog_png"
  page_size="$(identify -format '%wx%h' "$catalog_png")"
  magick "$catalog_png" +repage -density 72 -units PixelsPerInch -page "$page_size" "$out"
else
  magick "$header" "${rows[@]}" -append "$out"
fi
echo "$out"
