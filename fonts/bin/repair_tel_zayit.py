#!/usr/bin/env python3
"""Repair the ASCII glyph map in the chronological Tel Zayit font."""

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


def repair(path: Path) -> None:
    font = TTFont(path)

    # Ayin is encoded as O/o by master.tex. Both glyph slots get the same ring.
    for glyph_name in ("O", "o"):
        font["glyf"][glyph_name] = circle_glyph()
        font["hmtx"][glyph_name] = (620, 60)

    # This face stores He at Y/y. Point H/h there too, replacing the Heth map.
    for table in font["cmap"].tables:
        if ord("H") in table.cmap and ord("h") in table.cmap:
            table.cmap[ord("H")] = "Y"
            table.cmap[ord("h")] = "y"

    font.save(path)


if __name__ == "__main__":
    font_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parents[1] / "08-bc10c-paleo-hebrew-tel-zayit.ttf"
    repair(font_path)
