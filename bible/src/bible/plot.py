from __future__ import annotations

from pathlib import Path
import re
import unicodedata

from .canon import chapter_verses, order_books
from .refs import BookRef, ChapterRef, parse_ref
from .text import require_verse_texts


def books(*, order: str = "all", show: bool = True):
    import matplotlib.pyplot as plt
    import seaborn as sns

    _set_theme(sns)

    counts = chapter_verses()
    books = order_books(order)

    values = [len(counts[name]) for name in books]

    fig, ax = plt.subplots(figsize=(max(8, len(books) * 0.42), 5))
    sns.barplot(x=books, y=values, ax=ax, color=_COLORS["blue"])
    ax.set_ylabel("Chapters")
    ax.set_title("Chapters by book")
    ax.tick_params(axis="x", labelrotation=90)
    fig.tight_layout()

    if show:
        plt.show()
    return fig, ax


def chapters(
    book: str,
    *,
    order: str = "all",
    measure: str = "verses",
    language: str = "eng",
    show: bool = True,
):
    import matplotlib.pyplot as plt
    import seaborn as sns

    _set_theme(sns)

    counts = chapter_verses()
    start = parse_ref(book, order=order)
    if not isinstance(start, BookRef):
        raise ValueError("chapters plot expects a book reference, not a chapter or verse.")
    if start.book not in counts:
        raise ValueError(f"{start.book} has no available chapter data.")

    chapter_numbers = list(range(1, len(counts[start.book]) + 1))
    values = [
        _chapter_measure(start.book, chapter, measure=measure, language=language)
        for chapter in chapter_numbers
    ]

    fig, ax = plt.subplots(figsize=(max(8, len(chapter_numbers) * 0.32), 5))
    sns.barplot(x=chapter_numbers, y=values, ax=ax, color=_color(measure, language))
    ax.set_xlabel("Chapter")
    ax.set_ylabel(_measure_label(measure, language, scope="chapter"))
    ax.set_title(f"{start.book}: {_measure_title(measure, language)} by chapter")
    fig.tight_layout()

    if show:
        plt.show()
    return fig, ax


def chapter(
    ref: str,
    *,
    order: str = "all",
    measure: str = "words",
    language: str = "eng",
    show: bool = True,
):
    import matplotlib.pyplot as plt
    import seaborn as sns

    _set_theme(sns)

    parsed = parse_ref(ref, order=order)
    if not isinstance(parsed, ChapterRef):
        raise ValueError("chapter plot expects a book-chapter reference.")

    rows = [
        (verse_ref.verse, _text_measure(text, measure=measure, language=language))
        for verse_ref, text in require_verse_texts(parsed, language=language)
    ]
    if not rows:
        raise ValueError(f"No {language} text is available for {parsed}.")

    verse_numbers = [verse for verse, _value in rows]
    values = [value for _verse, value in rows]

    fig, ax = plt.subplots(figsize=(max(8, len(rows) * 0.2), 4.5))
    sns.barplot(x=verse_numbers, y=values, ax=ax, color=_color(measure, language))
    ax.set_xlabel("Verse")
    ax.set_ylabel(_measure_label(measure, language, scope="verse"))
    ax.set_title(f"{parsed}: {_measure_title(measure, language)} by verse")
    fig.tight_layout()

    if show:
        plt.show()
    return fig, ax


def verses(ref: str, *, order: str = "all", show: bool = True):
    import matplotlib.pyplot as plt
    import seaborn as sns

    _set_theme(sns)

    parsed = parse_ref(ref, order=order)
    if not isinstance(parsed, ChapterRef):
        raise ValueError("verses plot expects a book-chapter reference.")

    verse_count = chapter_verses()[parsed.book][parsed.chapter - 1]
    verse_numbers = list(range(1, verse_count + 1))

    fig, ax = plt.subplots(figsize=(max(8, verse_count * 0.18), 4))
    sns.barplot(x=verse_numbers, y=[1] * verse_count, ax=ax, color=_COLORS["gold"])
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


_COLORS = {
    "blue": "#31566d",
    "gold": "#b8842f",
    "green": "#5b6f3a",
    "red": "#8a4b3f",
}
_WORD_RE = re.compile(r"[\w\u0590-\u05ff]+(?:[-\u2019'][\w\u0590-\u05ff]+)*")


def _set_theme(sns) -> None:
    sns.set_theme(
        context="notebook",
        style="whitegrid",
        palette=[_COLORS["blue"], _COLORS["gold"], _COLORS["green"], _COLORS["red"]],
        rc={
            "axes.facecolor": "#fbfaf5",
            "figure.facecolor": "#fbfaf5",
            "grid.color": "#d9d0bf",
            "axes.edgecolor": "#6f6758",
            "axes.labelcolor": "#2e2a24",
            "text.color": "#2e2a24",
        },
    )


def _chapter_measure(
    book: str,
    chapter_number: int,
    *,
    measure: str,
    language: str,
) -> int:
    if measure == "verses":
        return chapter_verses()[book][chapter_number - 1]

    ref = ChapterRef(book, chapter_number)
    return sum(
        _text_measure(text, measure=measure, language=language)
        for _verse_ref, text in require_verse_texts(ref, language=language)
    )


def _text_measure(text: str, *, measure: str, language: str) -> int:
    text = _clean_text_for_language(text, language=language)
    if measure == "words":
        return len(_WORD_RE.findall(text))
    if measure == "chars":
        return len(re.sub(r"\s+", "", text))
    if measure == "verses":
        return 1
    raise ValueError(f"Unknown plot measure {measure!r}.")


def _clean_text_for_language(text: str, *, language: str) -> str:
    if language == "heb":
        text = "".join(
            char for char in text if unicodedata.category(char) != "Mn"
        )
    return text


def _measure_label(measure: str, language: str, *, scope: str) -> str:
    if measure == "verses":
        return "Verses"
    language_name = "Hebrew" if language == "heb" else "English"
    unit = "Words" if measure == "words" else "Characters"
    if measure == "chars" and language == "heb":
        unit = "Characters, niqqud stripped"
    return f"{language_name} {unit} per {scope}"


def _measure_title(measure: str, language: str) -> str:
    if measure == "verses":
        return "Verses"
    language_name = "Hebrew" if language == "heb" else "English"
    if measure == "words":
        return f"{language_name} words"
    if language == "heb":
        return "Hebrew characters, niqqud stripped"
    return "English characters"


def _color(measure: str, language: str) -> str:
    if language == "heb":
        return _COLORS["green"]
    if measure == "chars":
        return _COLORS["red"]
    if measure == "words":
        return _COLORS["gold"]
    return _COLORS["blue"]
