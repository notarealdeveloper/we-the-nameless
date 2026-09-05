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
import textwrap
import time
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
MASTER = ROOT / "master.tex"
OUTPUT = HERE / "we-the-nameless.epub"

# Publisher fonts are limited to scripts whose repertoire/design carries
# meaning. Ordinary prose deliberately remains in the reader's chosen font.
FONT_FILES = [
    ROOT / "fonts/hebrew-david.ttf",
    ROOT / "fonts/hebrew-david-bold.ttf",
    ROOT / "fonts/hebrew-ezra.ttf",
    ROOT / "fonts/paleo-hebrew-phoenician.ttf",
    ROOT / "fonts/paleo-hebrew.ttf",
    ROOT / "fonts/paleo-hebrew-siloam.ttf",
    ROOT / "fonts/paleo-hebrew-mono.ttf",
    ROOT / "fonts/english-im-fell-english-sc-regular.ttf",
    ROOT / "fonts/egyptian-hieroglyphs-regular-noto-sans.ttf",
    ROOT / "fonts/arabic-amiri-regular.ttf",
    ROOT / "fonts/noto-sans-syriac.ttf",
    ROOT / "fonts/noto-sans-cuneiform-regular.ttf",
    ROOT / "fonts/noto-sans-ugaritic-regular.ttf",
]

SOURCE_NAMES = {
    "J": "J", "E": "E", "P": "P", "R": "R", "X": "Other",
    "JE": "JE", "JP": "JP", "JM": "JM", "JPP": "JPP", "PR": "PR",
    "EP": "EP", "EPP": "EPP", "PP": "Paleo P", "Diff": "Textual difference",
    "Red": "Redactor", "Reblacktor": "Redactor", "Records": "Book of Records",
    "RJE": "RJE", "Dtn": "Dtn", "DtrA": "Dtr A", "DtrB": "Dtr B",
    "DtrH": "Dtr H", "Proto": "Proto", "ProtoA": "Proto A",
    "ProtoF": "Proto F", "Other": "Other", "BookOfRecords": "Book of Records",
}

SOURCE_ALIASES = {"BookOfRecords": "Records"}

COMMENTARY = {"aA": "annotation-a", "aB": "annotation-b",
              "aC": "annotation-c", "aP": "annotation-p",
              "aR": "annotation-r", "aRJE": "annotation-rje"}

INLINE = {
    "textbf": "strong", "bf": "strong", "emph": "em", "textit": "em",
    "textsl": "em", "textsc": "span", "texttt": "code", "heb": "span",
    "paleo": "span", "Paleo": "span", "Def": "dfn", "redacted": "span",
    "sout": "s", "textsuperscript": "sup", "path": "code", "href": "a",
}

LANGUAGE_INLINE = {
    "heb": ("hebrew", "he", "rtl"),
    "hebniq": ("hebrew hebrew-pointed", "he", "rtl"),
    "arb": ("arabic", "ar", "rtl"),
    "syriac": ("syriac", "syr", "rtl"),
    "ara": ("aramaic", "arc", "rtl"),
    "phn": ("phoenician", "phn", "rtl"),
    "uga": ("ugaritic", "uga", "ltr"),
    "akk": ("cuneiform", "akk", "ltr"),
    "cun": ("cuneiform", "akk", "ltr"),
    "egypt": ("egyptian", "egy", "ltr"),
    "egyptRaw": ("egyptian", "egy", "ltr"),
    "egyptNew": ("egyptian", "egy", "ltr"),
    "chinese": ("cjk", "zh-Hant", "ltr"),
    "chineseA": ("cjk", "zh-Hant", "ltr"),
    "chineseB": ("cjk", "zh-Hant", "ltr"),
    "chineseC": ("cjk", "zh-Hant", "ltr"),
    "chineseD": ("cjk", "zh-Hant", "ltr"),
    "chineseE": ("cjk", "zh-Hant", "ltr"),
    "korean": ("cjk", "ko", "ltr"),
    "telugu": ("telugu", "te", "ltr"),
}

COLOR_INLINE = {
    "cK": "ink", "cBlack": "ink", "cR": "red", "cRed": "red",
    "cB": "blue", "cBlue": "blue", "cG": "green", "cGreen": "green",
    "cY": "yellow", "cYellow": "yellow", "cGray": "gray", "cGrey": "gray",
    "hlA": "highlight-a", "hlB": "highlight-b", "hlC": "highlight-c",
}

MATH_SYMBOLS = {
    "sim": "∼", "approx": "≈", "times": "×", "cdot": "·",
    "rightarrow": "→", "infty": "∞", "phi": "φ", "gamma": "γ",
    "Delta": "Δ", "lambda": "λ", "tau": "τ", "oint": "∮",
}

ZERO_ARGUMENT_TEXT = {
    "IsaacBoundBurnedSummary": "Isaac bourned",
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


def optional_group(text: str, pos: int) -> tuple[str, int] | None:
    """Read a balanced TeX optional argument, if present."""
    while pos < len(text) and text[pos].isspace():
        pos += 1
    if pos >= len(text) or text[pos] != "[":
        return None
    depth, start, i = 1, pos + 1, pos + 1
    while i < len(text) and depth:
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == "[":
            depth += 1
        elif text[i] == "]":
            depth -= 1
        i += 1
    if depth:
        raise ValueError("unbalanced TeX optional argument")
    return text[start:i - 1], i


def split_tex(text: str, separator: str) -> list[str]:
    """Split at a TeX separator only at top-level brace depth."""
    parts: list[str] = []
    start = depth = i = 0
    while i < len(text):
        if text[i] == "\\":
            if depth == 0 and text.startswith(separator, i):
                parts.append(text[start:i])
                i += len(separator)
                start = i
                continue
            i += 2
            continue
        if text[i] == "{":
            depth += 1
        elif text[i] == "}" and depth:
            depth -= 1
        elif depth == 0 and text.startswith(separator, i):
            parts.append(text[start:i])
            i += len(separator)
            start = i
            continue
        i += 1
    parts.append(text[start:])
    return parts


def table_alignments(column_spec: str) -> list[str]:
    """Extract conceptual l/c/r alignment from a TeX tabular preamble."""
    spec = re.sub(r"@\{(?:[^{}]|\{[^{}]*\})*\}", "", column_spec)
    return [
        {"l": "start", "c": "center", "r": "end", "p": "start"}[token]
        for token in re.findall(r"[lcr]|p(?=\{)", spec)
    ]


def render_table(body: str, column_spec: str, custom_setup: bool = False) -> str:
    r"""Render \Table's centered blue, compact tabular as semantic HTML."""
    alignments = table_alignments(column_spec)
    has_vertical_rules = "|" in column_spec
    rows = [row for row in split_tex(body, r"\\") if row.strip()]
    rendered_rows: list[str] = []
    for row_number, raw_row in enumerate(rows):
        rule_above = bool(re.match(r"\s*\\(?:hline|toprule|midrule|bottomrule)\b", raw_row))
        row = re.sub(r"\\(?:hline|toprule|midrule|bottomrule)\b", "", raw_row).strip()
        if not row:
            continue
        cells = [cell.strip() for cell in split_tex(row, "&")]
        if not any(cells):
            continue
        is_header = row_number == 0 and any(re.search(r"\\(?:textbf|bf)\b", cell) for cell in cells)
        tag = "th" if is_header else "td"
        attrs = ' scope="col"' if tag == "th" else ""
        rendered_cells: list[str] = []
        for column, cell in enumerate(cells):
            content = tex_to_markdown(cell).strip()
            # Inline dollar math inside raw HTML tables can be paired across
            # cell boundaries by Markdown parsers. Keep simple table math
            # textual and local; display equations elsewhere still use MathML.
            content = re.sub(
                r"\$([^$]+)\$",
                lambda match: '<span class="math">' + html.escape(
                    match.group(1).replace(r"\sim", "∼").replace(r"\approx", "≈")
                ) + "</span>",
                content,
            )
            content = re.sub(r"\s*\n\s*", " ", content)
            alignment = alignments[column] if column < len(alignments) else "start"
            rendered_cells.append(f'<{tag}{attrs} class="align-{alignment}">{content}</{tag}>')
        rendered = "".join(rendered_cells)
        row_class = ' class="rule-above"' if rule_above else ""
        rendered_rows.append(f"<tr{row_class}>{rendered}</tr>")
    if not rendered_rows:
        return ""
    first_is_header = rendered_rows[0].find("<th") >= 0
    if first_is_header:
        head, *rest = rendered_rows
        contents = f"<thead>{head}</thead><tbody>{''.join(rest)}</tbody>"
    else:
        contents = f"<tbody>{''.join(rendered_rows)}</tbody>"
    classes = ["wtn-table"]
    if has_vertical_rules:
        classes.append("wtn-table-vertical-rules")
    if custom_setup:
        classes.append("wtn-table-custom")
    return f'\n\n<div class="table-scroll"><table class="{" ".join(classes)}">{contents}</table></div>\n\n'


def annotation_block(content: str, classes: str, alignment: str) -> str:
    """Keep multi-paragraph annotations valid inside Markdown fenced divs."""
    blocks = []
    for part in re.split(r"\n\s*\n", content.strip()):
        part = re.sub(r"\s*\n\s*", " ", part).strip()
        if part:
            blocks.append(f'<span class="annotation-paragraph">{part}</span>')
    return f'<span class="annotation {classes} align-{alignment}" role="note">{"".join(blocks)}</span>'


def command_at(text: str, pos: int) -> tuple[str, int] | None:
    if text[pos] != "\\":
        return None
    match = re.match(r"\\([A-Za-z@]+|.)", text[pos:])
    return (match.group(1), pos + len(match.group(0))) if match else None


def source_class(name: str) -> tuple[str, str] | None:
    if len(name) < 2 or name[0] not in "he":
        return None
    key = SOURCE_ALIASES.get(name[1:], name[1:])
    if key not in SOURCE_NAMES:
        return None
    return ("hebrew" if name[0] == "h" else "english", key)


def tex_to_markdown(text: str) -> str:
    """Conservatively retain prose while translating semantic TeX markup."""
    text = textwrap.dedent(strip_comments(text)).replace("~", "\u00a0")
    text = text.replace("``", "“").replace("''", "”")
    # Tables may contain currency dollars. Render them before scanning TeX math
    # so a price in one cell can never pair with a later price as an equation.
    table_runs: list[str] = []
    table_pos = 0
    while True:
        match = re.search(r"\\Table\s*", text[table_pos:])
        if not match:
            break
        start = table_pos + match.start()
        cursor = table_pos + match.end()
        setup = optional_group(text, cursor)
        setup_value = None
        if setup:
            setup_value, cursor = setup
        columns = group(text, cursor)
        if not columns:
            table_pos = cursor
            continue
        column_spec, cursor = columns
        rows = group(text, cursor)
        if not rows:
            table_pos = cursor
            continue
        row_body, end = rows
        token = f"WTNTABLERUN{len(table_runs)}TOKEN"
        table_runs.append(render_table(row_body, column_spec, setup_value is not None))
        text = text[:start] + token + text[end:]
        table_pos = start + len(token)
    math_runs: list[str] = []

    def protect_math(match: re.Match[str]) -> str:
        math = re.sub(r"\\(?:paleo|Paleo)\{([^{}]*)\}", r"\1", match.group(0))
        token = f"WTNMATHRUN{len(math_runs)}TOKEN"
        math_runs.append(math)
        return token

    text = re.sub(
        r"(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$(?![\d,])[^$\n]+(?<!\\)\$",
        protect_math,
        text,
        flags=re.DOTALL,
    )
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
            if text[i] == "$":
                out.append("&#36;")
            else:
                out.append(html.escape(text[i]) if text[i] in "&<>" else text[i])
            i += 1
            continue
        cmd_data = command_at(text, i)
        if not cmd_data:
            # A few source reconstructions use a trailing backslash as a
            # visual line-end marker. It has no content of its own.
            i += 1; continue
        name, after = cmd_data
        if name in MATH_SYMBOLS:
            out.append(MATH_SYMBOLS[name]); i = after; continue
        if name in ZERO_ARGUMENT_TEXT:
            out.append(ZERO_ARGUMENT_TEXT[name]); i = after; continue
        if name in {"nl", "linebreak", "par", "medskip", "newpage", "clearpage", "pagebreak"}:
            out.append("<br/>" if name in {"nl", "linebreak"} else "\n\n")
            i = after; continue
        if name == "item":
            out.append("\n- "); i = after; continue
        if name in {"mdash", "textemdash"}:
            out.append("—"); i = after; continue
        if name in {"ndash", "textendash"}:
            out.append("–"); i = after; continue
        if name == "\\":
            out.append("<br/>"); i = after; continue
        if name in {"hfill", "noindent", "centering", "raggedbottom", "RaggedRight",
                    "relax", "leavevmode", "sloppy", "tiny", "scriptsize", "footnotesize",
                    "small", "large", "Large", "bfseries", "ttfamily", "selectfont"}:
            i = after; continue
        optional = optional_group(text, after)
        optional_value = None
        if optional:
            optional_value, after = optional
        arg = group(text, after)
        if not arg:
            # Preserve common escaped punctuation; discard purely presentational commands.
            out.append({"%": "%", "&": "&amp;", "_": "_", "#": "#", "$": "&#36;", "{": "{", "}": "}"}.get(name, ""))
            i = after; continue
        body, end = arg
        if name == "Table":
            table_body = group(text, end)
            if table_body:
                table_body_value, end = table_body
                out.append(render_table(table_body_value, body, optional_value is not None))
            i = end
            continue
        if name in {"Def", "DefA", "DefB", "DefC"}:
            label = tex_to_markdown(body).strip()
            qualifier_value = None
            if name == "Def":
                qualifier = optional_group(text, end)
                if qualifier:
                    qualifier_value, end = qualifier
            second = group(text, end)
            if second:
                definition, end = second
                cls = {"Def": "definition", "DefA": "definition-a",
                       "DefB": "definition-b", "DefC": "definition-c"}[name]
                qualifier = ""
                if name == "Def" and qualifier_value:
                    qualifier = (
                        '<span class="definition-qualifier">('
                        + tex_to_markdown(qualifier_value).strip() + ")</span>"
                    )
                out.append(
                    f'\n\n<section class="definition {cls}">'
                    f'<p class="definition-heading"><dfn>{label}</dfn>{qualifier}.</p>'
                    f'<div class="definition-body">{tex_to_markdown(definition).strip()}</div>'
                    f'</section>\n\n'
                )
            else:
                out.append(f"<dfn>{label}</dfn>")
            i = end
            continue
        rendered = tex_to_markdown(body).strip()
        src = source_class(name)
        if src:
            language, key = src
            attrs = ' lang="he" dir="rtl"' if language == "hebrew" else ""
            label = html.escape(SOURCE_NAMES[key])
            if language == "hebrew":
                rendered = historical_hebrew(rendered, key)
            is_block = any(marker in rendered for marker in ("<div ", "<table"))
            if is_block:
                # HTML tables/divs cannot legally be children of an inline
                # source span. Their cells retain their own semantic markup.
                out.append(rendered)
            else:
                rendered = re.sub(r"\s*\n\s*", " ", rendered)
                out.append(f'<span class="source source-{key.lower()} {language}"{attrs} data-source="{label}">{rendered}</span>')
        elif name in COMMENTARY or re.fullmatch(r"a(?:A|B|C|J|E|P|DtrA|DtrB|Dtn|R|RJE|Records|Other)[lcr]", name):
            base_name = name[:-1] if name not in COMMENTARY else name
            cls = COMMENTARY.get(base_name, "annotation")
            alignment = {"l": "start", "c": "center", "r": "end"}.get(name[-1], "start")
            if any(marker in rendered for marker in ("<div ", "<table")):
                out.append(rendered)
            elif "\n\n" in rendered:
                out.append(annotation_block(rendered, cls, alignment))
            else:
                note = re.sub(r"\s*\n\s*", " ", rendered)
                out.append(f'<span class="annotation {cls} align-{alignment}" role="note">{note}</span>')
        elif name in {"fA", "fB", "fC", "fAX", "fBX", "fCX"}:
            voice = name[1]
            out.append(f'^[<span class="footnote-voice annotation-{voice.lower()}">{rendered}</span>]')
        elif name == "footnote" or name in {"recursivefootnote", "hangingfootnote"}:
            out.append(f"^[{rendered}]")
        elif name == "href":
            second = group(text, end)
            if second:
                label, end = second
                out.append(f"[{tex_to_markdown(label).strip()}]({body})")
            else:
                out.append(body)
        elif name in LANGUAGE_INLINE:
            cls, language, direction = LANGUAGE_INLINE[name]
            out.append(
                f'<span class="{cls}" lang="{language}" dir="{direction}">{rendered}</span>'
            )
        elif name in COLOR_INLINE:
            out.append(f'<span class="{COLOR_INLINE[name]}">{rendered}</span>')
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
                alt = html.escape(Path(path).stem.replace("-", " ").replace("_", " "))
                out.append(f'\n\n<figure><img src="{html.escape(path)}" alt="{alt}"/></figure>\n\n')
        elif name in {"hspace", "vspace", "raisebox", "makebox", "size", "up", "dn"}:
            second = group(text, end)
            if second:
                value, end = second
                out.append(tex_to_markdown(value).strip())
        elif name in {"Chapter", "Verse", "Book", "BookPart"}:
            out.append(rendered)
        else:
            # Unknown semantic wrappers are unwrapped, never silently dropping their prose.
            out.append(rendered)
        i = end
    result = "".join(out)
    # TeX source indentation is never a Markdown code block.
    result = re.sub(r"\n[ \t]+", "\n", result)
    result = re.sub(r"[ \t]+\n", "\n", result)
    result = re.sub(r"\n{4,}", "\n\n\n", result)
    for number, math in enumerate(math_runs):
        result = result.replace(f"WTNMATHRUN{number}TOKEN", math)
    for number, table in enumerate(table_runs):
        result = result.replace(f"WTNTABLERUN{number}TOKEN", table)
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


def chapter_summaries() -> dict[tuple[str, str], str]:
    """Read the editorial labels used by the print book's own contents page."""
    source = strip_comments(MASTER.read_text(encoding="utf-8"))
    summaries: dict[tuple[str, str], str] = {}
    for match in re.finditer(r"\\ChapterSummaryLink\s*", source):
        cursor = match.end()
        args: list[str] = []
        for _ in range(4):
            parsed = group(source, cursor)
            if not parsed:
                break
            value, cursor = parsed
            args.append(value.strip())
        if len(args) == 4:
            _, chapter, book, title = args
            summaries[(book, chapter)] = tex_to_markdown(title).strip()
    return summaries


def front_matter(sequence: list[tuple[str, str]], summaries: dict[tuple[str, str], str]) -> list[str]:
    """Reproduce the visible front matter from master.tex in reflowable form."""
    books = list(dict.fromkeys(book for book, _ in sequence))
    contents_sections: list[str] = [":::: {.contents-list}"]
    for book in books:
        chapters: list[str] = []
        for label, rel in sequence:
            if label != book:
                continue
            source = (ROOT / rel).read_text(encoding="utf-8")
            found = re.search(r"\\Chapter\s*\{([^}]+)\}", strip_comments(source))
            chapter = found.group(1).strip() if found else Path(rel).stem
            anchor = re.sub(r"[^a-z0-9]+", "-", f"{book}-{chapter}".lower()).strip("-")
            title = summaries.get((book, chapter), f"{book} {chapter}")
            chapters.append(f'{chapter}. [{title}](#{anchor})')
        book_anchor = re.sub(r"[^a-z0-9]+", "-", book.lower()).strip("-")
        contents_sections += [f'### [{book}](#{book_anchor}) {{#contents-{book_anchor} .contents-book-title}}', "", *chapters, ""]
    contents_sections.append("::::")
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
        '# Contents {.front-heading}', "", *contents_sections, "",
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
    summaries = chapter_summaries()
    lines = ["---", "lang: en-US", "---", ""] + front_matter(sequence, summaries)
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
        summary = summaries.get((book, chapter), "")
        heading = f"{chapter}. {summary}" if summary else f"{book} {chapter}"
        lines += [f"## {heading} {{#{anchor} .chapter-title}}", ""]
        chapter_count += 1
        verse_occurrences: dict[str, int] = {}
        for number, hebrew, english, commentary in parse_verses(source):
            verse_count += 1
            number_slug = re.sub(r'[^a-zA-Z0-9]+', '-', number).strip('-')
            base_verse_anchor = f"{anchor}-{number_slug}"
            duplicate_count = verse_occurrences.get(base_verse_anchor, 0)
            verse_occurrences[base_verse_anchor] = duplicate_count + 1
            verse_anchor = base_verse_anchor if not duplicate_count else f"{base_verse_anchor}-alternate-{duplicate_count + 1}"
            # master.tex: \Verse -> \VerseBody -> \VerseVertical.  Preserve its
            # reference/rule header, then English-before-Hebrew document order.
            lines += [
                f':::::: {{.verse #{verse_anchor}}}',
                f'### {book} {chapter}:{number} {{#{verse_anchor}-number .verse-reference}}',
                "::::: {.verse-translation}", tex_to_markdown(english), ":::::",
                '::::: {.verse-source lang="he" dir="rtl"}', tex_to_markdown(hebrew), ":::::",
            ]
            rendered_commentary = tex_to_markdown(commentary)
            if rendered_commentary:
                lines += ["::::: {.verse-commentary}", rendered_commentary, ":::::"]
            lines += ["::::::", ""]
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
        cmd = ["pandoc", str(manuscript), "--from=markdown+fenced_divs+footnotes+raw_html+markdown_in_html_blocks",
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
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        if result.returncode:
            return result.returncode
        fatal_warnings = ("Duplicate identifier", " unclosed at ")
        if any(marker in result.stderr for marker in fatal_warnings):
            log("Pandoc emitted structural warnings; refusing a potentially damaged EPUB")
            return 2
        validator = HERE / "validate.py"
        log("Running EPUB package and link validation...")
        validation = subprocess.run(
            [sys.executable, str(validator), str(args.output)], cwd=ROOT, check=False
        )
        if validation.returncode:
            return validation.returncode
        epubcheck = shutil.which("epubcheck")
        if epubcheck:
            log(f"Running EPUBCheck: {epubcheck}")
            checked = subprocess.run([epubcheck, str(args.output)], check=False)
            if checked.returncode:
                return checked.returncode
        else:
            log("EPUBCheck is not installed; dependency-free structural validation completed")
    output_size = args.output.stat().st_size
    elapsed = time.monotonic() - started
    log(
        f"Built {args.output} ({output_size:,} bytes, {chapters} chapters, "
        f"{verses} verses) in {elapsed:.1f}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
