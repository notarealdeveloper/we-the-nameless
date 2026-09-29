#!/usr/bin/env python3
"""Add corpus-derived Hebrew correspondences to lexical tables in the report.

The mapping is learned with IBM Model 1 from the source-aligned Hebrew/English
spans in the project's Torah TeX files.  It is therefore a correspondence in
this particular translation, not a claim that every English type has one
dictionary-equivalent Hebrew lemma.
"""
from __future__ import annotations

import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pkg/yhwh/src"))

from yhwh import TORAH_BOOKS, load  # noqa: E402
from yhwh.normalize import strip_niqqud  # noqa: E402

REPORT = Path(__file__).with_name("friedman_torah_jep_word_analysis.md")
SOURCES = {"J", "E", "P"}
EDGE = "'\"“”‘’.,;:!?()[]{}<>—–…"
MORPHOLOGY = {
    "and": "וְ־",
    "i'll": "אֶ־",
    "my": "־ִי",
    "of": "—",
    "shall": "—",
    "the": "הַ־",
    "their": "־ָם / ־ֶן",
    "its": "־וֹ / ־ָהּ",
    "you'll": "תִּ־",
}


def english_tokens(text: str) -> list[str]:
    text = text.replace("’", "'").replace("‘", "'")
    return [token.strip(EDGE).lower() for token in text.split() if token.strip(EDGE)]


def hebrew_tokens(text: str) -> list[tuple[str, str]]:
    out = []
    for raw in text.split():
        vocalized = raw.strip(EDGE + "־")
        consonantal = strip_niqqud(vocalized)
        consonantal = re.sub(r"[^\u05d0-\u05ea]", "", consonantal)
        if consonantal:
            out.append((consonantal, vocalized))
    return out


def training_pairs():
    corpus = load(ROOT)
    pairs = []
    spellings: dict[str, Counter[str]] = defaultdict(Counter)
    for verse in corpus.subset(TORAH_BOOKS):
        hebrew_by_source: dict[str, list[tuple[str, str]]] = defaultdict(list)
        english_by_source: dict[str, list[str]] = defaultdict(list)
        for span in verse.hebrew_spans:
            if span.source in SOURCES:
                hebrew_by_source[span.source].extend(hebrew_tokens(span.text))
        for span in verse.english_spans:
            if span.source in SOURCES:
                english_by_source[span.source].extend(english_tokens(span.text))
        for source in SOURCES:
            hs = hebrew_by_source[source]
            es = english_by_source[source]
            if not hs or not es:
                continue
            for consonantal, vocalized in hs:
                spellings[consonantal][vocalized] += 1
            pairs.append((list(dict.fromkeys(es)), list(dict.fromkeys(h for h, _ in hs))))
    return pairs, spellings


def report_words(text: str) -> set[str]:
    return set(re.findall(r"^\| `([^`]+)`\s*\|", text, re.M))


def learn(words: set[str], iterations: int = 8):
    pairs, spellings = training_pairs()
    candidates: dict[str, set[str]] = defaultdict(set)
    for es, hs in pairs:
        for e in es:
            if e in words:
                candidates[e].update(hs)
    probabilities = {
        e: {h: 1.0 / len(hs) for h in hs}
        for e, hs in candidates.items() if hs
    }
    for _ in range(iterations):
        counts: dict[str, Counter[str]] = defaultdict(Counter)
        totals: Counter[str] = Counter()
        for es, hs in pairs:
            wanted = [e for e in es if e in probabilities]
            if not wanted:
                continue
            for h in hs:
                denominator = sum(probabilities[e].get(h, 0.0) for e in wanted)
                if not denominator:
                    continue
                for e in wanted:
                    contribution = probabilities[e].get(h, 0.0) / denominator
                    if contribution:
                        counts[e][h] += contribution
                        totals[e] += contribution
        for e, hs in counts.items():
            probabilities[e] = {h: value / totals[e] for h, value in hs.items()}
    mapping = {}
    for e, hs in probabilities.items():
        ranked = sorted(hs, key=hs.get, reverse=True)
        # Diffuse alignments are normally English auxiliaries/articles whose
        # information is distributed through Hebrew morphology, not a word.
        if hs[ranked[0]] < 0.06:
            mapping[e] = "—"
            continue
        # One clear form is preferable; preserve alternatives when the model's
        # probability remains substantial because English often merges forms.
        chosen = [ranked[0]]
        for h in ranked[1:]:
            if len(chosen) == 3 or hs[h] < hs[ranked[0]] * 0.38:
                break
            chosen.append(h)
        rendered = []
        for h in chosen:
            rendered.append(spellings[h].most_common(1)[0][0] if spellings[h] else h)
        mapping[e] = " / ".join(rendered)
    mapping.update({word: form for word, form in MORPHOLOGY.items() if word in words})
    return mapping


def add_column(text: str, mapping: dict[str, str]) -> str:
    lines = text.splitlines()
    in_lexical_table = False
    for i, line in enumerate(lines):
        if line.startswith("| word") and "Hebrew" not in line:
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            cells.insert(1, "Hebrew")
            lines[i] = "| " + " | ".join(cells) + " |"
            in_lexical_table = True
            continue
        if in_lexical_table and re.match(r"^\|\s*:?-+", line):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            cells.insert(1, ":---:")
            lines[i] = "| " + " | ".join(cells) + " |"
            continue
        match = re.match(r"^\|\s*`([^`]+)`\s*\|", line) if in_lexical_table else None
        if match:
            word = match.group(1)
            lines[i] = re.sub(
                r"^(\|\s*`[^`]+`\s*\|)",
                rf"\1 `{mapping.get(word, '—')}` |",
                line,
                count=1,
            )
            continue
        if in_lexical_table and not line.startswith("|"):
            in_lexical_table = False
    note = (
        "Hebrew cells give the leading vocalized surface-form correspondence(s) "
        "learned from the source-aligned Torah text. They are translation-specific "
        "statistical alignments, not necessarily lexicon headwords; `/` marks strong alternatives."
    )
    marker = "## Strongest discrepancies in the entire corpus"
    lines.insert(lines.index(marker) + 1, "\n" + note)
    return "\n".join(lines) + "\n"


def main():
    text = REPORT.read_text(encoding="utf8")
    mapping = learn(report_words(text))
    if "| word | Hebrew |" in text:
        text = re.sub(
            r"^(\|\s*`([^`]+)`\s*\|)\s*`[^`]*`\s*\|",
            lambda m: f"{m.group(1)} `{mapping.get(m.group(2), '—')}` |",
            text,
            flags=re.M,
        )
        REPORT.write_text(text, encoding="utf8")
    else:
        REPORT.write_text(add_column(text, mapping), encoding="utf8")


if __name__ == "__main__":
    main()
