#!/usr/bin/env python3
"""Build a reflowable Kindle-compatible EPUB from the WTN TeX sources."""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
MASTER = ROOT / "master.tex"
OUTPUT = HERE / "we-the-nameless.epub"

SOURCE_NAMES = {
    "J": "J", "E": "E", "P": "P", "R": "R", "X": "Other",
    "JE": "JE", "JP": "JP", "JM": "JM", "JPP": "JPP", "PR": "PR",
    "RJE": "RJE", "Dtn": "Dtn", "DtrA": "Dtr A", "DtrB": "Dtr B",
    "DtrH": "Dtr H", "Proto": "Proto", "ProtoA": "Proto A",
    "ProtoF": "Proto F", "Other": "Other", "BookOfRecords": "Book of Records",
}

COMMENTARY = {"aA": "aside-a", "aAc": "aside-a", "aB": "aside-b",
              "aBr": "aside-b", "aC": "aside-c", "aP": "aside-p",
              "aR": "aside-r", "cB": "aside-b", "cR": "aside-r"}

INLINE = {
    "textbf": "strong", "bf": "strong", "emph": "em", "textit": "em",
    "textsl": "em", "textsc": "span", "texttt": "code", "heb": "span",
    "paleo": "span", "Paleo": "span", "Def": "dfn", "redacted": "span",
    "sout": "s", "textsuperscript": "sup", "path": "code", "href": "a",
}


def log(message: str) -> None:
    """Print a build status message immediately."""
    print(f"[ebook] {message}", flush=True)


def strip_comments(text: str) -> str:
    return re.sub(r"(?<!\\)%[^\n]*", "", text)


def group(text: str, pos: int) -> tuple[str, int] | None:
    while pos < len(text) and text[pos].isspace():
        pos += 1
    if pos >= len(text) or text[pos] != "{":
        return None
    depth, start, i = 1, pos + 1, pos + 1
    while i < len(text) and depth:
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    if depth:
        raise ValueError("unbalanced TeX group")
    return text[start:i - 1], i


def command_at(text: str, pos: int) -> tuple[str, int] | None:
    if text[pos] != "\\":
        return None
    match = re.match(r"\\([A-Za-z@]+|.)", text[pos:])
    return (match.group(1), pos + len(match.group(0))) if match else None


def source_class(name: str) -> tuple[str, str] | None:
    if len(name) < 2 or name[0] not in "he":
        return None
    key = name[1:]
    if key not in SOURCE_NAMES:
        return None
    return ("hebrew" if name[0] == "h" else "english", key)


def tex_to_markdown(text: str) -> str:
    """Conservatively retain prose while translating semantic TeX markup."""
    text = strip_comments(text).replace("~", "\u00a0")
    out: list[str] = []
    i = 0
    while i < len(text):
        if text.startswith("\\begin{", i):
            env = group(text, i + 6)
            if env:
                name, i = env
                if name in {"quote", "quotation"}:
                    out.append("\n\n> ")
                elif name in {"enumerate", "itemize"}:
                    out.append("\n\n")
                elif name in {"center", "flushleft", "flushright", "table", "tabular", "tabularx"}:
                    # Layout environments have no ebook analogue; keep their text.
                    out.append("\n\n")
                continue
        if text.startswith("\\end{", i):
            env = group(text, i + 4)
            if env:
                _, i = env
                out.append("\n\n")
                continue
        if text[i] != "\\":
            out.append(text[i])
            i += 1
            continue
        cmd_data = command_at(text, i)
        if not cmd_data:
            out.append(text[i]); i += 1; continue
        name, after = cmd_data
        if name in {"nl", "linebreak", "par", "medskip", "newpage", "clearpage", "pagebreak"}:
            out.append("  \n" if name in {"nl", "linebreak"} else "\n\n")
            i = after; continue
        if name == "item":
            out.append("\n- "); i = after; continue
        if name in {"mdash", "textemdash"}:
            out.append("—"); i = after; continue
        if name in {"ndash", "textendash"}:
            out.append("–"); i = after; continue
        if name in {"hfill", "noindent", "centering", "raggedbottom", "RaggedRight",
                    "relax", "leavevmode", "sloppy", "tiny", "scriptsize", "footnotesize",
                    "small", "large", "Large", "bfseries", "ttfamily", "selectfont"}:
            i = after; continue
        arg = group(text, after)
        if not arg:
            # Preserve common escaped punctuation; discard purely presentational commands.
            out.append({"%": "%", "&": "&", "_": "_", "#": "#", "{": "{", "}": "}"}.get(name, ""))
            i = after; continue
        body, end = arg
        rendered = tex_to_markdown(body).strip()
        src = source_class(name)
        if name in {"hP", "eP"}:
            lang = ' lang="he" dir="rtl"' if name == "hP" else ""
            cls = "hebrew-line" if name == "hP" else "english-line"
            out.append(f'\n\n<span class="{cls}"{lang}>{rendered}</span>\n\n')
        elif src:
            language, key = src
            attrs = ' lang="he" dir="rtl"' if language == "hebrew" else ""
            label = html.escape(SOURCE_NAMES[key])
            out.append(f'<span class="source source-{key.lower()} {language}"{attrs} data-source="{label}">{rendered}</span>')
        elif name in COMMENTARY:
            out.append(f'\n\n::: {{.{COMMENTARY[name]}}}\n{rendered}\n:::\n\n')
        elif name == "footnote" or name in {"recursivefootnote", "hangingfootnote"}:
            out.append(f"^[{rendered}]")
        elif name == "href":
            second = group(text, end)
            if second:
                label, end = second
                out.append(f"[{tex_to_markdown(label).strip()}]({body})")
            else:
                out.append(body)
        elif name in INLINE:
            tag = INLINE[name]
            attrs = ""
            if name == "heb": attrs = ' class="hebrew" lang="he" dir="rtl"'
            elif name == "paleo" or name == "Paleo": attrs = ' class="paleo" dir="rtl"'
            elif name == "textsc": attrs = ' class="smallcaps"'
            elif name == "redacted": attrs = ' class="redacted"'
            out.append(f"<{tag}{attrs}>{rendered}</{tag}>")
        elif name in {"includegraphics", "image"}:
            path = body.strip()
            if (ROOT / path).exists():
                out.append(f"\n\n![Illustration]({path})\n\n")
        elif name in {"Chapter", "Verse", "Book", "BookPart"}:
            out.append(rendered)
        else:
            # Unknown semantic wrappers are unwrapped, never silently dropping their prose.
            out.append(rendered)
        i = end
    result = "".join(out)
    result = re.sub(r"[ \t]+\n", "\n", result)
    result = re.sub(r"\n{4,}", "\n\n\n", result)
    return result.strip()


def parse_verses(text: str) -> list[tuple[str, str, str, str]]:
    text = strip_comments(text)
    verses = []
    pos = 0
    while True:
        match = re.search(r"\\Verse\s*", text[pos:])
        if not match:
            break
        cursor = pos + match.end()
        args = []
        for _ in range(4):
            parsed = group(text, cursor)
            if not parsed:
                break
            value, cursor = parsed
            args.append(value)
        if len(args) == 4:
            verses.append(tuple(args))
            pos = cursor
        else:
            pos += match.end()
    return verses


def master_sequence(selected_book: str | None = None) -> list[tuple[str, str]]:
    body = MASTER.read_text(encoding="utf-8").split("\\begin{document}", 1)[1]
    sequence: list[tuple[str, str]] = []
    current_book = ""
    current_part = ""
    for line in body.splitlines():
        m = re.match(r"\\Book\{([^}]+)\}", line)
        if m:
            current_book, current_part = m.group(1), ""
            continue
        m = re.match(r"\\BookPart\{([^}]+)\}", line)
        if m:
            current_part = m.group(1)
            continue
        m = re.match(r"\\include\{([^}]+)\}", line)
        if m:
            path = ROOT / f"{m.group(1)}.tex"
            if (selected_book is None or current_book == selected_book) and path.exists() and path.name != "apocrypha.tex":
                label = current_part or current_book
                sequence.append((label, str(path.relative_to(ROOT))))
    return sequence


def make_markdown(path: Path, selected_book: str | None = None) -> tuple[int, int]:
    lines = ["---", 'title: "We The Nameless"', "lang: en-US", "---", "",
             '# We The Nameless {.title-page}', "", "*The bible is weirder than you remember.*", ""]
    last_book = None
    chapter_count = verse_count = 0
    for book, rel in master_sequence(selected_book):
        source = (ROOT / rel).read_text(encoding="utf-8")
        chapter_match = re.search(r"\\Chapter\s*\{([^}]+)\}", strip_comments(source))
        chapter = chapter_match.group(1).strip() if chapter_match else Path(rel).stem
        if book != last_book:
            lines += [f"# {book} {{.book-title}}", ""]
            last_book = book
        anchor = re.sub(r"[^a-z0-9]+", "-", f"{book}-{chapter}".lower()).strip("-")
        lines += [f"## {book} {chapter} {{#{anchor} .chapter-title}}", ""]
        chapter_count += 1
        for number, hebrew, english, commentary in parse_verses(source):
            verse_count += 1
            verse_anchor = f"{anchor}-{re.sub(r'[^a-zA-Z0-9]+', '-', number).strip('-')}"
            lines += [f'::: {{.verse #{verse_anchor}}}', f'### {number} {{.verse-number}}',
                      '::: {.hebrew-block lang="he" dir="rtl"}', tex_to_markdown(hebrew), ":::",
                      "::: {.english-block}", tex_to_markdown(english), ":::"]
            rendered_commentary = tex_to_markdown(commentary)
            if rendered_commentary:
                lines += ["::: {.commentary}", rendered_commentary, ":::"]
            lines += [":::", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return chapter_count, verse_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--book", help="build only the named top-level \\Book from master.tex")
    parser.add_argument("--keep-markdown", action="store_true")
    args = parser.parse_args()
    if not shutil.which("pandoc"):
        parser.error("pandoc is required")
    started = time.monotonic()
    pandoc = shutil.which("pandoc")
    log(f"Starting EPUB build: {args.output}")
    log(f"Source document: {MASTER}")
    log(f"Pandoc: {pandoc}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="wtn-ebook-") as temp:
        manuscript = Path(temp) / "manuscript.md"
        sequence = master_sequence(args.book)
        if args.book and not sequence:
            parser.error(f"book not found or contains no source files: {args.book}")
        source_count = len(sequence)
        log(f"Generating Markdown from {source_count} included TeX files...")
        chapters, verses = make_markdown(manuscript, args.book)
        manuscript_size = manuscript.stat().st_size
        log(
            f"Generated {manuscript_size:,}-byte manuscript "
            f"({chapters} chapters, {verses} verses)"
        )
        if args.keep_markdown:
            kept_manuscript = HERE / "manuscript.generated.md"
            shutil.copy2(manuscript, kept_manuscript)
            log(f"Saved generated Markdown: {kept_manuscript}")
        cmd = ["pandoc", str(manuscript), "--from=markdown+fenced_divs+footnotes",
               "--to=epub3", "--output", str(args.output), "--standalone",
               "--toc", "--toc-depth=2", "--split-level=2", "--css", str(HERE / "epub.css"),
               "--metadata-file", str(HERE / "metadata.yaml")]
        cover = ROOT / "img/covers/we-cover-2.png"
        if cover.exists():
            cmd += ["--epub-cover-image", str(cover)]
            log(f"Using cover image: {cover}")
        else:
            log(f"Cover image not found; building without it: {cover}")
        log("Running Pandoc to package EPUB 3...")
        subprocess.run(cmd, cwd=ROOT, check=True)
    output_size = args.output.stat().st_size
    elapsed = time.monotonic() - started
    log(
        f"Built {args.output} ({output_size:,} bytes, {chapters} chapters, "
        f"{verses} verses) in {elapsed:.1f}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
