#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out="${1:-$root/tel-zayit-fonts.png}"

# Pango performs the shaping; the families resolve to the copies installed from
# fonts/ (and are checked here to avoid silently rendering a fallback face).
for family in "WTN Paleo Hebrew Tel Zayit" "Tel Zayit"; do
  matched="$(fc-match --format '%{family}' "$family")"
  [[ "$matched" == *"$family"* ]] || {
    printf 'font family not available to Pango: %s\n' "$family" >&2
    exit 1
  }
done

markup='<span font_family="DejaVu Sans" foreground="#1d252c" size="30000" weight="bold">TEL ZAYIT FONT SPECIMEN</span>
<span font_family="DejaVu Sans" foreground="#6b747c" size="15000">Canonical order:  aleph · bet · gimel · dalet · he · waw · zayin · heth · tet · yod · kaf · lamed · mem · nun · samekh · ayin · pe · tsade · qof · resh · shin · taw</span>

<span font_family="DejaVu Sans" foreground="#39444d" size="17500" weight="bold">08-bc10c-paleo-hebrew-tel-zayit.ttf</span>
<span font_family="DejaVu Sans" foreground="#7a838a" size="13500">WTN Paleo Hebrew Tel Zayit — repaired chronological font</span>
<span font_family="WTN Paleo Hebrew Tel Zayit" foreground="#111111" size="61000">a  b  g  d  e  w  z  h  T  y  k  l  m  n  S  o  p  c  q  r  s  t</span>

<span font_family="DejaVu Sans" foreground="#39444d" size="17500" weight="bold">paleo-hebrew-tel-zayit.ttf</span>
<span font_family="DejaVu Sans" foreground="#7a838a" size="13500">Tel Zayit — legacy source font</span>
<span font_family="Tel Zayit" foreground="#111111" size="61000">a  b  g  d  e  w  z  h  T  y  k  l  m  n  S  o  p  c  q  r  s  t</span>'

pango-view \
  --no-display \
  --markup \
  --pixels \
  --dpi=144 \
  --margin=90 \
  --spacing=20 \
  --width=2200 \
  --background='#f7f3eb' \
  --foreground='#111111' \
  --antialias=gray \
  --hinting=slight \
  --output="$out" \
  --text="$markup"

printf '%s\n' "$out"
