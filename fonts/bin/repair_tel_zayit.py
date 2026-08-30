#!/usr/bin/env python3
"""Repair the ASCII glyph map and punctuation in the Tel Zayit font."""

from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont


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


def repair(path: Path, mesha_path: Path) -> None:
    font = TTFont(path)
    mesha = TTFont(mesha_path)

    # Ayin is encoded as O/o by master.tex. Use the nearby Mesha Stele hand
    # instead of the conspicuously geometric ring formerly drawn here.
    for glyph_name in ("O", "o"):
        font["glyf"][glyph_name] = deepcopy(mesha["glyf"][glyph_name])
        font["hmtx"][glyph_name] = mesha["hmtx"][glyph_name]

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
    # Plain, narrow ASCII brackets. Tel Zayit's letters sit unusually high in
    # its em square, so position the brackets here rather than compensating in
    # document markup.
    add_glyph(font, "bracketleft", ord("["), polygon_glyph([
        (70, 880), (265, 880), (265, 825), (130, 825),
        (130, 140), (265, 140), (265, 85), (70, 85),
    ]), 335)
    add_glyph(font, "bracketright", ord("]"), polygon_glyph([
        (70, 880), (265, 880), (265, 85), (70, 85),
        (70, 140), (205, 140), (205, 825), (70, 825),
    ]), 335)

    font.save(path)


if __name__ == "__main__":
    font_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parents[1] / "08-bc10c-paleo-hebrew-tel-zayit.ttf"
    mesha_path = Path(__file__).parents[1] / "09-bc09c-paleo-hebrew-mesha-stele-a.ttf"
    repair(font_path, mesha_path)
