from __future__ import annotations

import re
from functools import cache
from pathlib import Path


TANAKH_ORDER = (
    "Genesis",
    "Exodus",
    "Leviticus",
    "Numbers",
    "Deuteronomy",
    "Joshua",
    "Judges",
    "1 Samuel",
    "2 Samuel",
    "1 Kings",
    "2 Kings",
    "Isaiah",
    "Jeremiah",
    "Ezekiel",
    "Hosea",
    "Joel",
    "Amos",
    "Obadiah",
    "Jonah",
    "Micah",
    "Nahum",
    "Habakkuk",
    "Zephaniah",
    "Haggai",
    "Zechariah",
    "Malachi",
    "Psalms",
    "Proverbs",
    "Job",
    "Song of Songs",
    "Ruth",
    "Lamentations",
    "Ecclesiastes",
    "Esther",
    "Daniel",
    "Ezra",
    "Nehemiah",
    "1 Chronicles",
    "2 Chronicles",
)

TORAH = TANAKH_ORDER[:5]
DEUTERONOMISTIC_HISTORY = (
    "Deuteronomy",
    "Joshua",
    "Judges",
    "1 Samuel",
    "2 Samuel",
    "1 Kings",
    "2 Kings",
)
PRIMARY_HISTORY = TORAH + DEUTERONOMISTIC_HISTORY[1:]
PROPHETS = (
    "Joshua",
    "Judges",
    "1 Samuel",
    "2 Samuel",
    "1 Kings",
    "2 Kings",
    "Isaiah",
    "Jeremiah",
    "Ezekiel",
    "Hosea",
    "Joel",
    "Amos",
    "Obadiah",
    "Jonah",
    "Micah",
    "Nahum",
    "Habakkuk",
    "Zephaniah",
    "Haggai",
    "Zechariah",
    "Malachi",
)
KETUVIM = TANAKH_ORDER[26:]

ORDER_BOOKS = {
    "all": TANAKH_ORDER,
    "jew": TANAKH_ORDER,
    "tor": TORAH,
    "deu": DEUTERONOMISTIC_HISTORY,
    "pri": PRIMARY_HISTORY,
    "pro": PROPHETS,
    "ktv": KETUVIM,
}

ORDER_KEYS = tuple(ORDER_BOOKS)

BOOK_DIRECTORIES = {
    "01-genesis": ("Genesis",),
    "02-exodus": ("Exodus",),
    "03-leviticus": ("Leviticus",),
    "04-numbers": ("Numbers",),
    "05-deuteronomy": ("Deuteronomy",),
    "06-joshua": ("Joshua",),
    "07-judges": ("Judges",),
    "08-samuel": ("1 Samuel", "2 Samuel"),
    "09-kings": ("1 Kings", "2 Kings"),
    "10-ezra": ("Ezra",),
    "11-nehemiah": ("Nehemiah",),
    "12-esther": ("Esther",),
}

VERSE_REF_RE = re.compile(
    r"^(?:##\s*)?(?P<book>(?:[1-3]|I{1,3})?\s*[A-Za-z][A-Za-z ]*?)\s+"
    r"(?P<chapter>[0-9]+):(?P<verse>[0-9]+)(?:\s|$)"
)
ROMAN_BOOK_PREFIXES = {
    "I ": "1 ",
    "II ": "2 ",
    "III ": "3 ",
}


def _repo_root() -> Path:
    for path in Path(__file__).resolve().parents:
        if (path / "eng").is_dir() or (path / "heb").is_dir():
            return path
    raise NotImplementedError(
        "TODO: provide an eng/ or heb/ data directory next to the bible package "
        "checkout, or package a chapter/verse data file."
    )


@cache
def chapter_verses() -> dict[str, tuple[int, ...]]:
    counts: dict[str, dict[int, int]] = {}

    for path in _data_files():
        for book, chapter, verse in verse_refs_in_file(path):
            book_counts = counts.setdefault(book, {})
            book_counts[chapter] = max(verse, book_counts.get(chapter, 0))

    if not counts:
        raise NotImplementedError(
            "TODO: provide parseable verse data in eng/ or heb/ before querying "
            "chapter and verse counts."
        )

    return {
        book: tuple(chapters[number] for number in range(1, max(chapters) + 1))
        for book, chapters in counts.items()
        if _has_contiguous_chapters(book, chapters)
    }


def available_books() -> tuple[str, ...]:
    counts = chapter_verses()
    return tuple(book for book in ORDER_BOOKS["all"] if book in counts)


def missing_books(order: str = "all") -> tuple[str, ...]:
    counts = chapter_verses()
    return tuple(
        book for book in order_books(order, require_counts=False) if book not in counts
    )


def verse_refs_in_file(path: Path) -> tuple[tuple[str, int, int], ...]:
    refs: list[tuple[str, int, int]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = VERSE_REF_RE.match(line.strip())
        if not match:
            continue
        book = canonical_book(match.group("book"))
        if book is None:
            continue
        refs.append((book, int(match.group("chapter")), int(match.group("verse"))))
    return tuple(refs)


def canonical_book(text: str) -> str | None:
    text = " ".join(text.split())
    for roman, arabic in ROMAN_BOOK_PREFIXES.items():
        if text.startswith(roman):
            text = arabic + text.removeprefix(roman)
            break
    for books in ORDER_BOOKS.values():
        for book in books:
            if book.casefold() == text.casefold():
                return book
    return None


def _data_files() -> tuple[Path, ...]:
    root = _repo_root()
    files: list[Path] = []
    for dirname in BOOK_DIRECTORIES:
        for base in (root / "eng" / dirname, root / "heb" / dirname):
            if base.is_dir():
                files.extend(sorted(base.glob("*.md")))
                files.extend(sorted(base.glob("*.tex")))
    return tuple(files)


def _has_contiguous_chapters(book: str, chapters: dict[int, int]) -> bool:
    missing = [
        number for number in range(1, max(chapters) + 1) if number not in chapters
    ]
    if missing:
        raise NotImplementedError(
            "TODO: provide chapter data for missing chapters in "
            f"{book}: {', '.join(str(number) for number in missing)}."
        )
    return True


def order_books(order: str = "all", *, require_counts: bool = True) -> tuple[str, ...]:
    try:
        books = ORDER_BOOKS[order]
    except KeyError as e:
        raise ValueError(
            f"Unknown order {order!r}. Expected one of: {', '.join(ORDER_KEYS)}"
        ) from e

    if require_counts:
        counts = chapter_verses()
        books = tuple(book for book in books if book in counts)
        if not books:
            raise NotImplementedError(
                "TODO: provide chapter and verse counts from eng/ or heb/ for "
                f"at least one book in order {order!r}."
            )

    return books
