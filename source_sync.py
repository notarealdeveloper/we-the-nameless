#!/usr/bin/env python3
"""Audit and update TeX source wrappers from the Tanach.us XML in src/.

The updater intentionally handles only verses with one XML source. Split verses
need translation-aware boundaries and are emitted by the audit for review.
"""

from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).resolve().parent
SOURCE_MAP = {"D1": "DtrA", "D2": "DtrB", "Dn": "Dtn", "O": "Other"}
SOURCE_NAMES = {
    "J", "JP", "JPP", "JE", "E", "EP", "EPP", "P", "PP", "DtrA",
    "DtrB", "DtrH", "Dtn", "R", "Red", "Reblacktor", "RJE", "Records",
    "BookOfRecords", "Other", "X", "Proto", "ProtoA", "ProtoB", "ProtoC",
    "ProtoD", "ProtoE", "ProtoF", "ProtoG",
}


def matching_brace(text: str, opening: int) -> int:
    depth = 0
    commented = False
    for i in range(opening, len(text)):
        char = text[i]
        if commented:
            if char == "\n":
                commented = False
            continue
        if char == "%" and (i == 0 or text[i - 1] != "\\"):
            commented = True
        elif char == "{" and (i == 0 or text[i - 1] != "\\"):
            depth += 1
        elif char == "}" and (i == 0 or text[i - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return i
    raise ValueError(f"unclosed brace at offset {opening}")


def verse_blocks(text: str):
    for match in re.finditer(r"\\Verse\{(\d+)\}", text):
        blocks = []
        cursor = match.end()
        for _ in range(3):
            while cursor < len(text) and text[cursor].isspace():
                cursor += 1
            if cursor >= len(text) or text[cursor] != "{":
                raise ValueError(f"expected verse block after {match.group(0)}")
            end = matching_brace(text, cursor)
            blocks.append((cursor, end))
            cursor = end + 1
        yield int(match.group(1)), blocks


def top_level_wrappers(text: str, start: int, end: int, language: str):
    wrappers = []
    depth = 0
    commented = False
    i = start + 1
    while i < end:
        char = text[i]
        if commented:
            if char == "\n":
                commented = False
            i += 1
            continue
        if char == "%" and text[i - 1] != "\\":
            commented = True
            i += 1
            continue
        if char == "{" and text[i - 1] != "\\":
            depth += 1
        elif char == "}" and text[i - 1] != "\\":
            depth -= 1
        elif char == "\\" and depth == 0:
            match = re.match(rf"\\{language}([A-Za-z]+)(?=\{{)", text[i:])
            if match and match.group(1) in SOURCE_NAMES:
                wrappers.append((i + 2, i + len(match.group(0)), match.group(1)))
                i += len(match.group(0))
                continue
        i += 1
    return wrappers


def xml_sources(path: pathlib.Path):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as error:
        return None, str(error)
    verses = collections.defaultdict(list)
    for verse in root.iter("v"):
        source = verse.get("s")
        if source:
            verses[int(verse.get("n"))].append(SOURCE_MAP.get(source, source))
    return verses, None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    invalid = []
    splits = []
    missing = []
    mismatches = []
    changed_files = 0
    changed_wrappers = 0

    for xml_path in sorted(ROOT.glob("src/0[1-9]-*/*.xml")):
        sources, error = xml_sources(xml_path)
        if error:
            invalid.append((xml_path.relative_to(ROOT), error))
            continue
        tex_path = ROOT / xml_path.relative_to(ROOT / "src").with_suffix(".tex")
        if not tex_path.exists():
            missing.append(str(tex_path.relative_to(ROOT)))
            continue
        text = tex_path.read_text()
        replacements = []
        found = set()
        for number, blocks in verse_blocks(text):
            found.add(number)
            expected = sources.get(number)
            if not expected:
                continue
            if len(expected) > 1:
                actual = []
                for language, block in zip(("h", "e"), blocks[:2]):
                    actual.append([item[2] for item in top_level_wrappers(text, *block, language)])
                splits.append((tex_path.relative_to(ROOT), number, expected, actual))
                continue
            source = expected[0]
            for language, block in zip(("h", "e"), blocks[:2]):
                wrappers = top_level_wrappers(text, *block, language)
                if not wrappers:
                    mismatches.append((tex_path.relative_to(ROOT), number, language, source, []))
                for start, end, actual in wrappers:
                    if actual != source:
                        mismatches.append((tex_path.relative_to(ROOT), number, language, source, [actual]))
                        replacements.append((start, end, source))
        for number in sources.keys() - found:
            missing.append(f"{tex_path.relative_to(ROOT)}:{number}")
        if args.write and replacements:
            for start, end, source in sorted(replacements, reverse=True):
                text = text[:start] + source + text[end:]
            tex_path.write_text(text)
            changed_files += 1
            changed_wrappers += len(replacements)

    print(f"invalid_xml={len(invalid)} missing={len(missing)} split_verses={len(splits)} mismatches={len(mismatches)}")
    if args.write:
        print(f"changed_files={changed_files} changed_wrappers={changed_wrappers}")
    for path, error in invalid:
        print(f"INVALID {path}: {error}")
    for item in missing:
        print(f"MISSING {item}")
    for path, number, expected, actual in splits:
        print(f"SPLIT {path}:{number} XML={','.join(expected)} TEX-H={','.join(actual[0])} TEX-E={','.join(actual[1])}")
    if not args.write:
        for path, number, language, expected, actual in mismatches:
            print(f"DIFF {path}:{number} {language} XML={expected} TEX={','.join(actual)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
