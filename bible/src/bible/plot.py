from __future__ import annotations

from pathlib import Path

from .canon import chapter_verses, order_books
from .refs import ChapterRef, parse_ref


def books(*, order: str = "all", show: bool = True):
    import matplotlib.pyplot as plt

    counts = chapter_verses()
    books = order_books(order)

    values = [len(counts[name]) for name in books]

    fig, ax = plt.subplots(figsize=(max(8, len(books) * 0.42), 5))
    ax.bar(books, values)
    ax.set_ylabel("Chapters")
    ax.set_title("Chapters by book")
    ax.tick_params(axis="x", labelrotation=90)
    fig.tight_layout()

    if show:
        plt.show()
    return fig, ax


def chapters(book: str, *, order: str = "all", show: bool = True):
    import matplotlib.pyplot as plt

    counts = chapter_verses()
    books = order_books(order)
    start = parse_ref(book, order=order)
    if not hasattr(start, "book"):
        raise ValueError("chapters plot expects a book reference.")
    if start.book not in books:
        raise ValueError(f"{start.book} is not available in order {order!r}.")

    selected = books[books.index(start.book):]
    values = [len(counts[name]) for name in selected]

    fig, ax = plt.subplots(figsize=(max(8, len(selected) * 0.32), 5))
    ax.bar(selected, values)
    ax.set_ylabel("Chapters")
    ax.set_title(f"Chapters by book from {start.book}")
    ax.tick_params(axis="x", labelrotation=90)
    fig.tight_layout()

    if show:
        plt.show()
    return fig, ax


def verses(ref: str, *, order: str = "all", show: bool = True):
    import matplotlib.pyplot as plt

    parsed = parse_ref(ref, order=order)
    if not isinstance(parsed, ChapterRef):
        raise ValueError("verses plot expects a book-chapter reference.")

    verse_count = chapter_verses()[parsed.book][parsed.chapter - 1]
    verse_numbers = list(range(1, verse_count + 1))

    fig, ax = plt.subplots(figsize=(max(8, verse_count * 0.18), 4))
    ax.bar(verse_numbers, [1] * verse_count)
    ax.set_xlabel("Verse")
    ax.set_yticks([])
    ax.set_title(f"{parsed.book} {parsed.chapter}: {verse_count} verses")
    fig.tight_layout()

    if show:
        plt.show()
    return fig, ax


def save(fig, output: str | Path) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    return path
