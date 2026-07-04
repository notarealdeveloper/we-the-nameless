#!/usr/bin/env -S fontforge -script
"""Rename fonts-ascii/ files and internal font names from chronology.tsv."""

from __future__ import annotations

import csv
import os
import re
import sys

import fontforge


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "fonts-ascii")
MANIFEST = os.path.join(FONT_DIR, "chronology.tsv")

FAMILY_NAME_IDS = {
    "Family",
    "Fullname",
    "PostScriptName",
    "SubFamily",
    "Preferred Family",
    "Preferred Styles",
    "Compatible Full",
    "UniqueID",
}


def ps_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", name)


def read_manifest() -> list[dict[str, str]]:
    with open(MANIFEST, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def new_sfnt_names(font, family: str) -> tuple[tuple[str, str, str], ...]:
    preserved = [
        row for row in font.sfnt_names
        if len(row) == 3 and row[1] not in FAMILY_NAME_IDS
    ]
    postscript = ps_name(family)
    return tuple(preserved + [
        ("English (US)", "Family", family),
        ("English (US)", "SubFamily", "Regular"),
        ("English (US)", "UniqueID", f"FontForge 2.0 : {family}"),
        ("English (US)", "Fullname", family),
        ("English (US)", "PostScriptName", postscript),
        ("English (US)", "Preferred Family", family),
        ("English (US)", "Preferred Styles", "Regular"),
        ("English (US)", "Compatible Full", family),
    ])


def rename_font(old_name: str, new_name: str) -> str:
    old_path = os.path.join(FONT_DIR, old_name)
    new_path = os.path.join(FONT_DIR, new_name)
    source_path = old_path if os.path.exists(old_path) else new_path
    if not os.path.exists(source_path):
        return f"missing {old_name}"

    family = os.path.splitext(new_name)[0]
    font = fontforge.open(source_path)
    font.familyname = family
    font.fullname = family
    font.fontname = ps_name(family)
    font.weight = font.weight or "Regular"
    font.sfnt_names = new_sfnt_names(font, family)

    tmp_path = new_path + ".tmp.ttf"
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    font.generate(tmp_path, flags=("opentype", "dummy-dsig"))
    font.close()

    os.replace(tmp_path, new_path)
    if old_path != new_path and os.path.exists(old_path):
        os.remove(old_path)
    return f"{old_name} -> {new_name}"


def main() -> int:
    if not os.path.isdir(FONT_DIR):
        print(f"missing {FONT_DIR}; run tools/asciify_fonts2.py first", file=sys.stderr)
        return 1
    if not os.path.exists(MANIFEST):
        print(f"missing {MANIFEST}", file=sys.stderr)
        return 1

    status = 0
    for row in read_manifest():
        result = rename_font(row["old_name"], row["new_name"])
        print(result)
        if result.startswith("missing "):
            status = 1
    return status


if __name__ == "__main__":
    raise SystemExit(main())
