#!/usr/bin/env fontforge
"""Split phoenician-alphabet.svg and build a Hebrew-encoded TrueType font."""

from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

import fontforge
import psMat


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "phoenician-alphabet.svg"
GLYPH_DIR = ROOT / "phoenician-alphabet-letters"
FONT = ROOT / "phoenician-alphabet-hebrew.ttf"
NS = "{http://www.w3.org/2000/svg}"

# Source paths run top-to-bottom in each column. The Unicode code points omit
# the five Hebrew final forms; those are added below as references.
LETTERS = [
    ("alef", "א", 0x05D0), ("bet", "ב", 0x05D1),
    ("gimel", "ג", 0x05D2), ("dalet", "ד", 0x05D3),
    ("he", "ה", 0x05D4), ("vav", "ו", 0x05D5),
    ("zayin", "ז", 0x05D6), ("het", "ח", 0x05D7),
    ("tet", "ט", 0x05D8), ("yod", "י", 0x05D9),
    ("kaf", "כ", 0x05DB), ("lamed", "ל", 0x05DC),
    ("mem", "מ", 0x05DE), ("nun", "נ", 0x05E0),
    ("samekh", "ס", 0x05E1), ("ayin", "ע", 0x05E2),
    ("pe", "פ", 0x05E4), ("tsadi", "צ", 0x05E6),
    ("qof", "ק", 0x05E7), ("resh", "ר", 0x05E8),
    ("shin", "ש", 0x05E9), ("tav", "ת", 0x05EA),
]
FINALS = [(0x05DA, 0x05DB), (0x05DD, 0x05DE), (0x05DF, 0x05E0),
          (0x05E3, 0x05E4), (0x05E5, 0x05E6)]


def split_svg():
    tree = ET.parse(SOURCE)
    root = tree.getroot()
    columns = []
    for group in root.findall(f"{NS}g"):
        paths = group.findall(f"{NS}path")
        if not paths:
            continue
        match = re.search(r"translate\(([-0-9.]+)", group.get("transform", ""))
        tx = float(match.group(1)) if match else 0.0
        entries = []
        for path in paths:
            nums = [float(x) for x in re.findall(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", path.get("d"))]
            # Every path starts with an absolute moveto; its y is enough to
            # restore the deliberately reversed source ordering.
            entries.append((nums[1], path.get("d"), tx))
        columns.append(sorted(entries))

    paths = columns[0] + columns[1] + columns[2]
    if len(paths) != 22:
        raise RuntimeError(f"expected 22 letter paths, found {len(paths)}")

    GLYPH_DIR.mkdir(exist_ok=True)
    outputs = []
    for (name, hebrew, codepoint), (_, data, tx) in zip(LETTERS, paths):
        # Start with a generous canvas, query the actual vector bounds, then
        # emit a padded tight viewBox. The path data itself is untouched.
        output = GLYPH_DIR / f"{codepoint:04X}-{name}.svg"
        temp = GLYPH_DIR / f".{name}.svg"
        temp.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="700" '
            'viewBox="0 0 1000 700">'
            f'<path id="letter" transform="translate({tx} 0)" d="{data}"/>'
            '</svg>\n', encoding="utf-8")
        query = subprocess.check_output(
            ["inkscape", "--query-id=letter", "--query-x", "--query-y",
             "--query-width", "--query-height", str(temp)], text=True)
        x, y, width, height = map(float, query.splitlines())
        pad = 3.0
        output.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width + 2*pad:.6g}" height="{height + 2*pad:.6g}" '
            f'viewBox="{x-pad:.6g} {y-pad:.6g} {width+2*pad:.6g} {height+2*pad:.6g}">\n'
            f'  <title>{name} ({hebrew})</title>\n'
            f'  <path transform="translate({tx:g} 0)" d="{data}"/>\n'
            '</svg>\n', encoding="utf-8")
        temp.unlink()
        outputs.append((output, x, y, width, height))
    return outputs


def build_font(images):
    font = fontforge.font()
    font.encoding = "UnicodeFull"
    font.em = 1000
    font.ascent = 800
    font.descent = 200
    font.fontname = "PhoenicianAlphabetHebrew"
    font.familyname = "Phoenician Alphabet Hebrew"
    font.fullname = "Phoenician Alphabet Hebrew Regular"
    font.weight = "Regular"
    font.version = "1.0"
    font.copyright = "Glyph outlines reproduced exactly from phoenician-alphabet.svg"

    # All source units receive the same scale. The typical 60-unit source
    # letter becomes 600 font units high, seated on the shared baseline.
    baseline = 0
    sidebearing = 70
    source_scale = 10.0
    for (name, _, codepoint), (image, _, _, _, source_height) in zip(LETTERS, images):
        glyph = font.createChar(codepoint, name)
        glyph.importOutlines(str(image))
        bounds = glyph.boundingBox()
        imported_height = bounds[3] - bounds[1]
        glyph.transform(psMat.scale(source_height * source_scale / imported_height))
        bounds = glyph.boundingBox()
        glyph.transform(psMat.translate(sidebearing - bounds[0], baseline - bounds[1]))
        bounds = glyph.boundingBox()
        glyph.width = int(round(bounds[2] + sidebearing))
        glyph.correctDirection()

    for final_codepoint, base_codepoint in FINALS:
        final = font.createChar(final_codepoint)
        final.addReference(font[base_codepoint].glyphname)
        final.width = font[base_codepoint].width

    font.selection.all()
    font.autoHint()
    font.generate(str(FONT), flags=("opentype", "dummy-dsig"))
    font.close()


if __name__ == "__main__":
    build_font(split_svg())
