#!/usr/bin/env -S fontforge -script
"""Build inscription-style Proto-Sinaitic fonts from local SVG drawings."""

from __future__ import annotations

import importlib.util
import os
import re
from importlib.machinery import SourceFileLoader

import fontforge
import psMat


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "fonts-master")
BASE_FONT = os.path.join(FONT_DIR, "04-bc15c-proto-sinaitic-15th-century.ttf")
if not os.path.exists(BASE_FONT):
    BASE_FONT = os.path.join(FONT_DIR, "03-bc15c-proto-sinaitic-15th-century.ttf")

REFERENCE_HEBREW_MEDIAN_HEIGHT = 584
REFERENCE_MAX_SVG_WIDTH = 900
GLYPH_SIDE_BEARING = 60
SPACE_WIDTH = 300
SVG_BASELINE = 90
SVG_SCALE_OVERRIDES = {
    ("02-bc19c-proto-sinaitic-wadi-el-hol-inscription.ttf", "aleph"): 1.18,
}


HEBREW = {
    "aleph": "א",
    "bet": "ב",
    "gimel": "ג",
    "dalet": "ד",
    "he": "ה",
    "waw": "ו",
    "zayin": "ז",
    "heth": "ח",
    "teth": "ט",
    "yod": "י",
    "kaf": "כ",
    "lamed": "ל",
    "mem": "מ",
    "nun": "נ",
    "samekh": "ס",
    "ayin": "ע",
    "pe": "פ",
    "tsade": "צ",
    "qoph": "ק",
    "resh": "ר",
    "shin": "ש",
    "taw": "ת",
}

FINAL_TO_BASE = {
    "ך": "כ",
    "ם": "מ",
    "ן": "נ",
    "ף": "פ",
    "ץ": "צ",
}

GENERIC = {
    "aleph": "fonts-proto-sinaitic-generic/Proto-semiticA-01.svg",
    "gimel": "fonts-proto-sinaitic-generic/Proto-semiticG-01.svg",
    "waw": "fonts-proto-sinaitic-generic/Proto-semiticW-01.svg",
    "zayin": "fonts-proto-sinaitic-generic/Proto-semiticZ-01.svg",
    "heth": "fonts-proto-sinaitic-generic/Proto-semiticHeth.svg",
    "teth": "fonts-proto-sinaitic-generic/Proto-semiticṬ-01.svg",
    "yod": "fonts-proto-sinaitic-generic/Proto-semiticI-02.svg",
    "nun": "fonts-proto-sinaitic-generic/Proto-semiticN-01.svg",
    "ayin": "fonts-proto-sinaitic-generic/Proto-semiticO-01.svg",
    "pe": "fonts-proto-sinaitic-generic/Proto-semiticP-01.svg",
    "qoph": "fonts-proto-sinaitic-generic/Proto-semiticQ-01.svg",
    "taw": "fonts-proto-sinaitic-generic/Proto-semiticT-01.svg",
}

FONTS = [
    {
        "filename": "02-bc19c-proto-sinaitic-wadi-el-hol-inscription.ttf",
        "family": "WTN Proto Sinaitic Wadi el-Hol 19th Century BCE",
        "source": "Wadi el-Hol SVG reconstructions with generic Proto-Semitic and fifteenth-century fallbacks",
        "description": "Inscription-style Proto-Sinaitic font using available Wadi el-Hol SVG letter drawings where present.",
        "svg": {
            "aleph": "fonts-proto-sinaitic-wadi-el-hol/Wadi_el-hol-A02.svg",
            "bet": "fonts-proto-sinaitic-wadi-el-hol/Wadi_el-hol-B.svg",
            "he": "fonts-proto-sinaitic-wadi-el-hol/Wadi_el-hol-H01.svg",
            "mem": "fonts-proto-sinaitic-wadi-el-hol/Wadi_el-hol-M02.svg",
            "nun": "fonts-proto-sinaitic-wadi-el-hol/Wadi_el-hol-N01.svg",
            "ayin": "fonts-proto-sinaitic-wadi-el-hol/Wadi_el-hol-O.svg",
            "pe": "fonts-proto-sinaitic-wadi-el-hol/Wadi_el-hol-P01.svg",
            "resh": "fonts-proto-sinaitic-wadi-el-hol/Wadi_el-hol-R011.svg",
            "shin": "fonts-proto-sinaitic-wadi-el-hol/Wadi_el-hol-Š.svg",
            "taw": "fonts-proto-sinaitic-wadi-el-hol/Wadi_el-hol-T.svg",
        },
    },
    {
        "filename": "03-bc18c-proto-sinaitic-serabit-el-khadim-inscription.ttf",
        "family": "WTN Proto Sinaitic Serabit el-Khadim 18th Century BCE",
        "source": "Serabit el-Khadim SVG reconstructions with generic Proto-Semitic and fifteenth-century fallbacks",
        "description": "Inscription-style Proto-Sinaitic font using available Serabit el-Khadim SVG letter drawings where present.",
        "svg": {
            "bet": "fonts-proto-sinaitic-serabit/Serabit-El-Khadim-B346.svg",
            "dalet": "fonts-proto-sinaitic-serabit/Serabit-El-Khadim-D346.svg",
            "heth": "fonts-proto-sinaitic-serabit/Serabit-El-Khadim-Ḥ362.svg",
            "kaf": "fonts-proto-sinaitic-serabit/Serabit-El-Khadim-K363.svg",
            "lamed": "fonts-proto-sinaitic-serabit/Serabit-El-Khadim-L348.svg",
            "mem": "fonts-proto-sinaitic-serabit/Serabit-El-Khadim-M354.svg",
            "ayin": "fonts-proto-sinaitic-serabit/Serabit-El-Khadim-O346.svg",
            "tsade": "fonts-proto-sinaitic-serabit/Serabit-El-Khadim-Ṣ356.svg",
            "resh": "fonts-proto-sinaitic-serabit/Serabit-El-Khadim-R352.svg",
        },
    },
]


def load_key_map() -> dict[str, str]:
    path = os.path.join(ROOT, "bin", "alphabet")
    spec = importlib.util.spec_from_loader("wtn_alphabet", SourceFileLoader("wtn_alphabet", path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.key_to_hebrew()


KEY_TO_HEBREW = load_key_map()


def ps_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]", "", value)
    return cleaned if not cleaned[:1].isdigit() else f"WTN{cleaned}"


def glyph_name(codepoint: int) -> str:
    return fontforge.nameFromUnicode(codepoint) or f"uni{codepoint:04X}"


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
    dst[dst_code].glyphname = glyph_name(dst_code)
    return True


def import_svg(dst, hebrew_char: str, svg_path: str, extra_scale: float = 1.0) -> None:
    code = ord(hebrew_char)
    glyph = dst.createChar(code)
    glyph.clear()
    glyph.glyphname = glyph_name(code)
    glyph.importOutlines(os.path.join(ROOT, svg_path))
    glyph.removeOverlap()
    glyph.correctDirection()
    xmin, ymin, xmax, ymax = glyph.boundingBox()
    height = ymax - ymin
    width = xmax - xmin
    if height > 0 and width > 0:
        scale = min(
            REFERENCE_HEBREW_MEDIAN_HEIGHT / height,
            REFERENCE_MAX_SVG_WIDTH / width,
        ) * extra_scale
        glyph.transform(psMat.scale(scale))
        glyph.round()
        xmin, ymin, _xmax, _ymax = glyph.boundingBox()
        glyph.transform(psMat.translate(-xmin, SVG_BASELINE - ymin))


def ink_glyphs(font):
    glyphs = []
    for key in KEY_TO_HEBREW:
        code = ord(key)
        if code not in font:
            continue
        glyph = font[code]
        if not glyph.isWorthOutputting():
            continue
        xmin, ymin, xmax, ymax = glyph.boundingBox()
        if xmax - xmin > 1 and ymax - ymin > 1:
            glyphs.append(glyph)
    return glyphs


def median(values: list[float]) -> float:
    values = sorted(values)
    if not values:
        return 0
    mid = len(values) // 2
    return values[mid] if len(values) % 2 else (values[mid - 1] + values[mid]) / 2


def normalize_size_and_spacing(font) -> None:
    glyphs = ink_glyphs(font)
    height = median([g.boundingBox()[3] - g.boundingBox()[1] for g in glyphs])
    if height > 0:
        scale = REFERENCE_HEBREW_MEDIAN_HEIGHT / height
        for glyph in glyphs:
            glyph.transform(psMat.scale(scale))
            glyph.round()

    for glyph in ink_glyphs(font):
        xmin, _ymin, xmax, _ymax = glyph.boundingBox()
        glyph.transform(psMat.translate(GLYPH_SIDE_BEARING - xmin, 0))
        glyph.width = int(round((xmax - xmin) + (2 * GLYPH_SIDE_BEARING)))

    if ord(" ") in font:
        font[ord(" ")].width = SPACE_WIDTH


def apply_metadata(font, spec: dict[str, object]) -> None:
    family = str(spec["family"])
    fullname = family
    font.familyname = family
    font.fullname = fullname
    font.fontname = ps_name(fullname)
    font.weight = "Regular"
    font.version = "1.000"
    font.sfnt_names = (
        ("English (US)", "Family", family),
        ("English (US)", "SubFamily", "Regular"),
        ("English (US)", "UniqueID", f"WTN normalized ancient-script font: {fullname}"),
        ("English (US)", "Fullname", fullname),
        ("English (US)", "PostScriptName", ps_name(fullname)),
        ("English (US)", "Preferred Family", family),
        ("English (US)", "Preferred Styles", "Regular"),
        ("English (US)", "Compatible Full", fullname),
        ("English (US)", "Descriptor", str(spec["description"])),
        ("English (US)", "Designer", str(spec["source"])),
        ("English (US)", "Manufacturer", "We the Nameless"),
    )


def build(spec: dict[str, object]) -> None:
    base = fontforge.open(BASE_FONT)
    font = fontforge.font()
    font.encoding = "UnicodeFull"
    font.em = base.em
    font.ascent = base.ascent
    font.descent = base.descent
    apply_metadata(font, spec)
    font.createChar(ord(" "), "space").width = SPACE_WIDTH

    for hebrew_char in set(KEY_TO_HEBREW.values()):
        source = FINAL_TO_BASE.get(hebrew_char, hebrew_char)
        copy_glyph(base, font, ord(source), ord(hebrew_char))

    svg_map = {**GENERIC, **spec["svg"]}
    for name, svg_path in svg_map.items():
        extra_scale = SVG_SCALE_OVERRIDES.get((str(spec["filename"]), name), 1.0)
        import_svg(font, HEBREW[name], svg_path, extra_scale)

    for final_char, base_char in FINAL_TO_BASE.items():
        copy_glyph(font, font, ord(base_char), ord(final_char))

    for key, hebrew_char in sorted(KEY_TO_HEBREW.items(), key=lambda item: ord(item[0])):
        copy_glyph(font, font, ord(hebrew_char), ord(key))

    normalize_size_and_spacing(font)
    out = os.path.join(FONT_DIR, str(spec["filename"]))
    font.generate(out, flags=("dummy-dsig",))
    font.close()
    base.close()
    print(out)


def main() -> int:
    for spec in FONTS:
        build(spec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
