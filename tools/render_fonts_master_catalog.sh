#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
font_dir="$root/fonts-master"
out="${1:-$root/fonts-master-catalog.png}"
label_font="$(fc-match --format '%{file}' 'DejaVu Sans')"
label_bold_font="$(fc-match --format '%{file}' 'DejaVu Sans:style=Bold')"

if [[ ! -d "$font_dir" ]]; then
  echo "missing $font_dir; run tools/build_fonts_master.py first" >&2
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

labels=(aleph bet gimel dalet he waw zayin het tet yod kaf lamed mem nun samekh ayin pe tsade qof resh shin taw)
hebrew=(א ב ג ד ה ו ז ח ט י כ ל מ נ ס ע פ צ ק ר ש ת)
keys=(a b g d h w z H T y k l m n S A p c q r s t)

label_w=720
cell_w=88
row_h=92
header_h=156
table_w=$((label_w + (${#keys[@]} * cell_w)))

rows=()
i=0
for font in "$font_dir"/*.{ttf,otf}; do
  [[ -e "$font" ]] || continue
  base="$(basename "$font")"
  i=$((i + 1))
  row_png="$(printf '%s/row-%03d.png' "$work" "$i")"

  magick -size "${table_w}x${row_h}" xc:white \
    -font "$label_font" \
    -pointsize 18 \
    -fill '#202020' \
    -gravity west \
    -annotate +16+0 "$base" \
    "$row_png"

  for idx in "${!keys[@]}"; do
    x=$((label_w + (idx * cell_w)))
    char="${keys[$idx]}"
    magick "$row_png" \
      -fill '#ECE7DF' -draw "rectangle $x,0 $((x + cell_w - 1)),$row_h" \
      -stroke '#D8D1C8' -strokewidth 1 -draw "line $x,0 $x,$row_h" \
      -stroke none \
      -font "$font" \
      -pointsize 42 \
      -fill black \
      -gravity northwest \
      -annotate "+$((x + 22))+22" "$char" \
      "$row_png"
  done
  magick "$row_png" -stroke '#D8D1C8' -strokewidth 1 -draw "line 0,$((row_h - 1)) $table_w,$((row_h - 1))" "$row_png"
  rows+=("$row_png")
done

if [[ "${#rows[@]}" -eq 0 ]]; then
  echo "no font files found in $font_dir" >&2
  exit 1
fi

header="$work/header.png"
magick -size "${table_w}x${header_h}" xc:white \
  -font "$label_bold_font" \
  -pointsize 32 \
  -fill '#111111' \
  -gravity northwest \
  -annotate +16+16 "Ancient-script font catalog" \
  -font "$label_font" \
  -pointsize 20 \
  -fill '#333333' \
  -annotate +16+62 "Columns follow Hebrew alphabet order; cells render the master key mapped to that Hebrew letter." \
  "$header"

for idx in "${!keys[@]}"; do
  x=$((label_w + (idx * cell_w)))
  magick "$header" \
    -fill '#F6F3EE' -draw "rectangle $x,96 $((x + cell_w - 1)),$header_h" \
    -stroke '#D8D1C8' -strokewidth 1 -draw "line $x,96 $x,$header_h" \
    -stroke none \
    -font "$label_bold_font" \
    -pointsize 21 \
    -fill '#111111' \
    -gravity northwest \
    -annotate "+$((x + 30))+101" "${hebrew[$idx]}" \
    -font "$label_font" \
    -pointsize 12 \
    -fill '#444444' \
    -annotate "+$((x + 8))+128" "${labels[$idx]} / ${keys[$idx]}" \
    "$header"
done
magick "$header" -stroke '#D8D1C8' -strokewidth 1 -draw "line 0,$((header_h - 1)) $table_w,$((header_h - 1))" "$header"

if [[ "${out,,}" == *.pdf ]]; then
  catalog_png="$work/catalog.png"
  magick "$header" "${rows[@]}" -append "$catalog_png"
  page_size="$(identify -format '%wx%h' "$catalog_png")"
  magick "$catalog_png" +repage -density 72 -units PixelsPerInch -page "$page_size" "$out"
else
  magick "$header" "${rows[@]}" -append "$out"
fi

echo "$out"
