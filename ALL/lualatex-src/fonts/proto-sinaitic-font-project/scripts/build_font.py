#!/usr/bin/env fontforge
# Run with:
#   fontforge -quiet -script scripts/build_font.py glyph_map.tsv glyphs dist/ProtoSinaiticLocal.ttf

import csv
import os
import sys

import fontforge

EM = 1000
ASCENT = 800
DESCENT = 200


def die(msg):
    print("error:", msg, file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) != 4:
        die("usage: fontforge -script build_font.py glyph_map.tsv glyphs output.ttf")

    map_path, glyph_dir, out_path = sys.argv[1:]

    font = fontforge.font()
    font.fontname = "ProtoSinaiticLocal"
    font.familyname = "Proto Sinaitic Local"
    font.fullname = "Proto Sinaitic Local"
    font.encoding = "UnicodeFull"
    font.em = EM
    font.ascent = ASCENT
    font.descent = DESCENT
    font.copyright = "Generated locally from user-provided SVG glyphs."
    font.version = "0.1"

    rows = []
    with open(map_path, newline="", encoding="utf-8") as f:
        for row in csv.reader(f, delimiter="\t"):
            if not row or row[0].startswith("#"):
                continue
            if len(row) < 3:
                die("bad row in glyph_map.tsv: " + repr(row))
            rows.append(row)

    for row in rows:
        name, hex_cp, svg_file = row[0], row[1], row[2]
        cp = int(hex_cp, 16)
        svg_path = os.path.join(glyph_dir, svg_file)
        if not os.path.exists(svg_path):
            die("missing SVG: " + svg_path)

        glyph = font.createChar(cp, name)
        glyph.importOutlines(svg_path)
        glyph.removeOverlap()
        glyph.correctDirection()
        glyph.width = 900

        # Normalize roughly into the em square.
        glyph.transform((1, 0, 0, 1, 0, 0))
        bbox = glyph.boundingBox()
        xmin, ymin, xmax, ymax = bbox
        w = xmax - xmin
        h = ymax - ymin
        if w > 0 and h > 0:
            scale = min(700.0 / w, 700.0 / h)
            glyph.transform((scale, 0, 0, scale, 0, 0))
            xmin, ymin, xmax, ymax = glyph.boundingBox()
            x_shift = (900 - (xmax - xmin)) / 2 - xmin
            y_shift = 100 - ymin
            glyph.transform((1, 0, 0, 1, x_shift, y_shift))

    # Basic metadata for Linux font menus.
    font.appendSFNTName("English (US)", "Family", "Proto Sinaitic Local")
    font.appendSFNTName("English (US)", "SubFamily", "Regular")
    font.appendSFNTName("English (US)", "Fullname", "Proto Sinaitic Local")
    font.appendSFNTName("English (US)", "Preferred Family", "Proto Sinaitic Local")
    font.appendSFNTName("English (US)", "Preferred Styles", "Regular")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    font.generate(out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
