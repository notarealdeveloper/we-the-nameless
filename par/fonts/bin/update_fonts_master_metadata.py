#!/usr/bin/env -S fontforge -script
"""Apply chronology.tsv filenames and font metadata to fonts-master/.

The manifest is the data layer.  This script only enforces it: each row's
current_name is renamed to new_name, and each generated font receives stable
fontconfig-friendly family metadata.
"""

from __future__ import annotations

import csv
import os
import re
import sys

import fontforge


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "fonts-master")
MANIFEST = os.path.join(FONT_DIR, "chronology.tsv")
METADATA_IDS = {
    "Family",
    "SubFamily",
    "UniqueID",
    "Fullname",
    "PostScriptName",
    "Preferred Family",
    "Preferred Styles",
    "Compatible Full",
    "Descriptor",
    "Designer",
    "Manufacturer",
    "Vendor URL",
    "License",
    "License URL",
}


def ps_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]", "", value)
    if cleaned and cleaned[0].isdigit():
        cleaned = "WTN" + cleaned
    return cleaned


def read_manifest() -> list[dict[str, str]]:
    with open(MANIFEST, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sfnt_names(font, row: dict[str, str]) -> tuple[tuple[str, str, str], ...]:
    family = row["family"]
    style = row["style"] or "Regular"
    fullname = family if style == "Regular" else f"{family} {style}"
    postscript = ps_name(fullname)
    unique_id = f"WTN normalized ancient-script font: {fullname}"
    source = row["source"]
    description = row["description"]
    if source:
        description = f"{description} Source: {source}."

    preserved = [
        entry for entry in font.sfnt_names
        if len(entry) == 3 and entry[1] not in METADATA_IDS
    ]
    generated = [
        ("English (US)", "Family", family),
        ("English (US)", "SubFamily", style),
        ("English (US)", "UniqueID", unique_id),
        ("English (US)", "Fullname", fullname),
        ("English (US)", "PostScriptName", postscript),
        ("English (US)", "Preferred Family", family),
        ("English (US)", "Preferred Styles", style),
        ("English (US)", "Compatible Full", fullname),
        ("English (US)", "Descriptor", description),
        ("English (US)", "Designer", source),
        ("English (US)", "Manufacturer", "We the Nameless"),
        ("English (US)", "Vendor URL", "https://www.bibleplaces.com/paleo_hebrew_fonts"),
        ("English (US)", "License", "Metadata and encoding normalized for We the Nameless; original font license and copyright retained where present."),
    ]
    return tuple(preserved + generated)


def apply_row(row: dict[str, str]) -> str:
    current = row["current_name"]
    new = row["new_name"]
    current_path = os.path.join(FONT_DIR, current)
    new_path = os.path.join(FONT_DIR, new)
    source_path = current_path if os.path.exists(current_path) else new_path
    renamed = source_path == current_path and current_path != new_path
    if not os.path.exists(source_path):
        return f"missing {current} / {new}"

    family = row["family"]
    style = row["style"] or "Regular"
    fullname = family if style == "Regular" else f"{family} {style}"

    font = fontforge.open(source_path)
    font.encoding = "UnicodeFull"
    font.familyname = family
    font.fullname = fullname
    font.fontname = ps_name(fullname)
    font.weight = style
    font.version = font.version or "1.000"
    font.sfnt_names = sfnt_names(font, row)

    tmp_path = new_path + ".tmp"
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    font.generate(tmp_path, flags=("dummy-dsig",))
    font.close()

    os.replace(tmp_path, new_path)
    if current_path != new_path and os.path.exists(current_path):
        os.remove(current_path)
    if renamed:
        return f"{current} -> {new}: {fullname}"
    return f"{new}: {fullname}"


def main() -> int:
    if not os.path.isdir(FONT_DIR):
        print(f"missing {FONT_DIR}", file=sys.stderr)
        return 1
    if not os.path.exists(MANIFEST):
        print(f"missing {MANIFEST}", file=sys.stderr)
        return 1

    status = 0
    for row in read_manifest():
        result = apply_row(row)
        print(result)
        if result.startswith("missing "):
            status = 1
    return status


if __name__ == "__main__":
    raise SystemExit(main())
