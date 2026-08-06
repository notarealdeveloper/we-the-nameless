from __future__ import annotations

import ast
from functools import cache
from pathlib import Path


CHRISTIAN_OLD_TESTAMENT = (
    "Genesis",
    "Exodus",
    "Leviticus",
    "Numbers",
    "Deuteronomy",
    "Joshua",
    "Judges",
    "Ruth",
    "1 Samuel",
    "2 Samuel",
    "1 Kings",
    "2 Kings",
    "1 Chronicles",
    "2 Chronicles",
    "Ezra",
    "Nehemiah",
    "Esther",
    "Job",
    "Psalms",
    "Proverbs",
    "Ecclesiastes",
    "Song of Solomon",
    "Isaiah",
    "Jeremiah",
    "Lamentations",
    "Ezekiel",
    "Daniel",
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

NEW_TESTAMENT = (
    "Matthew",
    "Mark",
    "Luke",
    "John",
    "Acts",
    "Romans",
    "1 Corinthians",
    "2 Corinthians",
    "Galatians",
    "Ephesians",
    "Philippians",
    "Colossians",
    "1 Thessalonians",
    "2 Thessalonians",
    "1 Timothy",
    "2 Timothy",
    "Titus",
    "Philemon",
    "Hebrews",
    "James",
    "1 Peter",
    "2 Peter",
    "1 John",
    "2 John",
    "3 John",
    "Jude",
    "Revelation",
)

JEWISH_ORDER = (
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
    "Song of Solomon",
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

TORAH = CHRISTIAN_OLD_TESTAMENT[:5]
DEUTERONOMISTIC_HISTORY = CHRISTIAN_OLD_TESTAMENT[4:12]
PRIMARY_HISTORY = CHRISTIAN_OLD_TESTAMENT[:12]
PROPHETS = (
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
KETUVIM = JEWISH_ORDER[26:]
GOSPELS = NEW_TESTAMENT[:4]
PAULINE_EPISTLES = (
    "Romans",
    "1 Corinthians",
    "2 Corinthians",
    "Galatians",
    "Ephesians",
    "Philippians",
    "Colossians",
    "1 Thessalonians",
    "2 Thessalonians",
    "1 Timothy",
    "2 Timothy",
    "Titus",
    "Philemon",
)

APOCRYPHA_AND_PSEUDEPIGRAPHA = (
    "Tobit",
    "Judith",
    "Greek Esther",
    "Wisdom of Solomon",
    "Sirach",
    "Baruch",
    "Letter of Jeremiah",
    "Prayer of Azariah",
    "Susanna",
    "Bel and the Dragon",
    "1 Maccabees",
    "2 Maccabees",
    "1 Esdras",
    "2 Esdras",
    "Prayer of Manasseh",
    "Psalm 151",
    "3 Maccabees",
    "4 Maccabees",
    "1 Enoch",
    "Jubilees",
    "Testaments of the Twelve Patriarchs",
)

ORDER_BOOKS = {
    "old": CHRISTIAN_OLD_TESTAMENT,
    "new": NEW_TESTAMENT,
    "chr": CHRISTIAN_OLD_TESTAMENT + NEW_TESTAMENT,
    "jew": JEWISH_ORDER,
    "tor": TORAH,
    "deu": DEUTERONOMISTIC_HISTORY,
    "pri": PRIMARY_HISTORY,
    "pro": PROPHETS,
    "ktv": KETUVIM,
    "gos": GOSPELS,
    "epi": PAULINE_EPISTLES,
    "apo": APOCRYPHA_AND_PSEUDEPIGRAPHA,
    "all": CHRISTIAN_OLD_TESTAMENT + APOCRYPHA_AND_PSEUDEPIGRAPHA + NEW_TESTAMENT,
}

ORDER_KEYS = tuple(ORDER_BOOKS)


def _repo_root() -> Path:
    for path in Path(__file__).resolve().parents:
        candidate = path / "we-progress"
        if candidate.exists():
            return path
    raise FileNotFoundError(
        "TODO: provide a packaged Bible chapter/verse data file or keep "
        "./we-progress at the repository root."
    )


@cache
def chapter_verses() -> dict[str, tuple[int, ...]]:
    path = _repo_root() / "we-progress"
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    for node in module.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == "CHAPTER_VERSES":
                value = ast.literal_eval(node.value)
                return {book: tuple(chapters) for book, chapters in value.items()}
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "CHAPTER_VERSES":
                    value = ast.literal_eval(node.value)
                    return {book: tuple(chapters) for book, chapters in value.items()}

    raise ValueError(f"TODO: provide CHAPTER_VERSES data in {path}.")


def order_books(order: str = "chr", *, require_counts: bool = True) -> tuple[str, ...]:
    try:
        books = ORDER_BOOKS[order]
    except KeyError as e:
        raise ValueError(
            f"Unknown order {order!r}. Expected one of: {', '.join(ORDER_KEYS)}"
        ) from e

    if require_counts:
        counts = chapter_verses()
        missing = [book for book in books if book not in counts]
        if missing:
            raise NotImplementedError(
                "TODO: provide chapter and verse counts for these books before "
                f"using order {order!r}: {', '.join(missing)}."
            )

    return books
