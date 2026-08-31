#!/usr/bin/env python3
"""Apply the documented English-niqqud spellings to Exodus 28--40 P text."""

import argparse
from pathlib import Path
import re
import unicodedata


ROOT = Path(__file__).resolve().parents[1]

# Keep these in longest-first order so related words do not shadow one another.
MARKS = {
    "Tent of Meeting": "Tֶ֔e֔n֗t oְ֜f֔ Meֵ֔e֔t֗iִ֗n֔g",
    "pomegranates": "p֜oֹ֜m֙eְ֔g֜r֙aַֽn֔aַֽt֗e֔s",
    "breastplate": "br֙eֶ֔aַֽs֔t֗p֜laֵֽt֗e",
    "carnelian": "c֙aָֽr֙n֔eִ֔liִ֗aְֽn",
    "anointing": "aְֽn֔oֹ֜iִ֗n֔t֗iִ֗n֔g",
    "headdress": "h֗eֶ֔aַֽddr֙eֶ֔s֔s",
    "Holiness": "Hoֹ֜liִ֗n֔eֶ֔s֔s",
    "amethyst": "aַֽm֙eְ֔t֗h֗yִ֗s֔t",
    "judgment": "j֙uָdg֠m֙eֶ֔n֔t",
    "sapphire": "s֔aַֽp֜p֜h֗iִ֗r֙e",
    "diamond": "diַ֗aְֽm֙oֹ֜n֔d",
    "jacinth": "j֙aַֽc֙iִ֗n֔t֗h",
    "golden": "g֜oֹ֜ldeֶ֔n",
    "emerald": "eֶ֔m֙eְ֔r֙aַֽld",
    "incense": "iִ֗n֔c֙eֶ֔n֔s֔e",
    "scarlet": "s֔caַr֙leֶ֔t",
    "Tummim": "Tuֻ֠m֙m֙iִ֗m",
    "holies": "h֗oֹ֜liִ֗eֶ֔s",
    "agate": "aַֽg֜aְֽt֗e",
    "ephod": "e֔p֜h֗oָ֜d",
    "purple": "p֜uֻ֠r֙ple",
    "shekel": "s֔h֗eֶ֔k֔eֶ֔l",
    "Aaron": "Aַaֽr֙oֹ֜n",
    "jasper": "j֙aַֽs֔p֜eְ֔r",
    "linen": "liִ֗n֔eֶ֔n",
    "beryl": "beֶ֔r֙yִ֗l",
    "rings": "r֙iִ֗n֔g֜s",
    "topaz": "t֗oֹ֜p֜aַֽz",
    "onyx": "oָ֜n֔yִּ֗x",
    "Urim": "Ur֙iִ֗m",
    "cubit": "c֙u֠biִ֗t",
    "ruby": "r֙u֠byִ֗",
    "Holy": "Hoֹ֜lyִ֗",
    "holy": "h֗oֹ֜lyִ֗",
    "gold": "g֜oֹ֜ld",
    "blue": "bluֻ֠e",
    "belt": "beֶ֔lt",
    "bell": "beֶ֔ll",
    "sash": "s֔aַֽs֔h",
}

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


if __name__ == "__main__":
    main()
