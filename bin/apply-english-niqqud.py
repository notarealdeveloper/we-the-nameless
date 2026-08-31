#!/usr/bin/env python3
"""Apply the documented English-niqqud spellings to Exodus 28--40 P text."""

import argparse
from pathlib import Path
import re
import unicodedata


ROOT = Path(__file__).resolve().parents[1]

# Longest first keeps related words from shadowing one another.  Each spelling
# uses a playful but readable scattering of Hebrew vowel points, with at most
# one point per Latin letter.  Upper points avoid ascenders (b, d, f, h, k, l,
# and t), while lower points avoid descenders (g, j, p, q, and y).  Dotted and
# qamats-like forms predominate over flat marks.  Across the set, every Hebrew
# vowel-point shape is represented; cantillation, dagesh, shin dots, and other
# inner marks are not.
MARKS = {
    "Tent of Meeting": "Teֶnְt of Meֵeִtiַnְg",
    "pomegranates": "poֹmְeֶgraָnaַteֵsְ",
    "breastplate": "breֵaַsְtplaָteֶ",
    "carnelian": "caָrְneֶliִaָnְ",
    "anointing": "aֲnoֹiִnְtiֵng",
    "headdress": "heֶaָdְdreֵsִs",
    "Holiness": "Hoֹliִneֶsְs",
    "amethyst": "aֱmeֶthִysְt",
    "judgment": "juֻdְgmeֶnְt",
    "sapphire": "saַpphiִreֵ",
    "diamond": "diִaָmoֹnְd",
    "jacinth": "jaciִnְth",
    "golden": "goֹlְdeֶnְ",
    "emerald": "eֶmeֵraַlְd",
    "incense": "iִnְceֶnְseֵ",
    "scarlet": "sְcaָrְleֶt",
    "Tummim": "Tuֻmְmiִmְ",
    "holies": "hoֹliִeֵsְ",
    "agate": "aֳgaָteֵ",
    "ephod": "eֶphoֹd",
    "purple": "puֻrְpleֶ",
    "shekel": "sְheֶkeֵlְ",
    "Aaron": "Aaָrֲoֹnְ",
    "jasper": "jasְpeֶrְ",
    "linen": "liִnְeֶnְ",
    "beryl": "beֶrֵylְ",
    "rings": "riִnְgsֵ",
    "topaz": "toֹpaָzְ",
    "onyx": "oֳnְyxֵ",
    "Urim": "Uֻriִmְ",
    "cubit": "cuֻbiִtְ",
    "ruby": "ruֻbְy",
    "Holy": "Hoֹlֵy",
    "holy": "hoֹlֵy",
    "gold": "goֹlְd",
    "blue": "bluֻeֵ",
    "belt": "beֶlְt",
    "bell": "beֶlְl",
    "sash": "saָsְh",
    "glory": "gloֹrֵy",
    "beauty": "beְaׇuֻtֵy",
}

WORDS = tuple(MARKS)

HEBREW_MARKS = r"[\u0591-\u05c7]*"


def decorated_pattern(plain: str) -> str:
    """Match a target spelling with any existing Hebrew marks on its letters."""
    pieces = []
    for character in plain:
        pieces.append(re.escape(character))
        if character.isascii() and character.isalpha():
            pieces.append(HEBREW_MARKS)
    return "".join(pieces)


def mark_p_blocks(text: str) -> str:
    lines = text.splitlines(keepends=True)
    inside = False
    depth = 0
    for index, line in enumerate(lines):
        if not inside and "\\eP{" in line:
            inside = True
            depth = 0
        if inside:
            # Normalize the one-e legacy form emitted by the first draft of this
            # script before applying the canonical two-e spelling.
            line = re.sub(decorated_pattern("Tent of Meting"), "Tent of Meeting", line)
            for plain, marked in MARKS.items():
                line = re.sub(
                    rf"(?<![A-Za-z]){decorated_pattern(plain)}(?![A-Za-z])",
                    plain,
                    line,
                )
            for plain, marked in MARKS.items():
                line = re.sub(rf"(?<![A-Za-z]){re.escape(plain)}(?![A-Za-z])", marked, line)
            depth += line.count("{") - line.count("}")
            lines[index] = line
            if depth == 0:
                inside = False
    return "".join(lines)


def unmark_english_blocks(text: str) -> str:
    """Remove Hebrew marks from English source macros without touching Hebrew."""
    lines = text.splitlines(keepends=True)
    inside = False
    depth = 0
    for index, line in enumerate(lines):
        if not inside and re.search(r"\\e[A-Z]+\{", line):
            inside = True
            depth = 0
        if inside:
            line = "".join(
                char for char in unicodedata.normalize("NFD", line)
                if not 0x0591 <= ord(char) <= 0x05C7
            )
            depth += line.count("{") - line.count("}")
            lines[index] = line
            if depth == 0:
                inside = False
    return "".join(lines)


def update_mapping_table() -> None:
    path = ROOT / "exodus-28-40-p-niqqud-counts.md"
    text = path.read_text()
    heading = "## Niqqud mapping\n"
    prefix, separator, _old_mapping = text.partition(heading)
    if not separator:
        raise ValueError(f"Missing mapping heading in {path}")
    rows = [heading, "| Plain           | Marked |\n", "| --------------- | ------ |\n"]
    for plain in WORDS:
        rows.append(f"| {plain:<15} | {MARKS[plain]} |\n")
    path.write_text(prefix + "".join(rows))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remove", action="store_true", help="remove marks instead of applying them")
    args = parser.parse_args()
    transform = unmark_english_blocks if args.remove else mark_p_blocks
    for chapter in range(28, 41):
        path = ROOT / "02-exodus" / f"{chapter:02}.tex"
        original = path.read_text()
        revised = transform(original)
        if revised != original:
            path.write_text(revised)
    if not args.remove:
        update_mapping_table()


if __name__ == "__main__":
    main()
