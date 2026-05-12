from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .client import LANG_ALIASES, SefariaClient, SefariaError, normalize_lang
from .models import Version


def dump_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def print_text(result, *, as_json: bool) -> None:
    if as_json:
        dump_json(result.raw)
        return
    print(result.plain())


def print_versions(versions: list[Version]) -> None:
    if not versions:
        print("No versions found.")
        return
    for v in versions:
        bits = [v.language or "?", v.version_title or "Untitled"]
        if v.version_source:
            bits.append(v.version_source)
        print("\t".join(bits))


def cmd_langs(args: argparse.Namespace) -> None:
    langs = {alias: code for alias, code in sorted(LANG_ALIASES.items())}
    if args.json:
        dump_json(langs)
        return
    for alias, code in langs.items():
        print(f"{alias}\t{code}")


def cmd_hebrew(args: argparse.Namespace) -> None:
    client = SefariaClient(timeout=args.timeout)
    print_text(client.get_hebrew(args.ref, version_title=args.version_title), as_json=args.json)


def cmd_text(args: argparse.Namespace) -> None:
    client = SefariaClient(timeout=args.timeout)
    print_text(
        client.get_text(
            args.ref,
            lang=args.lang,
            version_title=args.version_title,
            version=args.version,
            fallback_on_default=not args.no_fallback,
        ),
        as_json=args.json,
    )


def cmd_versions(args: argparse.Namespace) -> None:
    client = SefariaClient(timeout=args.timeout)
    result = client.versions(args.index)
    if args.json:
        dump_json(result.raw)
        return
    versions = result.versions
    if args.lang:
        versions = result.for_lang(normalize_lang(args.lang))
    print_versions(versions)


def cmd_index(args: argparse.Namespace) -> None:
    client = SefariaClient(timeout=args.timeout)
    data = client.index(args.title)
    if args.json:
        dump_json(data)
        return
    print(data.get("title", args.title))
    he = data.get("heTitle")
    cats = data.get("categories")
    if he:
        print(f"Hebrew title: {he}")
    if cats:
        print("Categories: " + " / ".join(cats))
    if data.get("sectionNames"):
        print("Sections: " + " / ".join(data["sectionNames"]))


def cmd_toc(args: argparse.Namespace) -> None:
    client = SefariaClient(timeout=args.timeout)
    data = client.toc()
    if args.json:
        dump_json(data)
        return
    for item in data:
        title = item.get("category") or item.get("title") or "?"
        print(title)


def cmd_related(args: argparse.Namespace) -> None:
    client = SefariaClient(timeout=args.timeout)
    data = client.related(args.ref)
    if args.json:
        dump_json(data)
        return
    for key in ("links", "sheets", "topics", "media", "manuscripts"):
        value = data.get(key)
        if value:
            print(f"{key}: {len(value)}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sefaria")
    p.add_argument("--timeout", type=float, default=30.0)
    sub = p.add_subparsers(dest="cmd", required=True)

    he = sub.add_parser("hebrew", help="fetch original Hebrew for a ref")
    he.add_argument("ref", help="Sefaria ref, e.g. 'Genesis 1:1', 'Genesis 1', or Genesis")
    he.add_argument("--version-title")
    he.add_argument("--json", action="store_true")
    he.set_defaults(func=cmd_hebrew)

    text = sub.add_parser("text", help="fetch a ref in a language/version")
    text.add_argument("ref")
    text.add_argument("--lang", default="en", help="en, he, es, fr, de, ru, etc.")
    text.add_argument("--version-title")
    text.add_argument("--version", help="alternate Sefaria version selector, if needed")
    text.add_argument("--no-fallback", action="store_true")
    text.add_argument("--json", action="store_true")
    text.set_defaults(func=cmd_text)

    versions = sub.add_parser("versions", help="list available versions/translations for an index")
    versions.add_argument("index", help="book/work title, e.g. Genesis")
    versions.add_argument("--lang", help="filter by language")
    versions.add_argument("--json", action="store_true")
    versions.set_defaults(func=cmd_versions)

    index = sub.add_parser("index", help="show metadata for a Sefaria index")
    index.add_argument("title")
    index.add_argument("--json", action="store_true")
    index.set_defaults(func=cmd_index)

    toc = sub.add_parser("toc", help="list top-level Sefaria library categories")
    toc.add_argument("--json", action="store_true")
    toc.set_defaults(func=cmd_toc)

    related = sub.add_parser("related", help="summarize related material for a ref")
    related.add_argument("ref")
    related.add_argument("--json", action="store_true")
    related.set_defaults(func=cmd_related)

    langs = sub.add_parser("langs", help="list built-in language aliases")
    langs.add_argument("--json", action="store_true")
    langs.set_defaults(func=cmd_langs)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except (SefariaError, ValueError) as e:
        print(f"sefaria: error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
