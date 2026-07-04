#!/usr/bin/env -S fontforge -script
"""Generate fonts-master copies of the normalized ancient fonts.

fonts2/ is the semantic normalization layer: every ancient script font exposes
its glyphs through the Hebrew Unicode block.  fonts-master/ is the public input
layer: every key in bin/alphabet is copied from the corresponding Hebrew
codepoint.
"""

from __future__ import annotations

import importlib.util
import os
import re
import sys
from importlib.machinery import SourceFileLoader

import fontforge
import psMat


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(ROOT, "fonts2")
TARGET_DIR = os.path.join(ROOT, "fonts-master")


def load_alphabet_map() -> dict[str, str]:
    path = os.path.join(ROOT, "bin", "alphabet")
    spec = importlib.util.spec_from_loader(
        "wtn_alphabet",
        SourceFileLoader("wtn_alphabet", path),
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.key_to_hebrew()


KEY_TO_HEBREW = load_alphabet_map()

REFERENCE_HEBREW_MEDIAN_HEIGHT = 584
GLYPH_SIDE_BEARING = 60
SPACE_WIDTH = 300


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


def blank_glyph(dst, dst_code: int, width: int = SPACE_WIDTH) -> None:
    glyph = dst.createChar(dst_code)
    glyph.glyphname = glyph_name(dst_code)
    glyph.width = width
    keep_blank_glyph_in_cmap(glyph)


def add_space(dst) -> None:
    glyph = dst.createChar(ord(" "))
    glyph.glyphname = "space"
    glyph.width = SPACE_WIDTH


def ink_glyphs(font):
    glyphs = []
    for codepoint in KEY_TO_HEBREW:
        code = ord(codepoint)
        if code not in font:
            continue

        glyph = font[code]
        if not glyph.isWorthOutputting():
            continue

        xmin, ymin, xmax, ymax = glyph.boundingBox()
        width = xmax - xmin
        height = ymax - ymin
        if width > 1 and height > 1:
            glyphs.append(glyph)
    return glyphs


def median(values: list[float]) -> float:
    values = sorted(values)
    if not values:
        return 0

    midpoint = len(values) // 2
    if len(values) % 2:
        return values[midpoint]
    return (values[midpoint - 1] + values[midpoint]) / 2


def normalize_size_and_spacing(font) -> None:
    glyphs = ink_glyphs(font)
    median_height = median([
        glyph.boundingBox()[3] - glyph.boundingBox()[1]
        for glyph in glyphs
    ])

    if median_height > 0:
        scale = REFERENCE_HEBREW_MEDIAN_HEIGHT / median_height
        for glyph in glyphs:
            glyph.transform(psMat.scale(scale))
            glyph.round()

    for glyph in ink_glyphs(font):
        xmin, _ymin, xmax, _ymax = glyph.boundingBox()
        glyph.transform(psMat.translate(GLYPH_SIDE_BEARING - xmin, 0))
        glyph.width = int(round((xmax - xmin) + (2 * GLYPH_SIDE_BEARING)))

    if ord(" ") in font:
        font[ord(" ")].width = SPACE_WIDTH


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
    for key, hebrew_char in sorted(KEY_TO_HEBREW.items(), key=lambda item: ord(item[0])):
        if not copy_glyph(src, dst, ord(hebrew_char), ord(key)):
            blank_glyph(dst, ord(key))
            missing.append(f"U+{ord(key):04X}->U+{ord(hebrew_char):04X}")

    normalize_size_and_spacing(dst)

    dst.os2_typoascent = src.os2_typoascent
    dst.os2_typodescent = src.os2_typodescent
    dst.os2_winascent = src.os2_winascent
    dst.os2_windescent = src.os2_windescent
    dst.generate(output_path, flags=("dummy-dsig",))
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
