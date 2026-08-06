from __future__ import annotations

from collections.abc import Iterable
from functools import cache
import re

from .canon import VERSE_REF_RE, canonical_book, _repo_root, chapter_verses
from .refs import BookRef, ChapterRef, VerseRef

LANGUAGES = ("eng", "heb", "both")
SUPERSCRIPT_VERSE_RE = re.compile(r"^[\u00b9\u00b2\u00b3\u2070-\u2079]+\s*")
SEPARATOR_RE = re.compile(r"^-{3,}\s*$")


def available_languages() -> tuple[str, ...]:
    root = _repo_root()
    return tuple(language for language in ("eng", "heb") if (root / language).is_dir())


def verse_texts(
    ref: BookRef | ChapterRef | VerseRef,
    *,
    language: str = "eng",
) -> Iterable[tuple[VerseRef, str]] | object:
    if language not in LANGUAGES:
        raise ValueError(
            f"Unknown language {language!r}. Expected one of: {', '.join(LANGUAGES)}"
        )

    if language == "both":
        return _combined_texts(ref)

    texts = _text_store(language)
    selected = [
        (verse_ref, texts[verse_ref])
        for verse_ref in _refs_in_scope(ref)
        if verse_ref in texts
    ]
    if selected:
        return selected
    return NotImplemented


def require_verse_texts(
    ref: BookRef | ChapterRef | VerseRef,
    *,
    language: str = "eng",
) -> Iterable[tuple[VerseRef, str]]:
    texts = verse_texts(ref, language=language)
    if texts is NotImplemented:
        raise NotImplementedError(
            "TODO: provide verse text for "
            f"{ref} in {language!r}. The package can parse eng/ markdown and "
            "heb/ tab-separated verse files when those files exist."
        )
    return texts


def get_verse_text(
    ref: VerseRef,
    *,
    language: str = "eng",
) -> str:
    texts = dict(require_verse_texts(ref, language=language))
    try:
        return texts[ref]
    except KeyError as e:
        raise NotImplementedError(
            f"TODO: provide verse text for {ref} in {language!r}."
        ) from e


def _combined_texts(
    ref: BookRef | ChapterRef | VerseRef,
) -> tuple[tuple[VerseRef, str], ...]:
    eng = _text_store("eng")
    heb = _text_store("heb")
    selected: list[tuple[VerseRef, str]] = []
    for verse_ref in _refs_in_scope(ref):
        parts = []
        if verse_ref in eng:
            parts.append(f"eng: {eng[verse_ref]}")
        if verse_ref in heb:
            parts.append(f"heb: {heb[verse_ref]}")
        if parts:
            selected.append((verse_ref, " | ".join(parts)))
    return tuple(selected) if selected else NotImplemented


@cache
def _text_store(language: str) -> dict[VerseRef, str]:
    root = _repo_root() / language
    if not root.is_dir():
        return {}

    texts: dict[VerseRef, str] = {}
    for path in sorted(root.glob("*/*")):
        if path.suffix == ".md":
            texts.update(_parse_markdown_text(path, language=language))
        elif path.suffix == ".tex":
            texts.update(_parse_tabbed_text(path))
    return texts


def _parse_tabbed_text(path) -> dict[VerseRef, str]:
    texts: dict[VerseRef, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        label, sep, text = line.partition("\t")
        if not sep:
            continue
        match = VERSE_REF_RE.match(label.strip())
        if not match:
            continue
        book = canonical_book(match.group("book"))
        if book is None:
            continue
        texts[
            VerseRef(book, int(match.group("chapter")), int(match.group("verse")))
        ] = text.strip()
    return texts


def _parse_markdown_text(path, *, language: str) -> dict[VerseRef, str]:
    if language == "heb":
        return _parse_tabbed_text(path)

    texts: dict[VerseRef, str] = {}
    current: VerseRef | None = None
    body: list[str] = []
    body_started = False

    def finish() -> None:
        nonlocal current, body, body_started
        if current is not None:
            text = _clean_english_body(body)
            if text:
                texts[current] = text
        current = None
        body = []
        body_started = False

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        header = stripped.removeprefix("## ").strip()
        match = VERSE_REF_RE.match(header)
        book = canonical_book(match.group("book")) if match else None
        if match and book is not None:
            finish()
            current = VerseRef(
                book, int(match.group("chapter")), int(match.group("verse"))
            )
            continue

        if current is None:
            continue
        if SEPARATOR_RE.match(stripped):
            if body_started:
                finish()
            continue
        if not body_started and (not stripped or stripped == str(current.chapter)):
            continue

        body_started = True
        body.append(line)

    finish()
    return texts


def _clean_english_body(lines: list[str]) -> str:
    paragraphs: list[str] = []
    current: list[str] = []
    for line in lines:
        stripped = SUPERSCRIPT_VERSE_RE.sub("", line.strip())
        if not stripped:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        current.append(stripped)
    if current:
        paragraphs.append(" ".join(current))
    return "\n".join(paragraphs)


def _refs_in_scope(ref: BookRef | ChapterRef | VerseRef) -> tuple[VerseRef, ...]:
    if isinstance(ref, VerseRef):
        return (ref,)

    counts = chapter_verses()
    if ref.book not in counts:
        raise NotImplementedError(
            f"TODO: provide chapter and verse counts for {ref.book}."
        )

    if isinstance(ref, ChapterRef):
        return tuple(
            VerseRef(ref.book, ref.chapter, verse)
            for verse in range(1, counts[ref.book][ref.chapter - 1] + 1)
        )

    return tuple(
        VerseRef(ref.book, chapter, verse)
        for chapter, verse_count in enumerate(counts[ref.book], start=1)
        for verse in range(1, verse_count + 1)
    )
