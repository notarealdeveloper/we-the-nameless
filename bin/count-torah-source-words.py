#!/usr/bin/env python3
"""Count words in the English J, E, and P spans of the numbered Torah chapters."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BOOKS = ("01-genesis", "02-exodus", "03-leviticus", "04-numbers", "05-deuteronomy")
WORD = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)*(?:-[A-Za-z]+(?:['’][A-Za-z]+)*)*")


def strip_comments(text: str) -> str:
    return re.sub(r"(?<!\\)%[^\n]*", "", text)


def braced(text: str, start: int) -> tuple[str, int]:
    """Return a balanced braced argument and the offset following it."""
    assert text[start] == "{"
    depth = 1
    i = start + 1
    while depth:
        if i >= len(text):
            raise ValueError("unclosed brace")
        if text[i] in "{}" and (i == 0 or text[i - 1] != "\\"):
            depth += 1 if text[i] == "{" else -1
        i += 1
    return text[start + 1 : i - 1], i


def optional(text: str, start: int) -> int:
    if start >= len(text) or text[start] != "[":
        return start
    depth = 1
    i = start + 1
    while depth:
        if text[i] == "[":
            depth += 1
        elif text[i] == "]":
            depth -= 1
        i += 1
    return i


def render(text: str) -> str:
    """Reduce the small TeX subset occurring inside the source spans to text."""
    out: list[str] = []
    i = 0
    discard_arg = {"footnote", "heb", "Paleo", "hspace", "vspace"}
    render_arg = {
        "eR", "hlA", "hlB", "hlC", "cR", "cB", "textbf", "textit",
        "textsl", "textsc", "emph", "smash", "hbox", "size",
    }
    declarations = {"scriptsize", "tiny", "footnotesize", "relax"}
    while i < len(text):
        if text[i] != "\\":
            out.append(text[i])
            i += 1
            continue
        match = re.match(r"\\([A-Za-z@]+|.)", text[i:])
        if not match:
            i += 1
            continue
        command = match.group(1)
        i += match.end()
        if command in {"God", "GodInit"}:
            out.append(" God ")
        elif command in {"nl", "par", "mdash"}:
            out.append(" ")
        elif command in {"&", "{", "}"}:
            out.append(command)
        elif command in declarations:
            pass
        elif command in discard_arg and i < len(text) and text[i] == "{":
            _, i = braced(text, i)
            out.append(" ")
        elif command == "genfrac" and i < len(text) and text[i] == "{":
            args = []
            for _ in range(6):
                arg, i = braced(text, i)
                args.append(arg)
            out.extend((render(args[4]), " ", render(args[5])))
        elif command in {"Above", "Below"} and i < len(text) and text[i] == "{":
            _, i = braced(text, i)  # Vertical measurement.
            if i < len(text) and text[i] == "{":
                arg, i = braced(text, i)
                out.append(render(arg))
            if i < len(text) and text[i] == "{":
                _, i = braced(text, i)  # Non-English annotation.
        elif command == "size" and i < len(text) and text[i] == "{":
            _, i = braced(text, i)  # Font measurement.
            if i < len(text) and text[i] == "{":
                arg, i = braced(text, i)
                out.append(render(arg))
        elif command == "raisebox" and i < len(text) and text[i] == "{":
            _, i = braced(text, i)
            i = optional(text, i)
            if i < len(text) and text[i] == "{":
                arg, i = braced(text, i)
                out.append(render(arg))
        elif command == "makebox":
            i = optional(text, i)
            i = optional(text, i)
            if i < len(text) and text[i] == "{":
                arg, i = braced(text, i)
                out.append(render(arg))
        elif command in render_arg and i < len(text) and text[i] == "{":
            arg, i = braced(text, i)
            out.append(render(arg))
        elif i < len(text) and text[i] == "{":
            # Unknown formatting command: retain its visible argument.
            arg, i = braced(text, i)
            out.append(render(arg))
        else:
            out.append(" ")
    return "".join(out)


def spans(text: str, source: str):
    marker = f"\\e{source}{{"
    i = 0
    while (start := text.find(marker, i)) != -1:
        body, end = braced(text, start + len(marker) - 1)
        yield body
        i = end  # Do not count a same-source macro nested within its parent twice.


def main() -> None:
    files = [path for book in BOOKS for path in sorted((ROOT / book).glob("[0-9][0-9].tex"))]
    for source in "JEP":
        counts: Counter[str] = Counter()
        span_count = 0
        for path in files:
            text = strip_comments(path.read_text(encoding="utf-8"))
            for body in spans(text, source):
                span_count += 1
                words = WORD.findall(render(body).replace("’", "'"))
                counts.update(word.lower() for word in words)
        frequencies = dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
        result = {
            "source": source,
            "scope": "Torah numbered chapters (Genesis through Deuteronomy)",
            "chapter_files": len(files),
            "source_spans": span_count,
            "total_words": counts.total(),
            "unique_words": len(counts),
            "tokenization": "lowercase; contractions and hyphenated compounds retained",
            "frequencies": frequencies,
        }
        output = ROOT / f"torah-{source.lower()}-word-frequencies.json"
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
