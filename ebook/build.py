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
import uuid
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
MASTER = ROOT / "master.tex"
OUTPUT = HERE / "we-the-nameless.epub"

# Publication identity must survive rebuilds.  Pandoc otherwise invents a new
# UUID each time, which makes stores (notably Google Play Books) treat an
# updated file as an unrelated book.  Keep a private UUID namespace and derive
# one identifier for each independently publishable edition.
PUBLICATION_NAMESPACE = uuid.UUID("9857bfad-f269-55a1-a839-fae7375e68b6")
PUBLICATION_KEY = "we-the-nameless"


def publication_metadata(selected_book: str | None) -> dict[str, str]:
    """Return stable store-facing metadata for a complete or single-book EPUB."""
    edition = selected_book or "complete"
    identity = f"{PUBLICATION_KEY}:{edition.casefold()}"
    return {
        "identifier": f"urn:uuid:{uuid.uuid5(PUBLICATION_NAMESPACE, identity)}",
        "title": "We The Nameless" if selected_book is None else f"We The Nameless: {selected_book}",
        "publisher": "LD LLC",
    }

# Publisher fonts are limited to scripts whose repertoire/design carries
# meaning. Ordinary prose deliberately remains in the reader's chosen font.
FONT_FILES = [
    ROOT / "fonts/hebrew-david.ttf",
    ROOT / "fonts/hebrew-david-bold.ttf",
    ROOT / "fonts/hebrew-ezra.ttf",
    ROOT / "fonts/babel-paleo-hebrew-phoenician.ttf",
    ROOT / "fonts/paleo-hebrew.ttf",
    ROOT / "fonts/08-bc10c-paleo-hebrew-tel-zayit.ttf",
    ROOT / "fonts/paleo-hebrew-moabite.ttf",
    ROOT / "fonts/paleo-hebrew-siloam.ttf",
    ROOT / "fonts/paleo-hebrew-mono.ttf",
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

# Historical faces backed by Latin codepoints need a bidi override: their
# characters are Hebrew even though a reading system sees strong LTR ASCII.
# Unicode Phoenician and square Hebrew need only an RTL base direction.
LEGACY_LTR_CODEPOINT_SOURCE_KEYS = {"E", "JE", "RJE", "Proto", "ProtoA", "ProtoF", "Other"}

# master.tex's speaker shortcuts are commentary-sized wrappers around either
# the A/B/C inks or a complete English source profile.  Keep that distinction:
# aJ is not merely generic commentary, for example; it is commentary in J's
# source face/colour.
COMMENTARY = {
    "aA": "annotation-a", "aB": "annotation-b", "aC": "annotation-c",
    "aJ": "source source-j english", "aE": "source source-e english",
    "aP": "annotation-p", "aDtrA": "source source-dtra english",
    "aDtrB": "source source-dtrb english", "aDtn": "source source-dtn english",
    "aR": "source source-r english", "aRJE": "source source-rje english",
    "aRecords": "source source-records english",
    "aOther": "source source-other english",
}

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
PALEO_ASCII_TABLE = str.maketrans(HEBREW_ORDER, PALEO_ASCII)
TEL_ZAYIT_ASCII = "ABGDHWZXTYKKLMMNNSOPPC CQRst".replace(" ", "")
TEL_ZAYIT_ASCII_TABLE = str.maketrans(HEBREW_ORDER, TEL_ZAYIT_ASCII)
_MATHML_CACHE: dict[str, str] = {}


def historical_hebrew(text: str, key: str) -> str:
    """Apply the same broad Hebrew encodings as master.tex's source profiles."""
    # P is explicitly printed in pointed square Hebrew.  Only the historical
    # alphabets discard niqqud before their glyph conversion.
    if key != "P":
        text = "".join(char for char in text if not unicodedata.combining(char))
    if key == "J":
        # The babeled J face maps Hebrew codepoints to its original Phoenician
        # outlines. Keeping Hebrew here gives Kindle an unambiguous RTL script.
        return text
    # master.tex's generic Proto profile (used for the Blessing of Jacob and
    # Genesis 14:1) selects the ASCII-slotted Tel Zayit hand. Its tet, ayin,
    # shin, and tav slots deliberately differ from the generic paleo map.
    if key == "Proto":
        return text.translate(TEL_ZAYIT_ASCII_TABLE)
    if key in {"E", "JE", "RJE", "Other"} or key.startswith("Proto"):
        encoded = text.translate(PALEO_ASCII_TABLE)
        return encoded
    # The Book of Records font used in Genesis 5 stores glyphs at Hebrew
    # codepoints. It needs stripped Hebrew, not the ASCII paleo encoding.
    return text


def log(message: str) -> None:
    """Print a build status message immediately."""
    print(f"[ebook] {message}", flush=True)


def render_complex_math(math: str) -> str | None:
    """Convert a self-contained formula before raw commentary HTML encloses it."""
    if math in _MATHML_CACHE:
        return _MATHML_CACHE[math]
    pandoc = shutil.which("pandoc")
    if not pandoc:
        return None
    converted = subprocess.run(
        [pandoc, "--from=markdown", "--to=html", "--mathml"],
        input=math, text=True, capture_output=True, check=False,
    )
    if converted.returncode:
        return None
    found = re.search(r"<math\b.*?</math>", converted.stdout, flags=re.DOTALL)
    if not found:
        return None
    fragment = found.group(0)
    # This fragment is subsequently embedded in a raw HTML commentary block.
    # With markdown_in_html_blocks enabled, Pandoc reparses underscores in the
    # optional TeX source annotation as emphasis and emits invalid MathML
    # (<em> is not permitted inside <annotation>).  The rendered mrow is the
    # accessible mathematical content; discard only the redundant source form.
    fragment = re.sub(r"<annotation\b[^>]*>.*?</annotation>", "", fragment, flags=re.DOTALL)
    _MATHML_CACHE[math] = fragment
    return fragment


def strip_comments(text: str) -> str:
    # A TeX comment consumes its line ending too. Consuming indentation on the
    # continuation line models TeX's ignored beginning-of-line space and, most
    # importantly, distinguishes `%\n` (no interword space) from a plain line
    # ending (one interword space after normalisation).
    return re.sub(r"(?<!\\)%[^\r\n]*(?:\r?\n[ \t]*)?", "", text)


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


def color_footnote_tokens(content: str, classes: str) -> str:
    """Apply a TeX speaker scope inside each detached Markdown footnote."""
    out: list[str] = []
    cursor = 0
    while True:
        start = content.find("^[", cursor)
        if start < 0:
            out.append(content[cursor:])
            break
        out.append(content[cursor:start])
        depth = 1
        end = start + 2
        while end < len(content) and depth:
            if content[end] == "[":
                depth += 1
            elif content[end] == "]":
                depth -= 1
            end += 1
        if depth:
            out.append(content[start:])
            break
        inner = content[start + 2:end - 1]
        out.append(f'^[<span class="footnote-voice {classes}">{inner}</span>]')
        cursor = end
    return "".join(out)


def render_tikz_fallback(body: str) -> str:
    """Translate the recurring Jacob-family TikZ scene into reflowable HTML."""
    match = re.search(r"\\JacobFamilyPeople\s*", body)
    people: list[str] = []
    if match:
        cursor = match.end()
        for _ in range(4):
            parsed = group(body, cursor)
            if not parsed:
                break
            value, cursor = parsed
            people.append(tex_to_markdown(value).strip())
    if len(people) != 4:
        return '<figure class="ebook-diagram"><figcaption>Diagram from the print edition.</figcaption></figure>'
    crossed = r"\JacobBlessingHand" in body
    hands = (
        '<div class="family-hands" aria-label="Jacob crosses his hands">↘ × ↙</div>'
        if crossed else ""
    )
    caption = (
        "Jacob crosses his hands toward Ephraim and Manasseh."
        if crossed else "Jacob, Ephraim, Manasseh, and Joseph."
    )
    return (
        '<figure class="ebook-diagram family-diagram" role="group">'
        f'<div class="family-jacob egyptian" lang="egy">{people[0]}</div>'
        f'{hands}<div class="family-grandsons egyptian" lang="egy">'
        f'<span>{people[1]}</span><span>{people[2]}</span></div>'
        f'<div class="family-joseph egyptian" lang="egy">{people[3]}</div>'
        f'<figcaption>{caption}</figcaption></figure>'
    )


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


def resolve_image_path(authored_path: str) -> Path | None:
    """Resolve print-style image names to a concrete source asset for EPUB."""
    direct = ROOT / authored_path
    if direct.is_file():
        return direct
    suffixes = ("",) if Path(authored_path).suffix else (".jpg", ".png")
    matches = [
        candidate
        for suffix in suffixes
        for candidate in ROOT.glob(f"*/include/{authored_path}{suffix}")
        if candidate.is_file()
    ]
    return matches[0] if len(matches) == 1 else None


def tex_to_markdown(text: str, *, compact: bool = False) -> str:
    """Conservatively retain prose while translating semantic TeX markup."""
    text = textwrap.dedent(strip_comments(text)).replace("~", "\u00a0")
    text = text.replace("``", "“").replace("''", "”")
    # A centered quote in TeX is a centered block, not a blockquote whose
    # contents should subsequently fall back to normal paragraph alignment.
    text = re.sub(
        r"\\begin\{quote\}\s*\\centering(.*?)\\end\{quote\}",
        r"\\begin{center}\1\\end{center}", text, flags=re.DOTALL,
    )
    tikz_runs: list[str] = []
    tikz_start = r"\begin{tikzpicture}"
    tikz_end = r"\end{tikzpicture}"
    search_from = 0
    while True:
        start = text.find(tikz_start, search_from)
        if start < 0:
            break
        end = text.find(tikz_end, start + len(tikz_start))
        if end < 0:
            break
        token = f"WTNTIKZRUN{len(tikz_runs)}TOKEN"
        tikz_runs.append(render_tikz_fallback(text[start + len(tikz_start):end]))
        text = text[:start] + token + text[end + len(tikz_end):]
        search_from = start + len(token)
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
    # Convert ordinary tabular environments too.  Processing the innermost
    # environment first also preserves the three-column comparison layout in
    # Genesis 2; its already-protected child \Table tokens become nested tables.
    while True:
        end_match = re.search(r"\\end\{tabularx?\}", text)
        if not end_match:
            break
        starts = list(re.finditer(r"\\begin\{(tabularx?)\}", text[:end_match.start()]))
        if not starts:
            break
        start_match = starts[-1]
        cursor = start_match.end()
        if start_match.group(1) == "tabularx":
            width = group(text, cursor)
            if width:
                _, cursor = width
        columns = group(text, cursor)
        if not columns:
            break
        column_spec, body_start = columns
        body = text[body_start:end_match.start()]
        token = f"WTNTABLERUN{len(table_runs)}TOKEN"
        table_runs.append(render_table(body, column_spec, True))
        text = text[:start_match.start()] + token + text[end_match.end():]
    math_runs: list[str] = []

    def protect_math(match: re.Match[str]) -> str:
        math = re.sub(r"\\(?:paleo|Paleo)\{([^{}]*)\}", r"\1", match.group(0))
        # The print book occasionally stacks two readings with TeX's low-level
        # \genfrac primitive. Pandoc cannot parse the surrounding \hbox,
        # \raisebox and custom \size commands, so express the same editorial
        # relationship as an accessible, reflow-safe inline stack.
        if r"\genfrac" in math:
            start = math.find(r"\genfrac") + len(r"\genfrac")
            arguments: list[str] = []
            cursor = start
            for _ in range(6):
                parsed = group(math, cursor)
                if not parsed:
                    break
                value, cursor = parsed
                arguments.append(value)
            if len(arguments) == 6:
                readings = []
                for value in arguments[-2:]:
                    # The generic converter unwraps hbox and preserves the
                    # content argument of raisebox/size while dropping their
                    # print-only measurements.
                    readings.append(tex_to_markdown(value).strip())
                rtl_paleo = any(re.search(r"[\u0590-\u05ff]", value) for value in readings)
                if rtl_paleo:
                    readings = [historical_hebrew(value, "J") for value in readings]
                stack_class = "stacked-reading paleo" if rtl_paleo else "stacked-reading"
                direction = ' lang="he" dir="rtl"' if rtl_paleo else ""
                rendered = (
                    f'<span class="{stack_class}"{direction} role="group" '
                    'aria-label="alternate readings: '
                    + html.escape("; ".join(re.sub(r"<[^>]+>", "", item) for item in readings), quote=True)
                    + '"><span>' + readings[0] + '</span><span>' + readings[1] + '</span></span>'
                )
                token = f"WTNMATHRUN{len(math_runs)}TOKEN"
                math_runs.append(rendered)
                return token
        # Protected runs are restored after TeX indentation has been removed;
        # normalize them now so indented display math does not become a code
        # block (which causes Pandoc to leave raw TeX in the EPUB).
        delimiter = "$$" if math.startswith("$$") else "$"
        inner = math[len(delimiter):-len(delimiter)]
        inner = textwrap.dedent(inner).strip()
        # A single line is accepted both in normal Markdown and inside the raw
        # HTML note containers used for complex commentary.
        inner = " ".join(line.strip() for line in inner.splitlines())
        math = f"{delimiter}{inner}{delimiter}"
        token = f"WTNMATHRUN{len(math_runs)}TOKEN"
        # Pandoc parses ordinary formulas correctly in the final document.
        # Complex display formulas nested in raw commentary spans need to be
        # converted before those spans are created or some writers retain TeX.
        preconverted = render_complex_math(math) if delimiter == "$$" and re.search(r"\\(?:boxed|frac|sqrt|text)\b", inner) else None
        math_runs.append(preconverted or math)
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
                if name == "minipage":
                    placement = optional_group(text, i)
                    if placement:
                        _, i = placement
                    width = group(text, i)
                    if width:
                        _, i = width
                elif name == "together":
                    for _ in range(2):
                        setting = optional_group(text, i)
                        if setting:
                            _, i = setting
                elif name in {"tabular", "tabularx"}:
                    width = group(text, i) if name == "tabularx" else None
                    if width:
                        _, i = width
                    preamble = group(text, i)
                    if preamble:
                        _, i = preamble
                elif name == "wrapfigure":
                    # A wrapped print sidebar is still part of the surrounding
                    # note in reflow. Consume its paper-only placement/width so
                    # strings such as ``{r}{.4\\linewidth}`` never leak.
                    placement = group(text, i)
                    if placement:
                        _, i = placement
                    width = group(text, i)
                    if width:
                        _, i = width
                    out.append('<span class="embedded-note">')
                if name in {"quote", "quotation"}:
                    # Raw blockquotes cannot be nested safely in Pandoc's
                    # inline footnote syntax. In compact contexts retain the
                    # quotation relationship as a block-like span.
                    out.append('<span class="quotation">' if compact else "\n\n> ")
                elif name in {"enumerate", "itemize"}:
                    out.append("\n\n")
                elif name in {"center", "flushleft", "flushright"}:
                    alignment = {"center": "center", "flushleft": "start", "flushright": "end"}[name]
                    tag = "span" if compact else "div"
                    out.append(f'<{tag} class="centered-block align-{alignment}">')
                elif name in {"table", "tabular", "tabularx"}:
                    # Layout environments have no ebook analogue; keep their text.
                    out.append("\n\n")
                continue
        if text.startswith("\\end{", i):
            env = group(text, i + 4)
            if env:
                name, i = env
                if name == "wrapfigure":
                    out.append("</span>")
                elif name in {"center", "flushleft", "flushright"}:
                    out.append("</span>" if compact else "</div>")
                elif name in {"quote", "quotation"} and compact:
                    out.append("</span>")
                else:
                    out.append("\n\n")
                continue
        if text[i] != "\\":
            if text[i] == "{":
                raw_group = group(text, i)
                if raw_group:
                    value, i = raw_group
                    out.append(tex_to_markdown(value, compact=compact))
                    continue
            if text[i] == "&":
                # An unescaped ampersand is TeX table scaffolding. Literal
                # prose ampersands are authored as \& and handled below.
                out.append("\n\n")
            elif text[i] == "$":
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
        # Starred layout commands have the same argument structure here. If
        # the star is left behind Markdown interprets it as emphasis and emits
        # visible strings such as "{2em}".
        if after < len(text) and text[after] == "*":
            after += 1
        if name in MATH_SYMBOLS:
            out.append(MATH_SYMBOLS[name]); i = after; continue
        if name in ZERO_ARGUMENT_TEXT:
            out.append(ZERO_ARGUMENT_TEXT[name]); i = after; continue
        if name in {"nl", "linebreak", "par", "medskip", "newpage", "clearpage", "pagebreak"}:
            if name == "pagebreak":
                setting = optional_group(text, after)
                if setting:
                    _, after = setting
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
                    "small", "large", "Large", "bfseries", "ttfamily", "selectfont",
                    "begingroup", "endgroup", "BookModeTextSizes"}:
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
        if name in {"setlength", "addtolength", "renewcommand", "newcommand"}:
            # Both arguments are print setup, never book content.
            second = group(text, end)
            i = second[1] if second else end
            continue
        if name == "Table":
            table_body = group(text, end)
            if table_body:
                table_body_value, end = table_body
                out.append(render_table(table_body_value, body, optional_value is not None))
            i = end
            continue
        if name == "egAbove":
            arguments = [body]
            cursor = end
            for _ in range(3):
                parsed = group(text, cursor)
                if not parsed:
                    break
                value, cursor = parsed
                arguments.append(value)
            if len(arguments) == 4:
                upper = tex_to_markdown(arguments[2]).strip()
                lower = tex_to_markdown(arguments[3]).strip()
                out.append(
                    '<span class="stacked-reading egyptian" lang="egy" role="group" '
                    f'aria-label="{html.escape(re.sub(r"<[^>]+>", "", upper + " " + lower), quote=True)}">'
                    f'<span>{upper}</span><span>{lower}</span></span>'
                )
                end = cursor
            i = end
            continue
        if name in {"Above", "Below"}:
            label_group = group(text, end)
            base_group = group(text, label_group[1]) if label_group else None
            if label_group and base_group:
                label = tex_to_markdown(label_group[0], compact=compact).strip()
                base = tex_to_markdown(base_group[0], compact=compact).strip()
                plain = re.sub(r"<[^>]+>", "", f"{label} {base}")
                out.append(
                    f'<ruby class="wtn-ruby ruby-{name.lower()}" '
                    f'aria-label="{html.escape(plain, quote=True)}">{base}'
                    f'<rp>(</rp><rt>{label}</rt><rp>)</rp></ruby>'
                )
                end = base_group[1]
            i = end
            continue
        if name in {"egScale", "egRaise"}:
            content = group(text, end)
            if content:
                value, end = content
                out.append(tex_to_markdown(value).strip())
            i = end
            continue
        if name == "egOverlap":
            first_rendered = tex_to_markdown(body).strip()
            second = group(text, end)
            if second:
                value, end = second
                out.append(
                    '<span class="glyph-overlap" role="img">'
                    f'<span>{first_rendered}</span><span>{tex_to_markdown(value).strip()}</span></span>'
                )
            else:
                out.append(first_rendered)
            i = end
            continue
        if name == "tikz":
            glyphs: list[str] = []
            cursor = 0
            while True:
                found = re.search(r"\\egyptNew\s*", body[cursor:])
                if not found:
                    break
                arg_at = cursor + found.end()
                parsed = group(body, arg_at)
                if not parsed:
                    break
                value, cursor = parsed
                glyphs.append(tex_to_markdown(value, compact=True).strip())
            if glyphs:
                layers = "".join(f"<span>{glyph}</span>" for glyph in glyphs)
                out.append(f'<span class="glyph-overlap egyptian" role="img">{layers}</span>')
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
                    f'\n\n<section class="definition {cls}">\n\n'
                    f'<p class="definition-heading"><dfn>{label}</dfn>{qualifier}.</p>\n\n'
                    f'<div class="definition-body">\n\n'
                    f'{tex_to_markdown(definition).strip()}\n\n'
                    f'</div>\n\n</section>\n\n'
                )
            else:
                out.append(f"<dfn>{label}</dfn>")
            i = end
            continue
        # Footnotes are an inline Markdown construct until Pandoc turns them
        # into EPUB asides. Compact conversion keeps nested print environments
        # from interrupting and visibly exposing that syntax.
        rendered = tex_to_markdown(
            body, compact=compact or name in {"footnote", "recursivefootnote", "hangingfootnote",
                                              "fA", "fB", "fC", "fAX", "fBX", "fCX"}
        ).strip()
        if name == "ruby":
            reading = group(text, end)
            if reading:
                reading_value, end = reading
                out.append(
                    '<ruby class="wtn-ruby">' + rendered
                    + '<rp>(</rp><rt>' + tex_to_markdown(reading_value, compact=True).strip()
                    + '</rt><rp>)</rp></ruby>'
                )
            else:
                out.append(rendered)
            i = end
            continue
        if name == "egMirror":
            out.append(f'<span class="glyph-mirror">{rendered}</span>')
            i = end
            continue
        src = source_class(name)
        if src:
            language, key = src
            attrs = ' lang="he" dir="rtl"' if language == "hebrew" else ""
            label = html.escape(SOURCE_NAMES[key])
            if language == "hebrew":
                rendered = historical_hebrew(rendered, key)
            is_block = any(marker in rendered for marker in ("<div ", "<table", "WTNTABLERUN"))
            if is_block:
                # HTML tables/divs cannot legally be children of an inline
                # source span. Their cells retain their own semantic markup.
                out.append(rendered)
            else:
                rendered = re.sub(r"\s*\n\s*", " ", rendered)
                tag = "bdo" if language == "hebrew" and key in LEGACY_LTR_CODEPOINT_SOURCE_KEYS else "span"
                out.append(f'<{tag} class="source source-{key.lower()} {language}"{attrs} data-source="{label}">{rendered}</{tag}>')
        elif name in COMMENTARY or re.fullmatch(r"a(?:A|B|C|J|E|P|DtrA|DtrB|Dtn|R|RJE|Records|Other)[lcr]", name):
            has_alignment_suffix = name not in COMMENTARY
            base_name = name[:-1] if has_alignment_suffix else name
            cls = COMMENTARY.get(base_name, "annotation")
            alignment = (
                {"l": "start", "c": "center", "r": "end"}[name[-1]]
                if has_alignment_suffix else "start"
            )
            if "^[" in rendered:
                # A display annotation around a footnote is a TeX color scope,
                # not part of the note's content model. Wrapping Pandoc's note
                # token in HTML would move unmatched tags into the footnote.
                # Carry the enclosing speaker colour into Pandoc's detached
                # footnote aside. The surrounding verse gets the same colour
                # class in make_markdown when this wrapper owns the whole note.
                out.append(color_footnote_tokens(rendered, cls))
            elif any(marker in rendered for marker in ("<div ", "<table", "WTNTABLERUN")):
                out.append(rendered)
            elif "\n\n" in rendered:
                out.append(annotation_block(rendered, cls, alignment))
            else:
                note = re.sub(r"\s*\n\s*", " ", rendered)
                out.append(f'<span class="annotation {cls} align-{alignment}" role="note">{note}</span>')
        elif name in {"fA", "fB", "fC", "fAX", "fBX", "fCX"}:
            voice = name[1]
            if "annotation-paragraph" in rendered:
                rendered = re.sub(r"</?span(?:\s[^>]*)?>", "", rendered)
            if any(tag in rendered for tag in ("<div ", "<table", "<figure", "WTNTABLERUN")) or "\n\n" in rendered:
                # Pandoc's inline-note syntax cannot legally contain a span
                # wrapped around block HTML. The blocks retain their own source
                # classes; keeping valid note structure takes precedence.
                if out:
                    out[-1] = out[-1].rstrip()
                out.append(f"^[{rendered}]")
            else:
                if out:
                    out[-1] = out[-1].rstrip()
                out.append(f'^[<span class="footnote-voice annotation-{voice.lower()}">{rendered}</span>]')
        elif name == "recursivefootnote" and compact:
            # EPUB/HTML footnotes cannot contain another noteref/aside pair.
            # Preserve a recursive print note in place inside its parent note
            # instead of letting Pandoc generate a self-referential duplicate
            # fnref id.
            out.append(f'<span class="nested-footnote">[{rendered}]</span>')
        elif name == "footnote" or name in {"recursivefootnote", "hangingfootnote"}:
            if "annotation-paragraph" in rendered:
                rendered = re.sub(r"</?span(?:\s[^>]*)?>", "", rendered)
            if out:
                out[-1] = out[-1].rstrip()
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
            elif name == "paleo" or name == "Paleo": attrs = ' class="paleo" lang="he" dir="rtl"'
            elif name == "textsc": attrs = ' class="smallcaps"'
            elif name == "redacted": attrs = ' class="redacted"'
            out.append(f"<{tag}{attrs}>{rendered}</{tag}>")
        elif name in {"includegraphics", "image"}:
            path = resolve_image_path(body.strip())
            if path is not None:
                alt = html.escape(path.stem.replace("-", " ").replace("_", " "))
                source_path = path.relative_to(ROOT).as_posix()
                if compact:
                    out.append(
                        f'<img class="embedded-note-image" src="{html.escape(source_path)}" alt="{alt}"/>'
                    )
                else:
                    out.append(f'\n\n<figure><img src="{html.escape(source_path)}" alt="{alt}"/></figure>\n\n')
        elif name == "hspace":
            # A handful of flush-left rhetorical diagrams use positive em
            # indentation to show logical nesting. Preserve that information
            # with bounded relative spacing; discard all other paper geometry.
            indent = re.fullmatch(r"\+?([246])(?:\.0)?em", body.strip())
            if indent:
                out.append(f'<span class="indent-{indent.group(1)}" aria-hidden="true"></span>')
            i = end
            continue
        elif name == "vspace":
            i = end
            continue
        elif name in {"raisebox", "makebox", "rotatebox", "size", "up", "dn"}:
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
    # TeX's `%` commonly suppresses whitespace before a footnote marker. The
    # comment is gone by this stage, so enforce the same attachment directly.
    result = re.sub(r"[ \t\r\n]+\^\[", "^[", result)
    # TeX turns an uncommented line ending between words into one interword
    # space. Commented endings have already been removed by strip_comments and
    # therefore leave the source spans directly adjacent.
    result = re.sub(
        r'(</span>)[ \t]*\r?\n[ \t]*(?=<span class="source\b)', r"\1 ", result,
    )
    if compact:
        result = re.sub(r"\s*\n\s*", " ", result)
    for number, math in enumerate(math_runs):
        result = result.replace(f"WTNMATHRUN{number}TOKEN", math)
    # Containers are appended after their child tables and can therefore
    # introduce earlier tokens when restored. Expand parents first.
    for number in range(len(table_runs) - 1, -1, -1):
        table = table_runs[number]
        result = result.replace(f"WTNTABLERUN{number}TOKEN", table)
    for number, diagram in enumerate(tikz_runs):
        result = result.replace(f"WTNTIKZRUN{number}TOKEN", diagram)
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


def chapter_heading(book: str, chapter: str) -> str:
    r"""The running chapter page follows \Chapter, not the summary-only ToC."""
    return f"{book} {chapter}"


def front_matter(
    sequence: list[tuple[str, str]],
    summaries: dict[tuple[str, str], str],
    edition_title: str = "Complete Edition",
) -> list[str]:
    """Reproduce the visible front matter from master.tex in reflowable form."""
    e_alphabet = historical_hebrew("אבגדהוזחטיכלמנסעפצקרשת", "E")
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
        f'<div class="title-book">{html.escape(edition_title)}</div>',
        '</section>', "",
        '# The History of the Alphabet {.front-heading .alphabet-heading}', "",
        '<div class="alphabet-page" dir="rtl" epub:type="frontmatter">',
        '<p class="alphabet paleo" lang="he" dir="rtl">אבגדהוזחטיכלמנסעפצקרשת</p>',
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
        '<dt><span class="source source-r">Highlights</span></dt><dd><span class="source source-r">Editors. Called Redactors in bible circles, since E was already taken. Redactors mostly insert glue prose when combining sources.</span></dd>',
        '<dt class="source source-bookofrecords">Record Grey</dt><dd class="source source-bookofrecords">Records. Begat lists, genealogies, and miscellaneous documents.</dd>',
        '</dl>', "",
        '# The Source Fonts {.front-heading}', "",
        '<div class="font-legend"><p class="source source-j hebrew" lang="he" dir="rtl">אבגדהוזחטיכלמנסעפצקרשת</p><p class="source source-j">J is written in the Paleo-Hebrew script of around 922 B.C.</p>',
        f'<p><bdo class="source source-e hebrew" lang="he" dir="rtl">{e_alphabet}</bdo></p><p class="source source-e">E uses a northern variant of the Paleo-Hebrew script from soon after the time of J.</p>',
        '<p class="source source-p hebrew" dir="rtl">אֲבֱגֶּדֲהֹוּזֻחִטֳיִּכֻלֵּמֱנָסֶעֲפֹצֻקָרֶשְּׁתֽ</p><p class="source source-p">P is rendered in the modern Hebrew square script with niqqud.</p>',
        '<p><span class="source source-r hebrew" dir="rtl">אבגדהוזחטיכלמנסעפצקרשת</span></p><p><span class="source source-r">R uses the Ezra variant of the Hebrew square script with no niqqud.</span></p></div>', "",
        '# Publication Notice {.front-heading .visually-hidden}', "",
        '<div class="publication-notice"><p><span class="aside-a">LD LLC makes no claim to have written the book that follows.<br/>We could not find a published edition of it, and thought one<br/>ought to exist. LD undertook the preparation of the text for<br/>publication, including its editing, typesetting, design, and</span><br/><span class="aside-b">production and is responsible for the volume presented here,<br/>but we make no claim to know the identity of the individuals<br/>who wrote the original text, nor do we make any claim to the<br/>effect that the original authors did not incorporate in that</span><br/><span class="aside-c">volume any earlier sources either verbatim or in paraphrase.<br/>In summary, it’s a bible, and all rules of that genre apply.<br/>If your work has been incorporated into the resulting volume<br/>and you would like to be removed from the bible, let us know</span></p>',
        '<img class="publication-logo" src="img/ld-book-light.png" alt="LD"/></div>', "",
    ]


def make_markdown(path: Path, selected_book: str | None = None) -> tuple[int, int]:
    sequence = master_sequence(selected_book)
    summaries = chapter_summaries()
    edition_title = selected_book or "Complete Edition"
    lines = ["---", "lang: en-US", "---", ""] + front_matter(
        sequence, summaries, edition_title
    )
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
        heading = chapter_heading(book, chapter)
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
            rendered_english = tex_to_markdown(english)
            rendered_hebrew = tex_to_markdown(hebrew)
            if book == "Genesis" and chapter == "3" and number.strip() == "6":
                rendered_english = re.sub(r"\s*<br\s*/?>\s*", " ", rendered_english)
                rendered_hebrew = re.sub(r"\s*<br\s*/?>\s*", " ", rendered_hebrew)
            lines += [
                f':::::: {{.verse #{verse_anchor}}}',
                f'<p id="{verse_anchor}-number" class="verse-reference">{book} {chapter}:{number}</p>',
                "::::: {.verse-translation}", rendered_english, ":::::",
                '::::: {.verse-source lang="he" dir="rtl"}', rendered_hebrew, ":::::",
            ]
            rendered_commentary = tex_to_markdown(commentary)
            if rendered_commentary:
                whole_voice = re.fullmatch(r"\s*\\a([ABC])\s*\{.*\}\s*", strip_comments(commentary), re.DOTALL)
                voice_class = f" .annotation-{whole_voice.group(1).lower()}" if whole_voice else ""
                lines += [f"::::: {{.verse-commentary{voice_class}}}", rendered_commentary, ":::::"]
            lines += ["::::::", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return chapter_count, verse_count


def postprocess_epub(path: Path) -> None:
    """Apply fixes that require access to Pandoc's packaged EPUB."""
    with zipfile.ZipFile(path, "r") as source:
        entries = [(info, source.read(info.filename)) for info in source.infolist()]
    rewritten: list[tuple[zipfile.ZipInfo, bytes]] = []
    for info, payload in entries:
        if info.filename.endswith("content.opf"):
            package = payload.decode("utf-8")
            invalid_ids = {
                value: "wtn-" + re.sub(r"[^A-Za-z0-9_.-]", "-", value)
                for value in re.findall(r'\bid="([^"]+)"', package)
                if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", value)
            }
            for old, new in invalid_ids.items():
                package = package.replace(f'id="{old}"', f'id="{new}"')
                for attribute in ("idref", "fallback", "media-overlay", "unique-identifier"):
                    package = package.replace(f'{attribute}="{old}"', f'{attribute}="{new}"')
            rewritten.append((info, package.encode("utf-8")))
            continue
        if not info.filename.endswith((".xhtml", ".html")):
            rewritten.append((info, payload))
            continue
        document = payload.decode("utf-8")
        voices: dict[str, str] = {}
        def mark_aside(match: re.Match[str]) -> str:
            opening, note_id, body = match.groups()
            voice_match = re.search(r'footnote-voice[^"<]*\bannotation-([abc])\b', body)
            if not voice_match:
                return match.group(0)
            voice = voice_match.group(1)
            voices[note_id] = voice
            voice_class = f"footnote-{voice}"
            opening = opening[:-1] + f' class="{voice_class}">'
            body = re.sub(
                r'(class="footnote-back)(")', rf'\1 {voice_class}\2', body, count=1,
            )
            return opening + body

        document = re.sub(
            r'(<aside\b[^>]*\bid="(fn\d+)"[^>]*>)(.*?</aside>)',
            mark_aside, document, flags=re.DOTALL,
        )
        for note_id, voice in voices.items():
            voice_class = f"footnote-{voice}"
            document = re.sub(
                rf'(<a\b[^>]*href="#{note_id}"\s+class="footnote-ref)(")',
                rf'\1 {voice_class}\2', document,
            )
        rewritten.append((info, document.encode("utf-8")))
    temporary = path.with_suffix(path.suffix + ".tmp")
    with zipfile.ZipFile(temporary, "w") as target:
        for info, payload in rewritten:
            if info.filename == "mimetype":
                info.compress_type = zipfile.ZIP_STORED
            target.writestr(info, payload)
    temporary.replace(path)


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
        cover = ROOT / "img/covers/we-cover-3.png"
        cmd = ["pandoc", str(manuscript), "--from=markdown+fenced_divs+footnotes+raw_html+markdown_in_html_blocks",
               "--to=epub3", "--output", str(args.output), "--standalone",
               "--toc", "--toc-depth=2", "--split-level=1", "--css", str(HERE / "epub.css"),
               "--metadata-file", str(HERE / "metadata.yaml"), "--epub-title-page=false",
               "--epub-cover-image", str(cover)]
        for key, value in publication_metadata(args.book).items():
            cmd += [f"--metadata={key}:{value}"]
        for font in FONT_FILES:
            cmd += ["--epub-embed-font", str(font)]
        log(f"Using cover image: {cover}")
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
        postprocess_epub(args.output)
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
