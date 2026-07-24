#!/usr/bin/env fontforge -script
"""Generate Hebrew-encoded ancient fonts into fonts2/.

The source fonts in fonts/ use several incompatible encodings: Hebrew,
Phoenician, Imperial Aramaic, Ugaritic, Egyptian hieroglyphs, and ASCII
letter slots.  This script copies only the interesting glyph outlines into
fresh fonts whose public encoding is the Hebrew Unicode block.
"""

from __future__ import annotations

import os
import re
import sys

import fontforge
import psMat


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(ROOT, "fonts")
TARGET_DIR = os.path.join(ROOT, "fonts2")

HEBREW_SCALE_REFERENCE = 2.66

HEBREW = [
    0x05D0, 0x05D1, 0x05D2, 0x05D3, 0x05D4, 0x05D5, 0x05D6, 0x05D7,
    0x05D8, 0x05D9, 0x05DB, 0x05DC, 0x05DE, 0x05E0, 0x05E1, 0x05E2,
    0x05E4, 0x05E6, 0x05E7, 0x05E8, 0x05E9, 0x05EA,
]

FINALS = {
    0x05DA: 0x05DB,
    0x05DD: 0x05DE,
    0x05DF: 0x05E0,
    0x05E3: 0x05E4,
    0x05E5: 0x05E6,
}

ASCII_UPPER = "ABGDHWZXJYKLMNS]PCQRVT"
ASCII_LOWER = "abgdhwzxjyklmns]pcqrvt"

PROTO_A_LOWER = ["a", "b", "g", "d", "h", "w", "Z", "x", "j", "y", "k", "l", "m", "n", "s", "]", "p", "c", "q", "r", "f", "t"]
PROTO_A_UPPER = ["A", "B", "G", "D", "H", "W", "Z", "X", "j", "Y", "K", "L", "M", "N", "S", "]", "P", "C", "Q", "R", "V", "T"]
PROTO_B_LOWER = ["a", "b", "g", "d", "H", "W", "z", "x", "j", "y", "k", "l", "M", "n", "s", "]", "p", "c", "q", "r", "v", "t"]
PROTO_B_UPPER = ["A", "B", "G", "D", "h", "w", "Z", "X", "J", "Y", "K", "L", "M", "N", "S", "]", "P", "C", "Q", "R", "V", "T"]
PROTO_C_UPPER = ["A", "B", "G", "D", "H", "W", "Z", "X", "J", "Y", "K", "L", None, "N", "S", "]", "P", "C", "Q", "R", "V", "T"]
PROTO_C_LOWER = ["a", "b", "g", "d", "h", "w", "z", "x", "j", "y", "k", "l", None, "n", "s", "]", "p", "c", "q", "R", "v", "t"]
PALEO_B_UPPER = ["A", "B", "G", "D", "H", "W", "Z", "X", None, "Y", "K", "L", "M", None, "S", "]", "P", "C", "Q", "R", "V", "T"]
PALEO_B_LOWER = ["a", "b", "g", "d", "h", "w", "z", "x", None, "y", "k", "l", "m", None, "s", "]", "p", "c", "q", "r", "v", "t"]

PHOENICIAN = "𐤀𐤁𐤂𐤃𐤄𐤅𐤆𐤇𐤈𐤉𐤊𐤋𐤌𐤍𐤎𐤏𐤐𐤑𐤒𐤓𐤔𐤕"
ARAMAIC = "𐡀𐡁𐡂𐡃𐡄𐡅𐡆𐡇𐡈𐡉𐡊𐡋𐡌𐡍𐡎𐡏𐡐𐡑𐡒𐡓𐡔𐡕"
UGARITIC = "𐎀𐎁𐎂𐎄𐎅𐎆𐎇𐎈𐎉𐎊𐎋𐎍𐎎𐎐𐎒𐎓𐎔𐎕𐎖𐎗𐎌𐎚"
EGYPTIAN = "𓃾𓉐𓌙𓆟𓀠𓌉𓏭𓉗𓄤𓂝𓂧𓍢𓈖𓆓𓊽𓁹𓂋𓇑𓎗𓁶𓌔𓏴"


def variant(chars) -> dict[int, int | None]:
    if len(chars) != len(HEBREW):
        raise ValueError(f"variant has {len(chars)} glyphs; expected {len(HEBREW)}: {chars!r}")
    mapping = {dst: (None if src is None else ord(src)) for dst, src in zip(HEBREW, chars)}
    for final, normal in FINALS.items():
        mapping[final] = mapping[normal]
    return mapping


def blank_glyph(dst, dst_code: int, width: int = 300) -> None:
    glyph = dst.createChar(dst_code)
    glyph.glyphname = f"uni{dst_code:04X}"
    glyph.width = width


def family_from_filename(filename: str) -> str:
    return os.path.splitext(os.path.basename(filename))[0]


def ps_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", name)


def copy_glyph(src, dst, src_code: int, dst_code: int, scale: float) -> bool:
    if src_code == ord("]") and (src_code not in src or not src[src_code].isWorthOutputting()):
        src_code = ord("[")

    if src_code not in src or not src[src_code].isWorthOutputting():
        return False

    src.selection.none()
    src.selection.select(("unicode",), src_code)
    src.copy()

    glyph = dst.createChar(dst_code)
    dst.selection.none()
    dst.selection.select(("unicode",), dst_code)
    dst.paste()

    glyph = dst[dst_code]
    glyph.glyphname = f"uni{dst_code:04X}"
    glyph.transform(psMat.scale(scale))
    glyph.width = int(round(glyph.width * scale))
    glyph.removeOverlap()
    glyph.simplify()
    return True


def build_font(spec: dict[str, object]) -> list[str]:
    source_path = os.path.join(SOURCE_DIR, str(spec["source"]))
    output_name = str(spec["output"])
    output_path = os.path.join(TARGET_DIR, output_name)
    family = family_from_filename(output_name)
    scale = float(spec["scale"]) / HEBREW_SCALE_REFERENCE

    src = fontforge.open(source_path)
    dst = fontforge.font()
    dst.encoding = "UnicodeFull"
    dst.em = 1000
    dst.ascent = 800
    dst.descent = 200
    dst.familyname = family
    dst.fullname = family
    dst.fontname = ps_name(family)
    dst.weight = "Regular"
    dst.copyright = src.copyright
    dst.version = "1.000"
    dst.appendSFNTName("English (US)", "Family", family)
    dst.appendSFNTName("English (US)", "Fullname", family)
    dst.appendSFNTName("English (US)", "PostScriptName", ps_name(family))
    dst.appendSFNTName("English (US)", "SubFamily", "Regular")
    dst.appendSFNTName("English (US)", "Preferred Family", family)
    dst.appendSFNTName("English (US)", "Preferred Styles", "Regular")
    dst.appendSFNTName("English (US)", "Compatible Full", family)

    copy_scale = (1000.0 / float(src.em)) * scale
    missing = []
    blank_width = int(round(450 * scale))
    for dst_code, src_code in dict(spec["mapping"]).items():
        if src_code is None:
            blank_glyph(dst, dst_code, blank_width)
        elif not copy_glyph(src, dst, src_code, dst_code, copy_scale):
            missing.append(f"U+{src_code:04X}->U+{dst_code:04X}")

    dst.os2_typoascent = 800
    dst.os2_typodescent = -200
    dst.os2_winascent = 900
    dst.os2_windescent = 300
    dst.generate(output_path, flags=("dummy-dsig",))
    dst.close()
    src.close()
    return missing


SPECS = [
    {"source": "egyptian-hieroglyphs-regular-noto-sans.ttf", "output": "egyptian-hieroglyphs-regular-noto-sans.ttf", "scale": 2.13, "mapping": variant(EGYPTIAN)},
    {"source": "noto-sans-imperial-aramaic-regular.ttf", "output": "noto-sans-imperial-aramaic-regular.ttf", "scale": 2.13, "mapping": variant(ARAMAIC)},
    {"source": "noto-sans-ugaritic-regular.ttf", "output": "noto-sans-ugaritic-regular.ttf", "scale": 2.13, "mapping": variant(UGARITIC)},
    {"source": "paleo-hebrew-phoenician.ttf", "output": "paleo-hebrew-phoenician.ttf", "scale": 2.13, "mapping": variant(PHOENICIAN)},
    {"source": "paleo-hebrew-robo.ttf", "output": "paleo-hebrew-robo.ttf", "scale": 1.81, "mapping": variant("".join(chr(c) for c in HEBREW))},
    {"source": "paleo-hebrew-mono.ttf", "output": "paleo-hebrew-mono.ttf", "scale": 1.81, "mapping": variant("".join(chr(c) for c in HEBREW))},
    {"source": "proto-sinaitic-best.ttf", "output": "proto-sinaitic-best.ttf", "scale": 1.81, "mapping": variant("".join(chr(c) for c in HEBREW))},
    {"source": "proto-sinaitic-best-bold.ttf", "output": "proto-sinaitic-best-bold.ttf", "scale": 1.81, "mapping": variant("".join(chr(c) for c in HEBREW))},
    {"source": "proto-sinaitic-other.ttf", "output": "proto-sinaitic-other-upper.ttf", "scale": 1.81, "mapping": variant(ASCII_UPPER)},
    {"source": "proto-sinaitic-other.ttf", "output": "proto-sinaitic-other-lower.ttf", "scale": 1.81, "mapping": variant(ASCII_LOWER)},
    {"source": "proto-sinaitic-15.ttf", "output": "proto-sinaitic-15-lower.ttf", "scale": 1.43, "mapping": variant(PROTO_A_LOWER)},
    {"source": "proto-sinaitic-15.ttf", "output": "proto-sinaitic-15-upper.ttf", "scale": 1.43, "mapping": variant(PROTO_A_UPPER)},
    {"source": "proto-sinaitic-13.ttf", "output": "proto-sinaitic-13-lower.ttf", "scale": 1.82, "mapping": variant(PROTO_B_LOWER)},
    {"source": "proto-sinaitic-13.ttf", "output": "proto-sinaitic-13-upper.ttf", "scale": 1.82, "mapping": variant(PROTO_B_UPPER)},
    {"source": "proto-sinaitic-13-izbet-sartah.ttf", "output": "proto-sinaitic-13-izbet-sartah-upper.ttf", "scale": 1.81, "mapping": variant(PROTO_C_UPPER)},
    {"source": "proto-sinaitic-13-izbet-sartah.ttf", "output": "proto-sinaitic-13-izbet-sartah-lower.ttf", "scale": 1.81, "mapping": variant(PROTO_C_LOWER)},
    {"source": "paleo-hebrew-tel-zayit.ttf", "output": "paleo-hebrew-tel-zayit.ttf", "scale": 1.81, "mapping": variant(ASCII_LOWER)},
    {"source": "paleo-hebrew-gezer.ttf", "output": "paleo-hebrew-gezer-upper.ttf", "scale": 1.82, "mapping": variant(PALEO_B_UPPER)},
    {"source": "paleo-hebrew-gezer.ttf", "output": "paleo-hebrew-gezer-lower.ttf", "scale": 1.82, "mapping": variant(PALEO_B_LOWER)},
    {"source": "paleo-hebrew-tel-dan.ttf", "output": "paleo-hebrew-tel-dan-upper.ttf", "scale": 1.82, "mapping": variant(ASCII_UPPER)},
    {"source": "paleo-hebrew-tel-dan.ttf", "output": "paleo-hebrew-tel-dan-lower.ttf", "scale": 1.82, "mapping": variant(ASCII_LOWER)},
    {"source": "paleo-hebrew-moabite.ttf", "output": "paleo-hebrew-moabite-upper.ttf", "scale": 1.81, "mapping": variant(ASCII_UPPER)},
    {"source": "paleo-hebrew-moabite.ttf", "output": "paleo-hebrew-moabite-lower.ttf", "scale": 1.81, "mapping": variant(ASCII_LOWER)},
    {"source": "paleo-hebrew.ttf", "output": "paleo-hebrew-upper.ttf", "scale": 1.81, "mapping": variant(ASCII_UPPER)},
    {"source": "paleo-hebrew.ttf", "output": "paleo-hebrew-lower.ttf", "scale": 1.81, "mapping": variant(ASCII_LOWER)},
    {"source": "paleo-hebrew-other.ttf", "output": "paleo-hebrew-other.ttf", "scale": 1.81, "mapping": variant("".join(chr(c) for c in HEBREW))},
    {"source": "paleo-hebrew-siloam.ttf", "output": "paleo-hebrew-siloam-upper.ttf", "scale": 1.81, "mapping": variant(ASCII_UPPER)},
    {"source": "paleo-hebrew-siloam.ttf", "output": "paleo-hebrew-siloam-lower.ttf", "scale": 1.81, "mapping": variant(ASCII_LOWER)},
    {"source": "paleo-hebrew-ketef-hinnom-1.ttf", "output": "paleo-hebrew-ketef-hinnom-1-upper.ttf", "scale": 1.82, "mapping": variant(ASCII_UPPER)},
    {"source": "paleo-hebrew-ketef-hinnom-1.ttf", "output": "paleo-hebrew-ketef-hinnom-1-lower.ttf", "scale": 1.82, "mapping": variant(ASCII_LOWER)},
    {"source": "paleo-hebrew-ketef-hinnom-2.ttf", "output": "paleo-hebrew-ketef-hinnom-2-upper.ttf", "scale": 1.82, "mapping": variant(ASCII_UPPER)},
    {"source": "paleo-hebrew-ketef-hinnom-2.ttf", "output": "paleo-hebrew-ketef-hinnom-2-lower.ttf", "scale": 1.82, "mapping": variant(ASCII_LOWER)},
    {"source": "paleo-hebrew-lachish-3.ttf", "output": "paleo-hebrew-lachish-3.ttf", "scale": 1.81, "mapping": variant(ASCII_UPPER)},
    {"source": "paleo-hebrew-lachish-4.ttf", "output": "paleo-hebrew-lachish-4.ttf", "scale": 1.81, "mapping": variant(ASCII_UPPER)},
    {"source": "paleo-hebrew-lachish-5.ttf", "output": "paleo-hebrew-lachish-5.ttf", "scale": 1.82, "mapping": variant(ASCII_UPPER)},
    {"source": "dead-sea-scrolls-isaiah.ttf", "output": "dead-sea-scrolls-isaiah-upper.ttf", "scale": 1.81, "mapping": variant(ASCII_UPPER)},
    {"source": "dead-sea-scrolls-isaiah.ttf", "output": "dead-sea-scrolls-isaiah-lower.ttf", "scale": 1.81, "mapping": variant(ASCII_LOWER)},
]


def main() -> int:
    os.makedirs(TARGET_DIR, exist_ok=True)
    for name in os.listdir(TARGET_DIR):
        if name.endswith((".ttf", ".otf")):
            os.remove(os.path.join(TARGET_DIR, name))

    failures = {}
    for spec in SPECS:
        output = spec["output"]
        print(f"building {output}")
        missing = build_font(spec)
        if missing:
            failures[output] = missing

    if failures:
        for output, missing in failures.items():
            print(f"{output}: missing {', '.join(missing)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
