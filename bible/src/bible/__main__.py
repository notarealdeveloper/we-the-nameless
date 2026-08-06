from __future__ import annotations

import argparse
import os
import re
import sys

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

from . import plot
from .canon import ORDER_KEYS, chapter_verses
from .refs import BookRef, ChapterRef, VerseRef, parse_ref
from .text import LANGUAGES, require_verse_texts


TOP_LEVEL_COMMANDS = {"help", "list", "plot", "grep", "-h", "--help"}


def add_order(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-o",
        "--order",
        choices=ORDER_KEYS,
        default="all",
        help="Book order/subset to use.",
    )


def add_plot_measure(parser: argparse.ArgumentParser, *, default: str) -> None:
    measure = parser.add_mutually_exclusive_group()
    measure.add_argument(
        "--verses",
        action="store_const",
        const="verses",
        dest="measure",
        help="Measure verses. This is the default for book chapter plots.",
    )
    measure.add_argument(
        "--words",
        action="store_const",
        const="words",
        dest="measure",
        help="Measure words in the selected language text.",
    )
    measure.add_argument(
        "--chars",
        action="store_const",
        const="chars",
        dest="measure",
        help="Measure non-space characters in the selected language text.",
    )
    parser.set_defaults(measure=default)
    parser.add_argument(
        "--hebrew",
        action="store_const",
        const="heb",
        default="eng",
        dest="language",
        help="Use Hebrew verse text for --words or --chars; --chars strips niqqud.",
    )


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("bible")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("help", help="Show this help message.")

    list_parser = subparsers.add_parser("list", help="List chapter or verse structure.")
    add_order(list_parser)
    list_parser.add_argument(
        "-l",
        "--language",
        choices=LANGUAGES,
        default="eng",
        help="Verse text source to print for chapter or verse refs.",
    )
    list_parser.add_argument("ref", nargs="+", help="Book or book-chapter reference.")

    grep = subparsers.add_parser("grep", help="Search loaded verse text with a regex.")
    add_order(grep)
    grep.add_argument(
        "-l",
        "--language",
        choices=LANGUAGES,
        default="eng",
        help="Verse text source to search.",
    )
    grep.add_argument("regex")
    grep.add_argument("ref", nargs="+", help="Book, chapter, or verse scope.")

    plot_parser = subparsers.add_parser("plot", help="Run structure plots.")
    add_order(plot_parser)
    plot_parser.add_argument("--output", help="Write the plot to this path instead of showing it.")
    plot_subparsers = plot_parser.add_subparsers(dest="plot_command")

    books = plot_subparsers.add_parser("books", help="Plot chapter counts for loaded books.")
    add_order(books)
    books.add_argument("--output", help="Write the plot to this path instead of showing it.")

    chapters = plot_subparsers.add_parser(
        "chapters",
        help="Plot one book with one bar per chapter.",
        description=(
            "Plot chapter 1, chapter 2, etc. for a single book. By default each "
            "bar is the number of verses in that chapter. With --words or "
            "--chars, each bar is the total words or non-space characters in "
            "that chapter's verse text."
        ),
    )
    add_order(chapters)
    add_plot_measure(chapters, default="verses")
    chapters.add_argument("book", nargs="+", help="Book reference, such as exodus or 1 sam.")
    chapters.add_argument("--output", help="Write the plot to this path instead of showing it.")

    chapter = plot_subparsers.add_parser(
        "chapter",
        help="Plot one chapter with one bar per verse.",
        description=(
            "Plot verse 1, verse 2, etc. for a single chapter. By default each "
            "bar is the word count of the verse's English text. Use --chars "
            "for character counts or --hebrew to measure Hebrew text."
        ),
    )
    add_order(chapter)
    add_plot_measure(chapter, default="words")
    chapter.add_argument("ref", nargs="+", help="Book-chapter reference, such as 'exodus 20'.")
    chapter.add_argument("--output", help="Write the plot to this path instead of showing it.")

    verses = plot_subparsers.add_parser("verses", help="Plot verse positions in a chapter.")
    add_order(verses)
    verses.add_argument("ref", nargs="+", help="Book-chapter reference.")
    verses.add_argument("--output", help="Write the plot to this path instead of showing it.")

    return parser


def run_list(args: argparse.Namespace) -> None:
    ref = parse_ref(args.ref, order=args.order)
    counts = chapter_verses()

    if isinstance(ref, BookRef):
        if ref.book not in counts:
            raise NotImplementedError(
                f"TODO: provide chapter and verse counts for {ref.book}."
            )
        print(len(counts[ref.book]))
    elif isinstance(ref, ChapterRef):
        for verse_ref, text in require_verse_texts(ref, language=args.language):
            print(_format_verse_line(verse_ref, text))
    elif isinstance(ref, VerseRef):
        for verse_ref, text in require_verse_texts(ref, language=args.language):
            print(_format_verse_line(verse_ref, text))
    else:
        print(ref)


def run_grep(args: argparse.Namespace) -> None:
    regex = re.compile(args.regex)
    ref = parse_ref(args.ref, order=args.order)
    for verse_ref, text in require_verse_texts(ref, language=args.language):
        if regex.search(text):
            print(_format_verse_line(verse_ref, text))


def _format_verse_line(verse_ref: VerseRef, text: str) -> str:
    return f"{verse_ref}: {' '.join(text.split())}"


def run_plot(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.output:
        import matplotlib

        matplotlib.use("Agg", force=True)

    if args.plot_command in (None, "books"):
        fig, _ax = plot.books(order=args.order, show=not args.output)
    elif args.plot_command == "chapters":
        fig, _ax = plot.chapters(
            " ".join(args.book),
            order=args.order,
            measure=args.measure,
            language=args.language,
            show=not args.output,
        )
    elif args.plot_command == "chapter":
        fig, _ax = plot.chapter(
            " ".join(args.ref),
            order=args.order,
            measure=args.measure,
            language=args.language,
            show=not args.output,
        )
    elif args.plot_command == "verses":
        fig, _ax = plot.verses(" ".join(args.ref), order=args.order, show=not args.output)
    else:
        parser.error(f"Unknown plot command: {args.plot_command}")

    if args.output:
        print(plot.save(fig, args.output))


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = make_parser()

    if argv and argv[0] not in TOP_LEVEL_COMMANDS:
        parser.print_help(sys.stderr)
        return 2

    args = parser.parse_args(argv)

    try:
        if args.command in (None, "help"):
            parser.print_help()
        elif args.command == "list":
            run_list(args)
        elif args.command == "grep":
            run_grep(args)
        elif args.command == "plot":
            run_plot(args, parser)
    except re.error as e:
        parser.error(f"Invalid regular expression: {e}")
    except (ValueError, NotImplementedError) as e:
        parser.error(str(e))
    except Exception as e:
        parser.error(f"{type(e).__name__}: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
