from __future__ import annotations

import re
from dataclasses import dataclass

from .canon import ORDER_BOOKS, chapter_verses


@dataclass(frozen=True)
class BookRef:
    book: str

    def __str__(self) -> str:
        return self.book


@dataclass(frozen=True)
class ChapterRef:
    book: str
    chapter: int

    def __str__(self) -> str:
        return f"{self.book} {self.chapter}"


@dataclass(frozen=True)
class VerseRef:
    book: str
    chapter: int
    verse: int

    def __str__(self) -> str:
        return f"{self.book} {self.chapter}:{self.verse}"


ALIASES = {
    "gen": "Genesis",
    "ge": "Genesis",
    "exo": "Exodus",
    "ex": "Exodus",
    "lev": "Leviticus",
    "num": "Numbers",
    "deut": "Deuteronomy",
    "deu": "Deuteronomy",
    "josh": "Joshua",
    "judg": "Judges",
    "1sam": "1 Samuel",
    "isam": "1 Samuel",
    "1sa": "1 Samuel",
    "2sam": "2 Samuel",
    "iisam": "2 Samuel",
    "2sa": "2 Samuel",
    "1kgs": "1 Kings",
    "1ki": "1 Kings",
    "1kings": "1 Kings",
    "2kgs": "2 Kings",
    "2ki": "2 Kings",
    "2kings": "2 Kings",
    "1chr": "1 Chronicles",
    "1chron": "1 Chronicles",
    "2chr": "2 Chronicles",
    "2chron": "2 Chronicles",
    "ps": "Psalms",
    "psa": "Psalms",
    "prov": "Proverbs",
    "eccl": "Ecclesiastes",
    "qoh": "Ecclesiastes",
    "song": "Song of Songs",
    "songs": "Song of Songs",
    "sos": "Song of Songs",
    "isa": "Isaiah",
    "jer": "Jeremiah",
    "lam": "Lamentations",
    "ezek": "Ezekiel",
    "dan": "Daniel",
    "obad": "Obadiah",
    "mic": "Micah",
    "nah": "Nahum",
    "hab": "Habakkuk",
    "zeph": "Zephaniah",
    "hag": "Haggai",
    "zech": "Zechariah",
    "mal": "Malachi",
}

ROMAN_PREFIXES = {
    "i": "1",
    "ii": "2",
    "iii": "3",
}


def norm(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"^(i|ii|iii)\b", lambda m: ROMAN_PREFIXES[m.group(1)], text)
    return re.sub(r"[^a-z0-9]+", "", text)


def resolve_book(text: str, *, order: str = "all") -> str:
    key = norm(text)
    books = ORDER_BOOKS[order]

    if key in ALIASES:
        book = ALIASES[key]
        if book in books:
            return book

    exact = [book for book in books if norm(book) == key]
    if exact:
        return exact[0]

    matches = [book for book in books if norm(book).startswith(key)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise ValueError(f"Ambiguous book prefix {text!r}: {', '.join(matches)}")

    raise ValueError(f"Unknown book in order {order!r}: {text!r}")


def parse_ref(parts: str | list[str] | tuple[str, ...], *, order: str = "all") -> BookRef | ChapterRef | VerseRef:
    if isinstance(parts, str):
        text = parts
    else:
        text = " ".join(parts)
    text = text.strip()
    if not text:
        raise ValueError("Bible reference is required.")

    verse_match = re.match(r"^(?P<book>.+?)\s+(?P<chapter>[0-9]+):(?P<verse>[0-9]+)$", text)
    if verse_match:
        book = resolve_book(verse_match.group("book"), order=order)
        return _validated_verse(book, int(verse_match.group("chapter")), int(verse_match.group("verse")))

    chapter_match = re.match(r"^(?P<book>.+?)\s+(?P<chapter>[0-9]+)$", text)
    if chapter_match:
        book = resolve_book(chapter_match.group("book"), order=order)
        return _validated_chapter(book, int(chapter_match.group("chapter")))

    return BookRef(resolve_book(text, order=order))


def _validated_chapter(book: str, chapter: int) -> ChapterRef:
    counts = chapter_verses()
    if book not in counts:
        raise NotImplementedError(
            f"TODO: provide chapter and verse counts for {book}."
        )
    if not 1 <= chapter <= len(counts[book]):
        raise ValueError(f"{book} has no chapter {chapter}.")
    return ChapterRef(book, chapter)


def _validated_verse(book: str, chapter: int, verse: int) -> VerseRef:
    chapter_ref = _validated_chapter(book, chapter)
    verse_count = chapter_verses()[book][chapter - 1]
    if not 1 <= verse <= verse_count:
        raise ValueError(f"{book} {chapter} has no verse {verse}.")
    return VerseRef(chapter_ref.book, chapter_ref.chapter, verse)
