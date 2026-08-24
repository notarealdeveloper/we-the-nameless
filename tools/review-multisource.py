#!/usr/bin/env python3
"""One-off, non-destructive reviewer for MULTI-SOURCE-VERSES.

Phase one only: inventory verses, record candidate seams, and persist review
decisions.  It deliberately does not rewrite TeX.  An apply mode should only be
added after every accepted decision has token anchors and preservation tests.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
METADATA = ROOT / "MULTI-SOURCE-VERSES"
DECISIONS = ROOT / "MULTI-SOURCE-DECISIONS.json"
REPORT = ROOT / "MULTI-SOURCE-REPORT.md"

BOOK_FILES = {
    "Gen": ("Genesis", ROOT / "01-genesis"),
    "Exod": ("Exodus", ROOT / "02-exodus"),
}

ENTRY_RE = re.compile(
    r"^(?P<book>\S+) (?P<chapter>\d+):(?P<first>\d+)"
    r"(?:[–-](?P<last>\d+))?: (?P<sources>.+)$"
)
SOURCE_RE = re.compile(r"\\([he])(J|E|P|RJE|R|Other|BookOfRecords)\{")

# Directly visible in the screenshot evidence supplied with the task.  Values
# identify the first token of the next source; they are proposals, not silent
# approvals.  Repeated-token cases use the full following phrase.
SCREENSHOT_SEAMS = {
    "Gen 2:4": [("בְּיוֹם", "in the day")],
    "Gen 6:9": [("נֹחַ אִישׁ", "Noah was")],
    "Gen 7:16": [("וַיִּסְגֹּר", "And YHWH closed")],
    "Gen 8:2": [("וַיִּכָּלֵא", "and the rain was")],
    "Gen 8:3": [("וַיַּחְסְרוּ", "and the water receded")],
    "Gen 8:13": [("וַיָּסַר", "And Noah turned")],
    "Gen 10:1": [("וַיִּוָּלְדוּ", "And children were")],
    "Gen 37:2": [("יוֹסֵף בֶּן", "Joseph, at")],
    "Gen 37:3": [("וְעָשָׂה", "And he made")],
}


def matching_brace(text: str, opening: int) -> int:
    depth = 0
    escaped = False
    for i in range(opening, len(text)):
        ch = text[i]
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
    raise ValueError(f"unclosed brace at offset {opening}")


def brace_groups_after(text: str, offset: int, count: int = 3) -> list[str]:
    groups: list[str] = []
    cursor = offset
    while len(groups) < count:
        opening = text.find("{", cursor)
        if opening < 0:
            break
        closing = matching_brace(text, opening)
        groups.append(text[opening + 1 : closing])
        cursor = closing + 1
    return groups


def strip_source_wrappers(text: str) -> str:
    """Remove only source wrapper names/braces, retaining nested TeX verbatim."""
    while True:
        match = SOURCE_RE.search(text)
        if not match:
            return text
        opening = match.end() - 1
        closing = matching_brace(text, opening)
        text = text[: match.start()] + text[opening + 1 : closing] + text[closing + 1 :]


def visible_text(text: str) -> str:
    text = strip_source_wrappers(text)
    text = re.sub(r"(?m)%.*$", "", text)
    text = re.sub(r"\\(?:nl|par)\b", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def source_sequence(text: str, language: str) -> list[str]:
    return [m.group(2) for m in SOURCE_RE.finditer(text) if m.group(1) == language]


def load_targets() -> list[dict]:
    targets: list[dict] = []
    for line_no, raw in enumerate(METADATA.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        match = ENTRY_RE.fullmatch(line)
        if not match:
            raise SystemExit(f"{METADATA}:{line_no}: cannot parse {line!r}")
        item = match.groupdict()
        targets.append({
            "reference": f"{item['book']} {item['chapter']}:{item['first']}"
            + (f"–{item['last']}" if item["last"] else ""),
            "book": item["book"],
            "chapter": int(item["chapter"]),
            "first": int(item["first"]),
            "last": int(item["last"] or item["first"]),
            "is_range": item["last"] is not None,
            "sources": item["sources"].split(","),
        })
    return targets


def read_verse(book: str, chapter: int, verse: int) -> dict:
    if book not in BOOK_FILES:
        raise KeyError(f"unsupported book abbreviation: {book}")
    book_name, directory = BOOK_FILES[book]
    path = directory / f"{chapter:02d}.tex"
    text = path.read_text(encoding="utf-8")
    marker = re.search(rf"(?m)^\\Verse\{{{verse}\}}\s*$", text)
    if not marker:
        raise KeyError(f"{path}: \\Verse{{{verse}}} not found")
    groups = brace_groups_after(text, marker.end(), 3)
    if len(groups) < 2:
        raise ValueError(f"{path}: verse {verse} lacks Hebrew/English groups")
    return {
        "reference": f"{book} {chapter}:{verse}",
        "book_name": book_name,
        "path": str(path.relative_to(ROOT)),
        "hebrew_raw": groups[0],
        "english_raw": groups[1],
        "hebrew": visible_text(groups[0]),
        "english": visible_text(groups[1]),
        "current_hebrew_sources": source_sequence(groups[0], "h"),
        "current_english_sources": source_sequence(groups[1], "e"),
    }


def inventory() -> list[dict]:
    rows: list[dict] = []
    for target in load_targets():
        if target["is_range"]:
            rows.append({**target, "status": "range-requires-interpretation"})
            continue
        verse = read_verse(target["book"], target["chapter"], target["first"])
        rows.append({**target, **verse, "status": "unreviewed"})
    return rows


def load_decisions() -> dict:
    if not DECISIONS.exists():
        return {"schema_version": 1, "reference_system": {}, "verses": {}}
    return json.loads(DECISIONS.read_text(encoding="utf-8"))


def save_decisions(data: dict) -> None:
    tmp = DECISIONS.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(DECISIONS)


def numbered(text: str) -> str:
    return "\n".join(f"{i:>3} {token}" for i, token in enumerate(text.split(), 1))


def seam(text: str, positions: list[int]) -> str:
    words = text.split()
    out: list[str] = []
    for i, word in enumerate(words, 1):
        if i - 1 in positions:
            out.append("|")
        out.append(word)
    if len(words) in positions:
        out.append("|")
    return " ".join(out)


def boundary_before(text: str, phrase: str) -> int:
    words = text.split()
    wanted = phrase.split()
    hits = [i for i in range(len(words)) if words[i : i + len(wanted)] == wanted]
    if len(hits) != 1:
        raise ValueError(f"expected one occurrence of {phrase!r}, found {len(hits)}")
    return hits[0]


def screenshot_proposal(row: dict) -> dict | None:
    evidence = SCREENSHOT_SEAMS.get(row["reference"])
    if not evidence:
        return None
    hb = [boundary_before(row["hebrew"], h) for h, _ in evidence]
    eb = [boundary_before(row["english"], e) for _, e in evidence]
    ht, et = row["hebrew"].split(), row["english"].split()
    return {
        "sources": row["sources"],
        "hebrew_boundaries": hb,
        "english_boundaries": eb,
        "hebrew_anchors": [{"after": ht[x - 1], "before": ht[x]} for x in hb],
        "english_anchors": [{"after": et[x - 1], "before": et[x]} for x in eb],
        "confidence": "HIGH",
        "evidence": "source-colored reference screenshot supplied in task prompt",
        "status": "proposed-high",
        "confirmed_by_user": False,
    }


def manual_review(row: dict, saved: dict) -> dict:
    required = " -> ".join(row["sources"])
    print("=" * 72)
    print(f"{row['book_name']} {row['chapter']}:{row['first']}")
    print(f"Required: {required}")
    print(f"Current Hebrew: {' -> '.join(row['current_hebrew_sources']) or '(none)'}")
    print(f"Current English: {' -> '.join(row['current_english_sources']) or '(none)'}")
    print("\nHEBREW TOKENS\n" + numbered(row["hebrew"]))
    print("\nENGLISH TOKENS\n" + numbered(row["english"]))
    old = saved.get(row["reference"], {})
    if old.get("hebrew_boundaries"):
        print("\nSaved Hebrew seam:\n" + seam(row["hebrew"], old["hebrew_boundaries"]))
    if old.get("english_boundaries"):
        print("\nSaved English seam:\n" + seam(row["english"], old["english_boundaries"]))
    print("\nEnter comma-separated token counts AFTER which each seam occurs.")
    print("Commands: s skip, q save and quit, Enter keep existing")
    h = input("Hebrew boundaries: ").strip()
    if h == "q":
        raise KeyboardInterrupt
    if h == "s":
        return {**old, "sources": row["sources"], "status": "skipped"}
    e = input("English boundaries: ").strip()
    if e == "q":
        raise KeyboardInterrupt
    needed = len(row["sources"]) - 1
    hb = old.get("hebrew_boundaries", []) if not h else [int(x) for x in h.split(",")]
    eb = old.get("english_boundaries", []) if not e else [int(x) for x in e.split(",")]
    if len(hb) != needed or len(eb) != needed:
        print(f"Not saved: exactly {needed} Hebrew and English boundaries required.")
        return old
    ht = row["hebrew"].split()
    et = row["english"].split()
    if any(x <= 0 or x >= len(ht) for x in hb) or any(x <= 0 or x >= len(et) for x in eb):
        print("Not saved: seams must be internal token boundaries.")
        return old
    print("\nHEBREW:\n" + seam(row["hebrew"], hb))
    print("\nENGLISH:\n" + seam(row["english"], eb))
    if input("Confirm [y/N]? ").strip().lower() != "y":
        return old
    return {
        "sources": row["sources"],
        "hebrew_boundaries": hb,
        "english_boundaries": eb,
        "hebrew_anchors": [
            {"after": ht[x - 1], "before": ht[x]} for x in hb
        ],
        "english_anchors": [
            {"after": et[x - 1], "before": et[x]} for x in eb
        ],
        "confidence": "manual",
        "evidence": "user-reviewed token boundary",
        "status": "confirmed",
        "confirmed_by_user": True,
    }


def write_report(rows: list[dict], decisions: dict) -> None:
    lines = [
        "# Multi-source verse dry-run report",
        "",
        "> Phase One only. No TeX source has been modified.",
        "",
        "Reference system: Richard Elliott Friedman, *The Bible with Sources Revealed*. "
        "Canonical Hebrew boundary data should be imported from the Tanach.us Friedman-based DH XML.",
        "",
        "| Reference | Required | Current H | Current E | Review |",
        "|---|---|---|---|---|",
    ]
    saved = decisions.get("verses", {})
    for row in rows:
        decision = saved.get(row["reference"], {})
        if row["is_range"]:
            current_h = current_e = "—"
        else:
            current_h = " → ".join(row["current_hebrew_sources"])
            current_e = " → ".join(row["current_english_sources"])
        lines.append(
            f"| {row['reference']} | {' → '.join(row['sources'])} | {current_h} | "
            f"{current_e} | {decision.get('status', row['status'])} |"
        )
    lines += ["", "## Blocking evidence gaps", "",
        "- `Gen 11:10–26` is a range whose meaning must be established from the reference before editing.",
        "- Unconfirmed word-level seams remain intentionally unresolved.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_research() -> None:
    rows = inventory()
    decisions = load_decisions()
    decisions["reference_system"] = {
        "primary": "Richard Elliott Friedman, The Bible with Sources Revealed (2003)",
        "hebrew_machine_readable": "https://tanach.us/DH/DHSpecification.Genesis.xml",
        "note": "Tanach.us states that its intra-verse DH markings resolve WWB ambiguities using BSR.",
    }
    for row in rows:
        proposal = None if row["is_range"] else screenshot_proposal(row)
        existing = decisions["verses"].get(row["reference"])
        if proposal and (not existing or existing.get("status") == "unreviewed"):
            decisions["verses"][row["reference"]] = proposal
        elif not existing:
            decisions["verses"][row["reference"]] = {
                "sources": row["sources"], "status": row["status"]
            }
    save_decisions(decisions)
    write_report(rows, decisions)
    print(f"Inventoried {len(rows)} metadata entries.")
    print(f"Wrote {DECISIONS.relative_to(ROOT)} and {REPORT.relative_to(ROOT)}.")


def cmd_review() -> None:
    rows = [r for r in inventory() if not r["is_range"]]
    decisions = load_decisions()
    try:
        for row in rows:
            if decisions["verses"].get(row["reference"], {}).get("status") == "confirmed":
                continue
            decisions["verses"][row["reference"]] = manual_review(row, decisions["verses"])
            save_decisions(decisions)
    except (KeyboardInterrupt, EOFError):
        print("\nSaved. Review can be resumed.")
    write_report(inventory(), decisions)


def cmd_check() -> None:
    rows = inventory()
    decisions = load_decisions().get("verses", {})
    confirmed = skipped = unresolved = 0
    for row in rows:
        status = decisions.get(row["reference"], {}).get("status", row["status"])
        confirmed += status == "confirmed"
        skipped += status == "skipped"
        unresolved += status not in {"confirmed", "skipped"}
    print(f"entries={len(rows)} confirmed={confirmed} skipped={skipped} unresolved={unresolved}")
    if unresolved:
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("research", "review", "check"))
    args = parser.parse_args()
    {"research": cmd_research, "review": cmd_review, "check": cmd_check}[args.mode]()


if __name__ == "__main__":
    main()
