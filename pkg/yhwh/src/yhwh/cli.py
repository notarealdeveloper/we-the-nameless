"""Argparse command-line interface for parsing, search, statistics, and models."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Iterable

from ._version import __version__
from .attribution import SourceAttributor
from .config import cache_dir, clean_cache
from .corpus import Corpus, PRIMARY_HISTORY, TORAH
from .dataset import build_dataset
from .frequency import frequencies_by_source, frequency
from .statistics import characteristic_words, source_profile


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="yhwh",
        description="Source-aware Biblical Hebrew and English corpus analysis",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--corpus", help="TeX corpus root or built JSONL/SQLite dataset")
    parser.add_argument("--no-cache", action="store_true", help="Do not use the parsed-corpus cache")
    sub = parser.add_subparsers(dest="command", required=True)

    info = sub.add_parser("info", help="Show corpus and source-label summary")
    info.add_argument("--json", action="store_true")

    build = sub.add_parser("build", help="Build JSONL, SQLite, frequencies, and Torah models")
    build.add_argument("output", nargs="?", default="dataset")
    build.add_argument("--name", default="primary-history")
    build.add_argument("--no-raw", action="store_true", help="Omit raw TeX from exported records")
    build.add_argument("--no-sqlite", action="store_true")
    build.add_argument("--no-frequencies", action="store_true")
    build.add_argument("--no-models", action="store_true")

    search = sub.add_parser("search", aliases=["grep"], help="Search words, phrases, or regexes")
    search.add_argument("query")
    _language(search)
    search.add_argument("--regex", action="store_true")
    search.add_argument("--case-sensitive", action="store_true")
    search.add_argument("--substring", action="store_true", help="English: do not require token boundaries")
    search.add_argument("--spaces", action="store_true", help="Hebrew: distinguish spaces")
    search.add_argument("--niqqud", action="store_true", help="Hebrew: distinguish niqqud")
    search.add_argument("--matres", choices=["keep", "internal", "all"], default="keep")
    search.add_argument("--source", action="append")
    search.add_argument("--book", action="append")
    search.add_argument("--limit", type=int)
    search.add_argument("--json", action="store_true")
    search.add_argument("--segments", action="store_true", help="Print matched source segments")

    freq = sub.add_parser("freq", aliases=["frequency"], help="Whitespace-token frequency analysis")
    _language(freq)
    freq.add_argument("--book", action="append")
    freq.add_argument("--scope", choices=["all", "torah", "primary-history"], default="primary-history")
    freq.add_argument("--source", action="append")
    freq.add_argument("--by-source", action="store_true")
    freq.add_argument("--literal-sources", action="store_true")
    freq.add_argument("--attribution", choices=["majority", "fractional", "all", "composite"], default="fractional")
    freq.add_argument("--case-sensitive", action="store_true")
    freq.add_argument("--niqqud", action="store_true")
    freq.add_argument("--matres", choices=["keep", "internal", "all"], default="keep")
    freq.add_argument("--top", type=int, default=50)
    freq.add_argument("--json", nargs="?", const="-", metavar="PATH")
    freq.add_argument("--plot", metavar="PATH")

    profile = sub.add_parser("profile", help="Full per-source evidence for a word/phrase/regex")
    profile.add_argument("query")
    _language(profile)
    profile.add_argument("--book", action="append")
    profile.add_argument("--scope", choices=["all", "torah", "primary-history"], default="torah")
    profile.add_argument("--regex", action="store_true")
    profile.add_argument("--case-sensitive", action="store_true")
    profile.add_argument("--spaces", action="store_true")
    profile.add_argument("--niqqud", action="store_true")
    profile.add_argument("--matres", choices=["keep", "internal", "all"], default="keep")
    profile.add_argument("--json", action="store_true")
    profile.add_argument("--plot", metavar="PATH")
    profile.add_argument(
        "--metric",
        choices=["count", "rate_per_million", "enrichment_log2", "log_odds_z", "pmi_bits"],
        default="rate_per_million",
    )

    chars = sub.add_parser("characteristic", help="Rank long-tail source-characteristic words")
    _language(chars)
    chars.add_argument("--source")
    chars.add_argument("--book", action="append")
    chars.add_argument("--scope", choices=["all", "torah", "primary-history"], default="torah")
    chars.add_argument("--min-count", type=float, default=2.0)
    chars.add_argument("--limit", type=int, default=100)
    chars.add_argument(
        "--rank-by",
        choices=["log_odds_z", "enrichment_log2", "information_bits", "count", "rate_per_million"],
        default="log_odds_z",
    )
    chars.add_argument("--json", action="store_true")
    chars.add_argument("--plot", metavar="PATH")

    attribute = sub.add_parser("attribute", help="Score novel text against Torah-trained sources")
    attribute.add_argument("text", nargs="?", help="Text to score; omit with --file or pipe stdin")
    attribute.add_argument("--file", type=Path)
    _language(attribute, default="hebrew")
    attribute.add_argument("--scope", default="torah", help="Training scope (default: trusted Torah)")
    attribute.add_argument("--source", action="append", dest="sources")
    attribute.add_argument("--model", type=Path, help="Load a previously serialized model")
    attribute.add_argument("--save-model", type=Path)
    attribute.add_argument("--niqqud", action="store_true")
    attribute.add_argument("--matres", choices=["keep", "internal", "all"], default="keep")
    attribute.add_argument("--top-tokens", type=int, default=12)
    attribute.add_argument("--json", action="store_true")
    attribute.add_argument("--plot", metavar="PATH")

    validate = sub.add_parser("validate", help="Check span integrity and missing text")
    validate.add_argument("--json", action="store_true")
    validate.add_argument("--fail-on-warning", action="store_true")

    cache = sub.add_parser("cache", help="Inspect or clean ~/.cache/yhwh")
    cache.add_argument("action", choices=["path", "clean"], nargs="?", default="path")
    return parser


def _language(parser: argparse.ArgumentParser, default: str = "english") -> None:
    parser.add_argument(
        "--language",
        "-l",
        choices=["english", "hebrew", "eng", "heb", "en", "he"],
        default=default,
    )


def _lang(value: str) -> str:
    return "hebrew" if value.lower().startswith("h") else "english"


def _load(path: str | None, *, use_cache: bool) -> Corpus:
    value = path or os.environ.get("YHWH_DATASET") or os.environ.get("YHWH_CORPUS")
    if value:
        target = Path(value).expanduser()
        if target.is_file() and (
            target.name.endswith(".jsonl.gz")
            or target.suffix in {".jsonl", ".sqlite", ".sqlite3", ".db"}
        ):
            return Corpus.from_dataset(target)
        if target.is_dir() and next(target.glob("*.jsonl.gz"), None) is not None and next(target.rglob("*.tex"), None) is None:
            return Corpus.from_dataset(target)
        return Corpus.from_tex(target, use_cache=use_cache)
    return Corpus.from_tex(use_cache=use_cache)


def _scope(corpus: Corpus, scope: str, books: list[str] | None = None) -> Any:
    if books:
        return corpus.select(books=books)
    if scope == "torah":
        return corpus.select(books=[book for book in TORAH if book in corpus.book_names])
    if scope == "primary-history":
        return corpus.select(books=[book for book in PRIMARY_HISTORY if book in corpus.book_names])
    return corpus.verses


def _print_json(value: Any, path: str | None = None) -> None:
    text = json.dumps(value, ensure_ascii=False, indent=2)
    if path and path != "-":
        Path(path).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


def _text(args: argparse.Namespace) -> str:
    if args.file:
        return args.file.read_text(encoding="utf-8")
    if args.text is not None:
        return args.text
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("attribute requires TEXT, --file, or stdin")


def main(argv: Iterable[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command == "cache":
        print(clean_cache() if args.action == "clean" else cache_dir())
        return 0

    corpus = _load(args.corpus, use_cache=not args.no_cache)
    if args.command == "info":
        summary = corpus.summary()
        if args.json:
            _print_json(summary)
        else:
            print(corpus)
            for key, value in summary.items():
                print(f"{key}: {value}")
        return 0

    if args.command == "build":
        generated = build_dataset(
            corpus,
            args.output,
            name=args.name,
            include_raw=not args.no_raw,
            with_sqlite=not args.no_sqlite,
            with_frequencies=not args.no_frequencies,
            with_models=not args.no_models,
        )
        for key, path in generated.items():
            print(f"{key}: {path}")
        return 0

    if args.command in {"search", "grep"}:
        language = _lang(args.language)
        verses = corpus.select(books=args.book) if args.book else corpus.verses
        common = {
            "regex": args.regex,
            "source": args.source,
        }
        if language == "hebrew":
            result = verses.hebrew(
                args.query,
                **common,
                spaces=args.spaces,
                niqqud=args.niqqud,
                matres=args.matres,
            )
        else:
            result = verses.english(
                args.query,
                **common,
                case_sensitive=args.case_sensitive,
                whole_word=False if args.substring else "auto",
            )
        selected = result if args.limit is None else result[: args.limit]
        if args.json:
            _print_json(
                [
                    {
                        **verse.to_dict(include_raw=False),
                        "matches": [match.to_dict() for match in result.match_info(verse)],
                    }
                    for verse in selected
                ]
            )
        else:
            for verse in selected:
                print(f"{verse.ref}\t{'+'.join(verse.sources(language, canonical=True))}")
                print(verse.text(language))
                if args.segments:
                    for match in result.match_info(verse):
                        print(f"  [{match.start}:{match.end}] {dict(match.sources)} {match.text!r}")
            print(f"{len(result)} matching verses", file=sys.stderr)
        return 0

    if args.command in {"freq", "frequency"}:
        language = _lang(args.language)
        verses = _scope(corpus, args.scope, args.book)
        if args.by_source:
            result = frequencies_by_source(
                verses,
                language=language,
                sources=args.source,
                canonical_sources=not args.literal_sources,
                case_sensitive=args.case_sensitive,
                niqqud=args.niqqud,
                matres=args.matres,
                attribution=args.attribution,
            )
            if args.json:
                _print_json(result.to_dict(), args.json)
            else:
                for source, counter in result.items():
                    print(f"\n## {source} ({counter.total_tokens:g} tokens)")
                    for word, count in counter.most_common(args.top):
                        print(f"{word}\t{count:g}\t{counter.rate(str(word)):.3f}/M")
            if args.plot:
                from .plotting import plot_frequency

                # One file per source avoids subplots and remains scriptable.
                base = Path(args.plot)
                for source, counter in result.items():
                    path = base.with_name(f"{base.stem}-{source}{base.suffix or '.png'}")
                    plot_frequency(counter, top=args.top, title=f"{source}: {language}", save=path)
        else:
            result = frequency(
                verses,
                language=language,
                source=args.source,
                case_sensitive=args.case_sensitive,
                niqqud=args.niqqud,
                matres=args.matres,
                attribution=args.attribution,
            )
            if args.json:
                _print_json(result.to_dict(), args.json)
            else:
                for word, count in result.most_common(args.top):
                    print(f"{word}\t{count:g}\t{result.rate(str(word)):.3f}/M")
            if args.plot:
                result.plot(top=args.top, save=args.plot)
        return 0

    if args.command == "profile":
        language = _lang(args.language)
        verses = _scope(corpus, args.scope, args.book)
        result = source_profile(
            verses,
            args.query,
            language=language,
            regex=args.regex,
            case_sensitive=args.case_sensitive,
            spaces=args.spaces,
            niqqud=args.niqqud,
            matres=args.matres,
        )
        if args.json:
            _print_json(result.to_dict())
        else:
            print(f"query: {result.query!r}; occurrences={result.total_occurrences:g}")
            print("source\tcount\trate/M\tlog2 enrich\tz\tPMI bits")
            for value in result.evidence:
                print(
                    f"{value.source}\t{value.count:g}\t{value.rate_per_million:.3f}\t"
                    f"{value.enrichment_log2:.3f}\t{value.log_odds_z:.3f}\t{value.pmi_bits:.3f}"
                )
        if args.plot:
            result.plot(metric=args.metric, save=args.plot)
        return 0

    if args.command == "characteristic":
        language = _lang(args.language)
        verses = _scope(corpus, args.scope, args.book)
        counters = frequencies_by_source(verses, language=language, attribution="fractional")
        values = characteristic_words(
            counters,
            source=args.source,
            min_count=args.min_count,
            limit=args.limit,
            rank_by=args.rank_by,
        )
        if args.json:
            _print_json([value.to_dict() for value in values])
        else:
            print("source\tword\tcount\trate/M\tz\tlog2 enrich\tinformation bits")
            for value in values:
                print(
                    f"{value.source}\t{value.word}\t{value.count:g}\t{value.rate_per_million:.3f}\t"
                    f"{value.log_odds_z:.3f}\t{value.enrichment_log2:.3f}\t{value.information_bits:.3f}"
                )
        if args.plot:
            from .plotting import plot_characteristic_words

            plot_characteristic_words(values, metric=args.rank_by, save=args.plot)
        return 0

    if args.command == "attribute":
        language = _lang(args.language)
        if args.model:
            model = SourceAttributor.load(args.model)
        else:
            model = SourceAttributor.train(
                corpus,
                scope=args.scope,
                language=language,
                sources=tuple(args.sources) if args.sources else ("J", "E", "P", "R", "D"),
                niqqud=args.niqqud,
                matres=args.matres,
            )
        if args.save_model:
            model.save(args.save_model)
        result = model.attribute(_text(args))
        if args.json:
            _print_json(result.to_dict())
        else:
            print(result)
            for source, probability in sorted(
                result.posterior.items(), key=lambda item: item[1], reverse=True
            ):
                print(
                    f"{source}: p={probability:.6f}; log evidence={result.log_evidence_bits[source]:.3f} bits; "
                    f"surprisal={result.posterior_surprisal_bits[source]:.3f} bits"
                )
            print(f"winner vs runner-up: {result.log2_bayes_factor:.3f} bits")
            print(f"known-token coverage: {result.known_tokens}/{result.total_tokens} ({result.coverage:.1%})")
            print("strongest token evidence:")
            for token in result.strongest_tokens(limit=args.top_tokens):
                contribution = token.contribution_vs_mean_bits[result.winner]
                print(f"  {token.original}\t{contribution:+.3f} bits\tknown={token.known}")
            print(result.caveat)
        if args.plot:
            result.plot(save=args.plot)
        return 0

    if args.command == "validate":
        issues = corpus.validate()
        if args.json:
            _print_json([issue.__dict__ for issue in issues])
        else:
            for issue in issues:
                print(f"{issue.level}\t{issue.code}\t{issue.verse_id or '-'}\t{issue.message}")
            print(f"{len(issues)} issues")
        bad = any(issue.level == "error" for issue in issues)
        warned = any(issue.level == "warning" for issue in issues)
        return int(bad or (args.fail_on_warning and warned))

    parser.error(f"Unhandled command {args.command}")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
