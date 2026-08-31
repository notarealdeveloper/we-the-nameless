"""A conservative TeX parser specialized for source-colored verse corpora.

It is intentionally not a TeX engine. It recognizes balanced groups, comments,
commands, and the paired ``\\hSOURCE{...}`` / ``\\eSOURCE{...}`` convention.
Unknown formatting commands are transparent when they wrap text; annotation
commands are excluded from extracted verse text but remain in ``Verse.raw_tex``.
"""
from __future__ import annotations

import hashlib
import re
from functools import lru_cache
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Sequence

from .model import Span, Verse


@dataclass(frozen=True)
class Node:
    start: int
    end: int


@dataclass(frozen=True)
class TextNode(Node):
    text: str


@dataclass(frozen=True)
class CommandNode(Node):
    name: str


@dataclass(frozen=True)
class GroupNode(Node):
    children: tuple[Node, ...]
    opener: str = "{"
    closer: str = "}"


@dataclass
class ParseWarning:
    path: str
    offset: int
    message: str


class TexSyntaxError(ValueError):
    pass


class TexParser:
    def __init__(self, text: str, *, path: str = "<string>", strict: bool = False) -> None:
        self.text = text
        self.path = path
        self.strict = strict
        self.pos = 0
        self.warnings: list[ParseWarning] = []

    def parse(self) -> tuple[Node, ...]:
        self.pos = 0
        return tuple(self._sequence(None))

    def _warn(self, offset: int, message: str) -> None:
        warning = ParseWarning(self.path, offset, message)
        self.warnings.append(warning)
        if self.strict:
            raise TexSyntaxError(f"{self.path}:{offset}: {message}")

    def _sequence(self, closer: str | None) -> list[Node]:
        nodes: list[Node] = []
        text_start: int | None = None
        text_parts: list[str] = []

        def flush() -> None:
            nonlocal text_start, text_parts
            if text_start is not None and text_parts:
                nodes.append(TextNode(text_start, self.pos, "".join(text_parts)))
            text_start = None
            text_parts = []

        while self.pos < len(self.text):
            char = self.text[self.pos]
            if closer is not None and char == closer:
                flush()
                return nodes
            if char == "%":
                flush()
                # Unescaped % starts a comment. Keep the newline as whitespace.
                while self.pos < len(self.text) and self.text[self.pos] not in "\r\n":
                    self.pos += 1
                if self.pos < len(self.text):
                    start = self.pos
                    if self.text[self.pos] == "\r":
                        self.pos += 1
                    if self.pos < len(self.text) and self.text[self.pos] == "\n":
                        self.pos += 1
                    nodes.append(TextNode(start, self.pos, "\n"))
                continue
            # Square brackets in this corpus frequently mark reconstructed
            # Hebrew and must remain visible. Treat them as optional-argument
            # groups only immediately after a command (or another option group).
            significant = next(
                (
                    prior
                    for prior in reversed(nodes)
                    if not (isinstance(prior, TextNode) and not prior.text.strip())
                ),
                None,
            )
            pending_visible_text = text_start is not None and bool("".join(text_parts).strip())
            optional = char == "[" and not pending_visible_text and (
                isinstance(significant, CommandNode)
                or (isinstance(significant, GroupNode) and significant.opener == "[")
            )
            if char == "{" or optional:
                flush()
                start = self.pos
                opening = char
                closing = "}" if char == "{" else "]"
                self.pos += 1
                children = tuple(self._sequence(closing))
                if self.pos < len(self.text) and self.text[self.pos] == closing:
                    self.pos += 1
                else:
                    self._warn(start, f"Unclosed group beginning with {opening!r}")
                nodes.append(GroupNode(start, self.pos, children, opening, closing))
                continue
            if char == "}" or (char == "]" and closer == "]"):
                if closer is None:
                    if text_start is None:
                        text_start = self.pos
                    text_parts.append(char)
                    self._warn(self.pos, f"Unmatched closing delimiter {char!r}")
                    self.pos += 1
                    continue
                flush()
                self._warn(self.pos, f"Expected {closer!r}, found {char!r}")
                return nodes
            if char == "\\":
                flush()
                start = self.pos
                self.pos += 1
                if self.pos >= len(self.text):
                    nodes.append(CommandNode(start, self.pos, ""))
                    continue
                if self.text[self.pos].isalpha() or self.text[self.pos] == "@":
                    name_start = self.pos
                    while self.pos < len(self.text) and (
                        self.text[self.pos].isalpha() or self.text[self.pos] in "@:_"
                    ):
                        self.pos += 1
                    # The corpus uses conceptual source names containing digits,
                    # even though classic TeX control words normally do not.
                    while self.pos < len(self.text) and self.text[self.pos].isdigit():
                        self.pos += 1
                    name = self.text[name_start : self.pos]
                    # TeX swallows whitespace after a control word. Retain a single
                    # logical separator only through surrounding source blocks.
                    while self.pos < len(self.text) and self.text[self.pos] in " \t":
                        self.pos += 1
                else:
                    name = self.text[self.pos]
                    self.pos += 1
                nodes.append(CommandNode(start, self.pos, name))
                continue
            if text_start is None:
                text_start = self.pos
            text_parts.append(char)
            self.pos += 1
        flush()
        if closer is not None:
            self._warn(self.pos, f"Unclosed group; expected {closer!r}")
        return nodes


@lru_cache(maxsize=128)
def parse_tex(text: str, *, path: str = "<string>", strict: bool = False) -> tuple[Node, ...]:
    # Verse extraction asks for Hebrew and English from the same fragment back to
    # back; a small cache avoids parsing each balanced-brace tree twice.
    return TexParser(text, path=path, strict=strict).parse()


def iter_nodes(nodes: Iterable[Node]) -> Iterator[Node]:
    for node in nodes:
        yield node
        if isinstance(node, GroupNode):
            yield from iter_nodes(node.children)


def command_names(text: str) -> set[str]:
    return {node.name for node in iter_nodes(parse_tex(text)) if isinstance(node, CommandNode)}


FALSE_SIDE_MACROS = {
    "heb",
    "hebrew",
    "hspace",
    "hfill",
    "href",
    "emph",
    "ensuremath",
    "enumerate",
    "equation",
}

KNOWN_SOURCE_SUFFIXES = {
    "J",
    "E",
    "P",
    "R",
    "RJE",
    "Other",
    "Proto",
    "D",
    "Dtn",
    "Dtr",
    "Dtr1",
    "Dtr2",
    "DH",
}


def discover_source_suffixes(texts: Iterable[str]) -> set[str]:
    h: set[str] = set()
    e: set[str] = set()
    for text in texts:
        for name in command_names(text):
            if name in FALSE_SIDE_MACROS or len(name) < 2:
                continue
            if name.startswith("h") and name[1:2].isupper():
                h.add(name[1:])
            elif name.startswith("e") and name[1:2].isupper():
                e.add(name[1:])
    return (h & e) | (KNOWN_SOURCE_SUFFIXES & (h | e))


@dataclass
class _Buffer:
    chars: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    macros: list[str | None] = field(default_factory=list)

    def append(self, text: str, source: str, macro: str | None = None) -> None:
        for char in text:
            self.chars.append(char)
            self.sources.append(source)
            self.macros.append(macro)

    @property
    def text(self) -> str:
        return "".join(self.chars)

    def finish(self) -> tuple[str, tuple[Span, ...]]:
        # Normalize typographic TeX conventions before whitespace compaction.
        replacements = {
            "---": "—",
            "--": "–",
            "``": "“",
            "''": "”",
            "~": " ",
            "\u00a0": " ",
        }
        chars = self.chars
        sources = self.sources
        macros = self.macros
        for old, new in replacements.items():
            i = 0
            while i <= len(chars) - len(old):
                if "".join(chars[i : i + len(old)]) == old:
                    source = sources[i] if i < len(sources) else "Unknown"
                    macro = macros[i] if i < len(macros) else None
                    chars[i : i + len(old)] = list(new)
                    sources[i : i + len(old)] = [source] * len(new)
                    macros[i : i + len(old)] = [macro] * len(new)
                i += 1

        clean_chars: list[str] = []
        clean_sources: list[str] = []
        clean_macros: list[str | None] = []
        pending_space: tuple[str, str | None] | None = None
        for char, source, macro in zip(chars, sources, macros):
            if char.isspace():
                if clean_chars:
                    pending_space = (source, macro)
                continue
            if pending_space is not None and clean_chars:
                clean_chars.append(" ")
                clean_sources.append(pending_space[0])
                clean_macros.append(pending_space[1])
                pending_space = None
            clean_chars.append(char)
            clean_sources.append(source)
            clean_macros.append(macro)
        text = "".join(clean_chars)
        spans: list[Span] = []
        if text:
            start = 0
            current_source = clean_sources[0]
            current_macro = clean_macros[0]
            for i in range(1, len(text)):
                if clean_sources[i] != current_source or clean_macros[i] != current_macro:
                    spans.append(Span(start, i, current_source, current_macro))
                    start = i
                    current_source = clean_sources[i]
                    current_macro = clean_macros[i]
            spans.append(Span(start, len(text), current_source, current_macro))
        return text, tuple(spans)


SKIP_COMMANDS = {
    "aA",
    "aB",
    "aC",
    "fA",
    "fB",
    "fC",
    "footnote",
    "footnotemark",
    "marginpar",
    "label",
    "index",
    "Table",
    "caption",
    "todo",
    "textsuperscript",
}

TRANSPARENT_COMMANDS = {
    "emph",
    "textit",
    "textbf",
    "textnormal",
    "textrm",
    "textsf",
    "texttt",
    "uline",
    "underline",
    "mbox",
    "makebox",
    "parbox",
    "small",
    "large",
    "Large",
    "LARGE",
    "tiny",
    "scriptsize",
    "footnotesize",
    "normalsize",
    "heb",
    "egypt",
    "foreignlanguage",
    "textcolor",
    "colorbox",
    "href",
}

# Number of braced arguments; the last is textual for transparent commands.
COMMAND_ARITY = {
    "href": 2,
    "foreignlanguage": 2,
    "textcolor": 2,
    "colorbox": 2,
    "makebox": 1,
    "parbox": 2,
    "begin": 1,
    "end": 1,
    "label": 1,
    "index": 1,
    "footnote": 1,
    "textsuperscript": 1,
    "Table": 2,
}

SPECIAL_COMMANDS = {
    "\\": " ",
    " ": " ",
    ",": " ",
    ";": " ",
    "!": "",
    "%": "%",
    "&": "&",
    "_": "_",
    "#": "#",
    "$": "$",
    "{": "{",
    "}": "}",
    "textbackslash": "\\",
    "ldots": "…",
    "dots": "…",
    "textemdash": "—",
    "textendash": "–",
    "YHWH": "YHWH",
    "JHWH": "YHWH",
    "yhwh": "YHWH",
    "LORD": "LORD",
    "Lord": "Lord",
    "par": " ",
    "newline": " ",
    "textquotedblleft": "“",
    "textquotedblright": "”",
    "textquoteleft": "‘",
    "textquoteright": "’",
}


def _next_groups(nodes: Sequence[Node], index: int, limit: int | None = None) -> tuple[list[GroupNode], int]:
    groups: list[GroupNode] = []
    cursor = index + 1
    while cursor < len(nodes):
        node = nodes[cursor]
        if isinstance(node, TextNode) and not node.text.strip():
            cursor += 1
            continue
        if isinstance(node, GroupNode) and node.opener == "{":
            groups.append(node)
            cursor += 1
            if limit is not None and len(groups) >= limit:
                break
            continue
        # Optional groups do not count as required args, but are consumed.
        if isinstance(node, GroupNode) and node.opener == "[":
            cursor += 1
            continue
        break
    return groups, cursor


def _group_literal(group: GroupNode, original: str) -> str:
    return original[group.start + 1 : max(group.start + 1, group.end - 1)].strip()


def _decode_text(value: str) -> str:
    # Escaped special characters are represented as CommandNodes; this handles
    # only plain text left by the scanner.
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _render_nodes(
    nodes: Sequence[Node],
    *,
    side: str,
    suffixes: set[str],
    active_source: str,
    active_macro: str,
    buffer: _Buffer,
) -> None:
    i = 0
    while i < len(nodes):
        node = nodes[i]
        if isinstance(node, TextNode):
            buffer.append(_decode_text(node.text), active_source, active_macro)
            i += 1
            continue
        if isinstance(node, GroupNode):
            _render_nodes(
                node.children,
                side=side,
                suffixes=suffixes,
                active_source=active_source,
                active_macro=active_macro,
                buffer=buffer,
            )
            i += 1
            continue
        assert isinstance(node, CommandNode)
        groups, cursor = _next_groups(nodes, i, 1)
        name = node.name
        if len(name) > 1 and name[0] in "he" and name[1:] in suffixes:
            if groups:
                if name[0] == side:
                    _render_nodes(
                        groups[0].children,
                        side=side,
                        suffixes=suffixes,
                        active_source=name[1:],
                        active_macro=name,
                        buffer=buffer,
                    )
                # A source block from the opposite language is ignored.
                i = cursor
                continue
        if name in SKIP_COMMANDS:
            arity = COMMAND_ARITY.get(name, 1)
            used, cursor2 = _next_groups(nodes, i, arity)
            i = cursor2 if used else i + 1
            continue
        if name in ("begin", "end"):
            used, cursor2 = _next_groups(nodes, i, 1)
            buffer.append(" ", active_source, active_macro)
            i = cursor2 if used else i + 1
            continue
        if name in SPECIAL_COMMANDS:
            buffer.append(SPECIAL_COMMANDS[name], active_source, active_macro)
            i += 1
            continue
        if groups:
            arity = COMMAND_ARITY.get(name, len(groups) if name in TRANSPARENT_COMMANDS else 1)
            used, cursor2 = _next_groups(nodes, i, arity)
            if used:
                # For two-argument wrappers (language/color/href), only the last
                # argument is displayed. For unknown one-argument wrappers, the
                # argument is treated as transparent rather than discarded.
                target = used[-1]
                _render_nodes(
                    target.children,
                    side=side,
                    suffixes=suffixes,
                    active_source=active_source,
                    active_macro=active_macro,
                    buffer=buffer,
                )
                i = cursor2
                continue
        # A parameterless all-uppercase semantic macro is usually intended as
        # visible text (e.g. custom divine-name macros).
        if name and (name.isupper() or name in {"God", "Lord", "Adonai"}):
            buffer.append(name, active_source, active_macro)
        i += 1


def extract_language(
    text: str,
    *,
    side: str,
    suffixes: Iterable[str],
    path: str = "<string>",
) -> tuple[str, tuple[Span, ...]]:
    """Extract one language and its nested source spans from a verse fragment."""
    suffix_set = set(suffixes)
    nodes = parse_tex(text, path=path)
    buffer = _Buffer()

    def walk_outer(sequence: Sequence[Node]) -> None:
        i = 0
        while i < len(sequence):
            node = sequence[i]
            if isinstance(node, CommandNode):
                groups, cursor = _next_groups(sequence, i, 1)
                name = node.name
                # Commentary/footnote blocks can themselves quote source macros;
                # they are not verse text and must not leak into extraction.
                if name in SKIP_COMMANDS:
                    arity = COMMAND_ARITY.get(name, 1)
                    used, skipped_to = _next_groups(sequence, i, arity)
                    i = skipped_to if used else i + 1
                    continue
                if (
                    len(name) > 1
                    and name[0] in "he"
                    and name[1:] in suffix_set
                    and groups
                ):
                    if name[0] == side:
                        # Preserve a logical separator between distinct outer
                        # blocks. Nested changes are rendered without insertion.
                        if buffer.chars and not buffer.chars[-1].isspace():
                            buffer.append(" ", name[1:], name)
                        _render_nodes(
                            groups[0].children,
                            side=side,
                            suffixes=suffix_set,
                            active_source=name[1:],
                            active_macro=name,
                            buffer=buffer,
                        )
                    i = cursor
                    continue
            if isinstance(node, GroupNode):
                walk_outer(node.children)
            i += 1

    walk_outer(nodes)
    return buffer.finish()


BOOK_ALIASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Genesis", ("genesis", "gen", "בראשית")),
    ("Exodus", ("exodus", "exod", "exo", "שמות")),
    ("Leviticus", ("leviticus", "lev", "ויקרא")),
    ("Numbers", ("numbers", "num", "במדבר")),
    ("Deuteronomy", ("deuteronomy", "deut", "deu", "דברים")),
    ("Joshua", ("joshua", "josh", "יהושע")),
    ("Judges", ("judges", "judg", "שופטים")),
    ("1 Samuel", ("1-samuel", "1samuel", "1-sam", "1sam", "samuel-1")),
    ("2 Samuel", ("2-samuel", "2samuel", "2-sam", "2sam", "samuel-2")),
    ("1 Kings", ("1-kings", "1kings", "1-kgs", "1kgs", "kings-1")),
    ("2 Kings", ("2-kings", "2kings", "2-kgs", "2kgs", "kings-2")),
)


def infer_book(path: str | Path, text: str = "") -> str:
    value = str(path).replace("_", "-").lower()
    compact = re.sub(r"[^a-z0-9א-ת]+", "-", value)
    # Split Samuel/Kings directories commonly encode the part in the filename.
    name = Path(path).name.lower()
    if "samuel" in compact or re.search(r"(?:^|/)08-samuel", value):
        if re.match(r"2[-_.]", name) or "/2-" in value:
            return "2 Samuel"
        if re.match(r"1[-_.]", name) or "/1-" in value:
            return "1 Samuel"
    if "kings" in compact or re.search(r"(?:^|/)09-kings", value):
        if re.match(r"2[-_.]", name) or "/2-" in value:
            return "2 Kings"
        if re.match(r"1[-_.]", name) or "/1-" in value:
            return "1 Kings"
    for book, aliases in BOOK_ALIASES:
        if any(re.search(rf"(?:^|-){re.escape(alias)}(?:-|$)", compact) for alias in aliases):
            return book
    match = re.search(r"\\Book\s*\{([^{}]+)\}", text)
    if match:
        return match.group(1).strip()
    parent = Path(path).parent.name
    parent = re.sub(r"^\d+[-_.]*", "", parent).replace("-", " ").replace("_", " ")
    return parent.title() or "Unknown"


@dataclass(frozen=True)
class ParsedFile:
    path: str
    book: str
    verses: tuple[Verse, ...]
    source_suffixes: tuple[str, ...]
    warnings: tuple[ParseWarning, ...] = ()
    sha256: str = ""


def _top_level_events(nodes: Sequence[Node], original: str) -> list[tuple[int, str, str, int]]:
    events: list[tuple[int, str, str, int]] = []
    for i, node in enumerate(nodes):
        if not isinstance(node, CommandNode) or node.name not in {"Chapter", "Verse"}:
            continue
        groups, cursor = _next_groups(nodes, i, 1)
        if not groups:
            continue
        value = _group_literal(groups[0], original)
        content_start = groups[0].end
        events.append((node.start, node.name, value, content_start))
    return events


def parse_tex_file(
    path: str | Path,
    *,
    source_suffixes: Iterable[str] | None = None,
    strict: bool = False,
    encoding: str = "utf-8",
) -> ParsedFile:
    target = Path(path)
    text = target.read_text(encoding=encoding, errors="replace")
    parser = TexParser(text, path=str(target), strict=strict)
    nodes = parser.parse()
    suffixes = set(source_suffixes or discover_source_suffixes([text]))
    book = infer_book(target, text)
    events = _top_level_events(nodes, text)
    chapter: int | None = None
    verses: list[Verse] = []
    ordinals: dict[tuple[int, str], int] = {}
    for event_index, (start, kind, value, content_start) in enumerate(events):
        if kind == "Chapter":
            number = re.search(r"\d+", value)
            if number:
                chapter = int(number.group())
            continue
        if chapter is None:
            # Fall back to a chapter number encoded by the filename.
            numbers = re.findall(r"\d+", target.stem)
            if numbers:
                chapter = int(numbers[-1])
            else:
                parser._warn(start, "Verse encountered before chapter could be inferred")
                chapter = 0
        end = events[event_index + 1][0] if event_index + 1 < len(events) else len(text)
        fragment = text[content_start:end]
        hebrew, h_spans = extract_language(
            fragment, side="h", suffixes=suffixes, path=str(target)
        )
        english, e_spans = extract_language(
            fragment, side="e", suffixes=suffixes, path=str(target)
        )
        verse_number = value.strip()
        key = (chapter, verse_number)
        ordinal = ordinals.get(key, 0)
        ordinals[key] = ordinal + 1
        verses.append(
            Verse(
                book=book,
                chapter=chapter,
                number=verse_number,
                hebrew=hebrew,
                english=english,
                hebrew_spans=h_spans,
                english_spans=e_spans,
                path=str(target),
                raw_tex=text[start:end],
                ordinal=ordinal,
                metadata={"file_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()},
            )
        )
    return ParsedFile(
        str(target),
        book,
        tuple(verses),
        tuple(sorted(suffixes)),
        tuple(parser.warnings),
        hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )
