"""Pure string normalization, tokenization, and match-index projection.

This module deliberately knows nothing about TeX or Bible objects. It is useful
for arbitrary strings and is the layer on which corpus search is built.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Iterator, Pattern

from .config import get_niqqud

HEBREW_START = "\u0590"
HEBREW_END = "\u05ff"
MATRES = frozenset("אהוי")
TOKEN_RE = re.compile(r"\S+", flags=re.UNICODE)


class MatresMode(str, Enum):
    KEEP = "keep"
    INTERNAL = "internal"
    ALL = "all"

    @classmethod
    def coerce(cls, value: "MatresMode | str | bool | None") -> "MatresMode":
        if value in (None, False, "keep", "none", "false"):
            return cls.KEEP
        if value in (True, "all", "true"):
            return cls.ALL
        if value in ("internal", "inside"):
            return cls.INTERNAL
        return cls(str(value).lower())


@dataclass(frozen=True)
class NormalizedText:
    text: str
    # One original code-point offset for each normalized code point.
    index: tuple[int, ...]
    original: str

    def original_span(self, start: int, end: int) -> tuple[int, int]:
        if start < 0 or end < start or end > len(self.text):
            raise IndexError((start, end, len(self.text)))
        if start == end:
            if not self.index:
                return (0, 0)
            if start == len(self.index):
                return (len(self.original), len(self.original))
            pos = self.index[start]
            return (pos, pos)
        original_start = self.index[start]
        original_end = self.index[end - 1] + 1
        # When ignored combining marks trail the final matched base, include the
        # complete original grapheme in the projected match span.
        while original_end < len(self.original) and unicodedata.category(
            self.original[original_end]
        ).startswith("M"):
            original_end += 1
        return original_start, original_end


@dataclass(frozen=True)
class TextMatch:
    start: int
    end: int
    normalized_start: int
    normalized_end: int
    text: str
    normalized_text: str
    groups: tuple[str | None, ...] = ()


def is_hebrew_mark(char: str) -> bool:
    cp = ord(char)
    return 0x0591 <= cp <= 0x05C7 and unicodedata.category(char).startswith("M")


def strip_niqqud(text: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFD", text) if not is_hebrew_mark(ch))


def _decomposed(text: str) -> Iterator[tuple[str, int]]:
    for offset, char in enumerate(text):
        for piece in unicodedata.normalize("NFD", char):
            yield piece, offset


def _internal_mater_offsets(text: str) -> set[int]:
    remove: set[int] = set()
    for match in TOKEN_RE.finditer(text):
        bases = [
            i
            for i in range(match.start(), match.end())
            if not is_hebrew_mark(text[i]) and not text[i].isspace()
        ]
        if len(bases) < 3:
            continue
        for i in bases[1:-1]:
            if text[i] in MATRES:
                remove.add(i)
    return remove


def normalize_hebrew_with_map(
    text: str,
    *,
    niqqud: bool | None = None,
    spaces: bool = False,
    matres: MatresMode | str | bool | None = MatresMode.KEEP,
) -> NormalizedText:
    """Normalize Hebrew while retaining a map back to original string offsets.

    By default niqqud and whitespace disappear. ``spaces=True`` preserves word
    boundaries as one ASCII space per whitespace run. ``matres='internal'``
    removes א/ה/ו/י only when internal to a whitespace-delimited token;
    ``matres='all'`` removes them everywhere.
    """
    keep_marks = get_niqqud() if niqqud is None else bool(niqqud)
    mode = MatresMode.coerce(matres)
    internal = _internal_mater_offsets(text) if mode is MatresMode.INTERNAL else set()
    out: list[str] = []
    index: list[int] = []
    in_space = False
    for char, original_offset in _decomposed(text):
        if char.isspace():
            if spaces and not in_space and out:
                out.append(" ")
                index.append(original_offset)
            in_space = True
            continue
        in_space = False
        if not keep_marks and is_hebrew_mark(char):
            continue
        if mode is MatresMode.ALL and char in MATRES:
            continue
        if mode is MatresMode.INTERNAL and original_offset in internal and char in MATRES:
            continue
        out.append(char)
        index.append(original_offset)
    if spaces and out and out[-1] == " ":
        out.pop()
        index.pop()
    normalized = unicodedata.normalize("NFC", "".join(out))
    # NFC could theoretically alter length. Hebrew bases + marks generally retain
    # one base plus combining marks; reconstruct safely if it does change.
    if len(normalized) != len(index):
        normalized = "".join(out)
    return NormalizedText(normalized, tuple(index), text)


def normalize_hebrew(
    text: str,
    *,
    niqqud: bool | None = None,
    spaces: bool = False,
    matres: MatresMode | str | bool | None = MatresMode.KEEP,
) -> str:
    return normalize_hebrew_with_map(
        text, niqqud=niqqud, spaces=spaces, matres=matres
    ).text


def normalize_english_with_map(
    text: str,
    *,
    case_sensitive: bool = False,
    collapse_spaces: bool = True,
) -> NormalizedText:
    out: list[str] = []
    index: list[int] = []
    in_space = False
    for original_offset, char in enumerate(unicodedata.normalize("NFC", text)):
        if char.isspace() and collapse_spaces:
            if not in_space and out:
                out.append(" ")
                index.append(original_offset)
            in_space = True
            continue
        in_space = False
        rendered = char if case_sensitive else char.casefold()
        for piece in rendered:
            out.append(piece)
            index.append(original_offset)
    if collapse_spaces and out and out[-1] == " ":
        out.pop()
        index.pop()
    return NormalizedText("".join(out), tuple(index), text)


def normalize_english(
    text: str, *, case_sensitive: bool = False, collapse_spaces: bool = True
) -> str:
    return normalize_english_with_map(
        text, case_sensitive=case_sensitive, collapse_spaces=collapse_spaces
    ).text


def whitespace_tokens(text: str) -> Iterator[tuple[str, int, int]]:
    """Yield tokens whose *only* boundary is Unicode whitespace."""
    for match in TOKEN_RE.finditer(text):
        yield match.group(0), match.start(), match.end()


def _literal_pattern(query: str, *, whole_word: bool) -> Pattern[str]:
    escaped = re.escape(query)
    if whole_word:
        escaped = rf"(?<!\S){escaped}(?!\S)"
    return re.compile(escaped)


def find_english(
    text: str,
    query: str | Pattern[str],
    *,
    regex: bool = False,
    case_sensitive: bool = False,
    whole_word: bool | str = "auto",
) -> list[TextMatch]:
    normalized = normalize_english_with_map(text, case_sensitive=case_sensitive)
    is_regex = regex or hasattr(query, "finditer")
    if is_regex:
        if hasattr(query, "finditer"):
            pattern = query  # type: ignore[assignment]
        else:
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(str(query), flags)
    else:
        q = normalize_english(str(query), case_sensitive=case_sensitive)
        use_word = (" " not in q) if whole_word == "auto" else bool(whole_word)
        pattern = _literal_pattern(q, whole_word=use_word)
    result: list[TextMatch] = []
    for match in pattern.finditer(normalized.text):
        start, end = normalized.original_span(match.start(), match.end())
        result.append(
            TextMatch(
                start,
                end,
                match.start(),
                match.end(),
                text[start:end],
                normalized.text[match.start() : match.end()],
                tuple(match.groups()),
            )
        )
    return result


def find_hebrew(
    text: str,
    query: str | Pattern[str],
    *,
    regex: bool = False,
    niqqud: bool | None = None,
    spaces: bool = False,
    matres: MatresMode | str | bool | None = MatresMode.KEEP,
) -> list[TextMatch]:
    normalized = normalize_hebrew_with_map(text, niqqud=niqqud, spaces=spaces, matres=matres)
    is_regex = regex or hasattr(query, "finditer")
    if is_regex:
        # Regexes operate on the normalized stream. A compiled regex is used
        # literally; a string regex has ordinary Hebrew marks/spaces normalized.
        if hasattr(query, "finditer"):
            pattern = query  # type: ignore[assignment]
        else:
            q = normalize_hebrew(str(query), niqqud=niqqud, spaces=spaces, matres=matres)
            pattern = re.compile(q)
    else:
        q = normalize_hebrew(str(query), niqqud=niqqud, spaces=spaces, matres=matres)
        pattern = re.compile(re.escape(q))
    result: list[TextMatch] = []
    for match in pattern.finditer(normalized.text):
        start, end = normalized.original_span(match.start(), match.end())
        result.append(
            TextMatch(
                start,
                end,
                match.start(),
                match.end(),
                text[start:end],
                normalized.text[match.start() : match.end()],
                tuple(match.groups()),
            )
        )
    return result
