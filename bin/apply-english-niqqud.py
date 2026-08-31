#!/usr/bin/env python3
"""Apply the documented English-niqqud spellings to Exodus 28--40 P text."""

import argparse
from pathlib import Path
import re
import unicodedata


ROOT = Path(__file__).resolve().parents[1]

# Longest first keeps related words from shadowing one another.  These are all
# Hebrew *points*, never cantillation marks.  Descenders get only upper/inner
# points; capitals and tall b/d get only lower points.  Everything else gets
# the typographical equivalent of an entire box of glitter.
WORDS = (
    "Tent of Meeting", "pomegranates", "breastplate", "carnelian",
    "anointing", "headdress", "Holiness", "amethyst", "judgment",
    "sapphire", "diamond", "jacinth", "golden", "emerald", "incense",
    "scarlet", "Tummim", "holies", "agate", "ephod", "purple",
    "shekel", "Aaron", "jasper", "linen", "beryl", "rings", "topaz",
    "onyx", "Urim", "cubit", "ruby", "Holy", "holy", "gold", "blue",
    "belt", "bell", "sash", "glory", "beauty",
)

LOWER_POINTS = "ְֱֲֳִֵֶַָׇֻ"
UPPER_INNER_POINTS = "ֹּׁׂ"
ALL_POINTS = LOWER_POINTS + UPPER_INNER_POINTS


def festoon(word: str) -> str:
    marked = []
    for character in word:
        marked.append(character)
        if not character.isascii() or not character.isalpha():
            continue
        if character in "pg":
            marked.append(UPPER_INNER_POINTS)
        elif character.isupper() or character in "bd":
            marked.append(LOWER_POINTS)
        else:
            marked.append(ALL_POINTS)
    return "".join(marked)


MARKS = {word: festoon(word) for word in WORDS}

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
