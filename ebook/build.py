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
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
MASTER = ROOT / "master.tex"
OUTPUT = HERE / "we-the-nameless.epub"

# Fonts used by master.tex.  Pandoc embeds these in the EPUB so the design does
# not depend on whichever fonts happen to be installed on the reading device.
FONT_FILES = [
    ROOT / "fonts/hebrew-david.ttf",
    ROOT / "fonts/hebrew-david-bold.ttf",
    ROOT / "fonts/hebrew-ezra.ttf",
    ROOT / "fonts/paleo-hebrew-phoenician.ttf",
    ROOT / "fonts/paleo-hebrew.ttf",
    ROOT / "fonts/paleo-hebrew-siloam.ttf",
    ROOT / "fonts/paleo-hebrew-mono.ttf",
    ROOT / "fonts/english-im-fell-english-sc-regular.ttf",
]


def system_font(command: str, *args: str) -> Path | None:
    executable = shutil.which(command)
    if not executable:
        return None
    result = subprocess.run([executable, *args], text=True, capture_output=True, check=False)
    path = Path(result.stdout.splitlines()[0]) if result.stdout.strip() else None
    return path if path and path.is_file() else None


for discovered_font in (
    system_font("fc-match", "FreeSerif", "-f", "%{file}\n"),
    system_font("fc-match", "FreeSerif:style=Bold", "-f", "%{file}\n"),
    system_font("fc-match", "FreeSerif:style=Italic", "-f", "%{file}\n"),
    system_font("fc-match", "FreeSerif:style=Bold Italic", "-f", "%{file}\n"),
    system_font("kpsewhich", "lmroman10-regular.otf"),
):
    if discovered_font and discovered_font not in FONT_FILES:
        FONT_FILES.append(discovered_font)

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

HEBREW_ORDER = "אבגדהוזחטיכךלמםנןסעפףצץקרשת"
PALEO_ASCII = "ABGDHWZXJYKKLMMNNS]PPC CQRVT".replace(" ", "")
PHOENICIAN = "𐤀𐤁𐤂𐤃𐤄𐤅𐤆𐤇𐤈𐤉𐤊𐤊𐤋𐤌𐤌𐤍𐤍𐤎𐤏𐤐𐤐𐤑𐤑𐤒𐤓𐤔𐤕"
PALEO_ASCII_TABLE = str.maketrans(HEBREW_ORDER, PALEO_ASCII)
PHOENICIAN_TABLE = str.maketrans(HEBREW_ORDER, PHOENICIAN)


def historical_hebrew(text: str, key: str) -> str:
    """Apply the same broad Hebrew encodings as master.tex's source profiles."""
    text = "".join(char for char in text if not unicodedata.combining(char))
    if key == "J":
        return text.translate(PHOENICIAN_TABLE)
    if key in {"E", "JE", "RJE", "BookOfRecords", "Other"} or key.startswith("Proto"):
        return text.translate(PALEO_ASCII_TABLE)
    return text


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
            if language == "hebrew":
                rendered = historical_hebrew(rendered, key)
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


def front_matter(sequence: list[tuple[str, str]]) -> list[str]:
    """Reproduce the visible front matter from master.tex in reflowable form."""
    books = list(dict.fromkeys(book for book, _ in sequence))
    contents = "\n".join(
        f'<li><a href="#{re.sub(r"[^a-z0-9]+", "-", book.lower()).strip("-")}">{html.escape(book)}</a></li>'
        for book in books
    )
    return [
        '<section class="wtn-title-page" epub:type="titlepage">',
        '<div class="title-we">We</div>',
        '<div class="title-nameless">The Nameless</div>',
        '</section>', "",
        '# The Alphabet {.front-heading .alphabet-heading}', "",
        '<div class="alphabet-page" dir="rtl">',
        '<p class="alphabet paleo">𐤀𐤁𐤂𐤃𐤄𐤅𐤆𐤇𐤈𐤉𐤊𐤋𐤌𐤍𐤎𐤏𐤐𐤑𐤒𐤓𐤔𐤕</p>',
        '<p class="alphabet hebrew-david">אבגדהוזחטיכלמנסעפצקרשת</p>',
        '<p class="alphabet hebrew-ezra">אֲבֱגֶּדֲהֹוּזֻחִטֳיִּכֻלֵּמֱנָסֶעֲפֹצֻקָרֶשְּׁתֽ</p>',
        '</div>', "",
        '# Contents {.front-heading}', "", f'<ol class="contents-list">{contents}</ol>', "",
        '# The Authors {.front-heading}', "",
        '<p class="authors-subtitle"><em>or</em><br/><span>We: The Nameless</span></p>',
        '<p class="legend-key"><span class="source source-j">J</span> &nbsp; '
        '<span class="source source-e">E</span> &nbsp; '
        '<span class="source source-p">P</span> &nbsp; '
        '<span class="source source-r">R</span></p>',
        '<dl class="source-legend">',
        '<dt class="source source-j">Green</dt><dd class="source source-j">J. The first author of the bible. The first author of prose in history. The author of the most widely known bible stories. The author of the bible with the best sense of human nature. We have little knowledge of the author’s identity beyond this.</dd>',
        '<dt class="source source-e">Yellow</dt><dd class="source source-e">Mushites. A group of Levite priests who claim descent from Moses. Associated with the first temple in the city of Shiloh. The first author in this group is commonly known as the Elohist, or E.</dd>',
        '<dt class="source source-p">Blue</dt><dd class="source source-p">Aaronids. A group of Levite priests who claim descent from Aaron. Associated with the first and second temple in Jerusalem. The first author in this group is known as the Priestly source, or P.</dd>',
        '<dt class="source source-dtrb">Orange</dt><dd class="source source-dtrb">Deuteronomists. The later Mushite tradition, associated with king Josiah, the Shiloh and Anathoth priesthood, and the prophet Jeremiah.</dd>',
        '<dt class="source source-r">Highlights</dt><dd class="source source-r">Editors. Called Redactors in bible circles, since E was already taken. Redactors mostly insert glue prose when combining sources.</dd>',
        '<dt class="source source-bookofrecords">Record Grey</dt><dd class="source source-bookofrecords">Records. Begat lists, genealogies, and miscellaneous documents.</dd>',
        '</dl>', "",
        '# The Source Fonts {.front-heading}', "",
        '<div class="font-legend"><p class="source source-j hebrew" dir="rtl">𐤀𐤁𐤂𐤃𐤄𐤅𐤆𐤇𐤈𐤉𐤊𐤋𐤌𐤍𐤎𐤏𐤐𐤑𐤒𐤓𐤔𐤕</p><p class="source source-j">J is written in the Paleo-Hebrew script of around 922 B.C.</p>',
        '<p class="source source-e hebrew" dir="rtl">ABGDHWZXJYKLMNS]PCQRVT</p><p class="source source-e">E uses a northern variant of the Paleo-Hebrew script from soon after the time of J.</p>',
        '<p class="source source-p hebrew" dir="rtl">אֲבֱגֶּדֲהֹוּזֻחִטֳיִּכֻלֵּמֱנָסֶעֲפֹצֻקָרֶשְּׁתֽ</p><p class="source source-p">P is rendered in the modern Hebrew square script with niqqud.</p>',
        '<p class="source source-r hebrew" dir="rtl">אבגדהוזחטיכלמנסעפצקרשת</p><p class="source source-r">R uses the Ezra variant of the Hebrew square script with no niqqud.</p></div>', "",
        '# Publication Notice {.front-heading .visually-hidden}', "",
        '<div class="publication-notice"><p><span class="aside-a">LD LLC makes no claim to have written the book that follows.<br/>We could not find a published edition of it, and thought one<br/>ought to exist. LD undertook the preparation of the text for<br/>publication, including its editing, typesetting, design, and</span><br/><span class="aside-b">production and is responsible for the volume presented here,<br/>but we make no claim to know the identity of the individuals<br/>who wrote the original text, nor do we make any claim to the<br/>effect that the original authors did not incorporate in that</span><br/><span class="aside-c">volume any earlier sources either verbatim or in paraphrase.<br/>In summary, it’s a bible, and all rules of that genre apply.<br/>If your work has been incorporated into the resulting volume<br/>and you would like to be removed from the bible, let us know</span></p>',
        '<img class="publication-logo" src="img/ld-book-light.png" alt="LD"/></div>', "",
    ]


def make_markdown(path: Path, selected_book: str | None = None) -> tuple[int, int]:
    sequence = master_sequence(selected_book)
    lines = ["---", "lang: en-US", "---", ""] + front_matter(sequence)
    last_book = None
    chapter_count = verse_count = 0
    for book, rel in sequence:
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
    # Pandoc runs from the repository root so source-relative images resolve.
    # Resolve the requested destination first so a relative --output remains
    # relative to the caller instead of being written into ROOT.
    args.output = args.output.resolve()
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
               "--metadata-file", str(HERE / "metadata.yaml"), "--epub-title-page=false"]
        for font in FONT_FILES:
            cmd += ["--epub-embed-font", str(font)]
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
