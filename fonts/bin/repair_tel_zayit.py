#!/usr/bin/env python3
"""Repair the ASCII glyph map and punctuation in the Tel Zayit font."""

from __future__ import annotations

import sys
from pathlib import Path

from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont


def circle_glyph(radius: int = 250, stroke: int = 28):
    """Return a hand-drawn-weight circular ayin as a TrueType outline."""
    pen = TTGlyphPen(None)
    cx, cy = 310, 450

    # Quadratic Bézier control distance for a close approximation of a circle.
    control = round(radius * 0.41421356237)
    pen.moveTo((cx, cy + radius))
    pen.qCurveTo((cx + control, cy + radius), (cx + radius, cy + control), (cx + radius, cy))
    pen.qCurveTo((cx + radius, cy - control), (cx + control, cy - radius), (cx, cy - radius))
    pen.qCurveTo((cx - control, cy - radius), (cx - radius, cy - control), (cx - radius, cy))
    pen.qCurveTo((cx - radius, cy + control), (cx - control, cy + radius), (cx, cy + radius))
    pen.closePath()

    inner = radius - stroke
    control = round(inner * 0.41421356237)
    # Reverse winding makes the inner contour a counter.
    pen.moveTo((cx, cy + inner))
    pen.qCurveTo((cx - control, cy + inner), (cx - inner, cy + control), (cx - inner, cy))
    pen.qCurveTo((cx - inner, cy - control), (cx - control, cy - inner), (cx, cy - inner))
    pen.qCurveTo((cx + control, cy - inner), (cx + inner, cy - control), (cx + inner, cy))
    pen.qCurveTo((cx + inner, cy + control), (cx + control, cy + inner), (cx, cy + inner))
    pen.closePath()
    return pen.glyph()


def polygon_glyph(points):
    """Return a closed polygon as a TrueType outline."""
    pen = TTGlyphPen(None)
    pen.moveTo(points[0])
    for point in points[1:]:
        pen.lineTo(point)
    pen.closePath()
    return pen.glyph()


def add_glyph(font: TTFont, name: str, codepoint: int, glyph, advance: int) -> None:
    """Add a glyph and expose it through every Unicode cmap."""
    if name not in font.getGlyphOrder():
        font.setGlyphOrder([*font.getGlyphOrder(), name])
    font["glyf"][name] = glyph
    font["hmtx"][name] = (advance, 50)
    for table in font["cmap"].tables:
        if table.isUnicode():
            table.cmap[codepoint] = name


def repair(path: Path) -> None:
    font = TTFont(path)

    # Ayin is encoded as O/o by master.tex. Both glyph slots get the same ring.
    for glyph_name in ("O", "o"):
        font["glyf"][glyph_name] = circle_glyph()
        font["hmtx"][glyph_name] = (620, 60)

    # This face stores He at E/e. Point H/h there too, replacing the Heth map.
    for table in font["cmap"].tables:
        if ord("H") in table.cmap and ord("h") in table.cmap:
            table.cmap[ord("H")] = table.cmap[ord("E")]
            table.cmap[ord("h")] = table.cmap[ord("e")]

        # Shin and tav live in this face's lowercase s/t slots. Keep direct
        # Hebrew-codepoint rendering aligned with the Tel Zayit ASCII encoder;
        # the uppercase V/T slots contain waw and teth forms in this font.
        if table.isUnicode():
            table.cmap[ord("ש")] = table.cmap[ord("s")]
            table.cmap[ord("ת")] = table.cmap[ord("t")]

    # Editorial gaps and supplied text use these ASCII characters in the
    # reconstructed FMC/DNF Hebrew. Keep them in the historical face so they
    # survive font selection instead of rendering as missing-glyph boxes.
    add_glyph(font, "underscore", ord("_"), polygon_glyph([
        (50, -105), (570, -105), (570, -55), (50, -55),
    ]), 620)
    add_glyph(font, "less", ord("<"), polygon_glyph([
        (535, 690), (535, 610), (145, 350), (535, 90),
        (535, 10), (55, 325), (55, 375),
    ]), 620)
    add_glyph(font, "greater", ord(">"), polygon_glyph([
        (85, 690), (565, 375), (565, 325), (85, 10),
        (85, 90), (475, 350), (85, 610),
    ]), 620)
    add_glyph(font, "bracketleft", ord("["), polygon_glyph([
        (150, 690), (520, 690), (520, 625), (230, 625),
        (230, 75), (520, 75), (520, 10), (150, 10),
    ]), 620)
    add_glyph(font, "bracketright", ord("]"), polygon_glyph([
        (100, 690), (470, 690), (470, 10), (100, 10),
        (100, 75), (390, 75), (390, 625), (100, 625),
    ]), 620)

    font.save(path)


if __name__ == "__main__":
    font_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parents[1] / "08-bc10c-paleo-hebrew-tel-zayit.ttf"
    repair(font_path)
