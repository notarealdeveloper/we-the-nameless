#!/usr/bin/env -S fontforge -script
"""Generate ASCII-encoded copies of the normalized ancient fonts.

fonts2/ is the semantic normalization layer: every ancient script font exposes
its glyphs through the Hebrew Unicode block.  fonts-ascii/ is a keyboard-entry
layer: every ASCII letter used by the transliteration table below is copied
from the corresponding Hebrew codepoint.
"""

from __future__ import annotations

import os
import re
import sys

import fontforge


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(ROOT, "fonts2")
TARGET_DIR = os.path.join(ROOT, "fonts-ascii")


HEBREW_BY_ASCII = {
    "a": "א",
    "b": "ב",
    "v": "ב",
    "g": "ג",
    "d": "ד",
    "e": "ה",
    "h": "ה",
    "w": "ו",
    "z": "ז",
    "x": "ח",
    "H": "ח",
    "T": "ט",
    "0": "ט",
    "i": "י",
    "j": "י",
    "y": "י",
    "k": "כ",
    "K": "ך",
    "l": "ל",
    "m": "מ",
    "M": "ם",
    "n": "נ",
    "N": "ן",
    "S": "ס",
    "o": "ע",
    "A": "ע",
    "p": "פ",
    "P": "ף",
    "c": "צ",
    "C": "ץ",
    "q": "ק",
    "r": "ר",
    "s": "ש",
    "t": "ת",
}

# Fill unused ASCII letters with predictable aliases.  Lowercase keeps the
# closest available phonetic value; uppercase either mirrors lowercase or, for
# the five Hebrew final forms, keeps the final-form convention already used by
# K/M/N/P/C above.
ASCII_ALIASES = {
    "B": "ב",
    "D": "ד",
    "E": "ה",
    "f": "ף",
    "F": "ף",
    "G": "ג",
    "I": "י",
    "J": "י",
    "L": "ל",
    "O": "ע",
    "Q": "ק",
    "R": "ר",
    "u": "ו",
    "U": "ו",
    "V": "ב",
    "W": "ו",
    "X": "ח",
    "Y": "י",
    "Z": "ז",
}

ASCII_TO_HEBREW = {**HEBREW_BY_ASCII, **ASCII_ALIASES}


def ps_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", name)


def glyph_name(codepoint: int) -> str:
    return fontforge.nameFromUnicode(codepoint) or f"uni{codepoint:04X}"


def keep_blank_glyph_in_cmap(glyph) -> None:
    if len(glyph.foreground) != 0:
        return

    pen = glyph.glyphPen()
    pen.moveTo((0, -1000))
    pen.lineTo((1, -1000))
    pen.lineTo((1, -999))
    pen.lineTo((0, -999))
    pen.closePath()


def copy_glyph(src, dst, src_code: int, dst_code: int) -> bool:
    if src_code not in src:
        return False

    src.selection.none()
    src.selection.select(("unicode",), src_code)
    src.copy()

    dst.createChar(dst_code)
    dst.selection.none()
    dst.selection.select(("unicode",), dst_code)
    dst.paste()

    glyph = dst[dst_code]
    glyph.glyphname = glyph_name(dst_code)
    keep_blank_glyph_in_cmap(glyph)
    return True


def blank_glyph(dst, dst_code: int, width: int = 300) -> None:
    glyph = dst.createChar(dst_code)
    glyph.glyphname = glyph_name(dst_code)
    glyph.width = width
    keep_blank_glyph_in_cmap(glyph)


def add_space(dst) -> None:
    glyph = dst.createChar(ord(" "))
    glyph.glyphname = "space"
    glyph.width = 300


def build_font(source_path: str) -> list[str]:
    source_filename = os.path.basename(source_path)
    source_family = os.path.splitext(source_filename)[0]
    ascii_family = f"{source_family}-ascii"
    output_path = os.path.join(TARGET_DIR, f"{ascii_family}.ttf")

    src = fontforge.open(source_path)
    dst = fontforge.font()
    dst.encoding = "UnicodeFull"
    dst.em = src.em
    dst.ascent = src.ascent
    dst.descent = src.descent
    dst.familyname = ascii_family
    dst.fullname = ascii_family
    dst.fontname = ps_name(ascii_family)
    dst.weight = src.weight or "Regular"
    dst.copyright = src.copyright
    dst.version = src.version or "1.000"
    dst.appendSFNTName("English (US)", "Family", ascii_family)
    dst.appendSFNTName("English (US)", "Fullname", ascii_family)
    dst.appendSFNTName("English (US)", "PostScriptName", ps_name(ascii_family))
    dst.appendSFNTName("English (US)", "SubFamily", "Regular")
    dst.appendSFNTName("English (US)", "Preferred Family", ascii_family)
    dst.appendSFNTName("English (US)", "Preferred Styles", "Regular")
    dst.appendSFNTName("English (US)", "Compatible Full", ascii_family)

    missing = []
    add_space(dst)
    for ascii_char, hebrew_char in sorted(ASCII_TO_HEBREW.items()):
        if not copy_glyph(src, dst, ord(hebrew_char), ord(ascii_char)):
            blank_glyph(dst, ord(ascii_char))
            missing.append(f"{ascii_char}->U+{ord(hebrew_char):04X}")

    dst.os2_typoascent = src.os2_typoascent
    dst.os2_typodescent = src.os2_typodescent
    dst.os2_winascent = src.os2_winascent
    dst.os2_windescent = src.os2_windescent
    dst.generate(output_path, flags=("opentype", "dummy-dsig"))
    dst.close()
    src.close()
    return missing


def main() -> int:
    if not os.path.isdir(SOURCE_DIR):
        print(f"missing {SOURCE_DIR}; run tools/uniformize_ancient_fonts.py first", file=sys.stderr)
        return 1

    os.makedirs(TARGET_DIR, exist_ok=True)
    for name in os.listdir(TARGET_DIR):
        if name.endswith((".ttf", ".otf")):
            os.remove(os.path.join(TARGET_DIR, name))

    blanked = {}
    for name in sorted(os.listdir(SOURCE_DIR)):
        if not name.endswith((".ttf", ".otf")):
            continue
        print(f"building {os.path.splitext(name)[0]}-ascii.ttf")
        missing = build_font(os.path.join(SOURCE_DIR, name))
        if missing:
            blanked[name] = missing

    for name, missing in blanked.items():
        print(f"{name}: blanked unavailable glyphs: {', '.join(missing)}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
