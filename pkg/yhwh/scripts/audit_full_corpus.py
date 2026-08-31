#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from yhwh import Corpus, PRIMARY_HISTORY


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--output", type=Path, default=Path("full-corpus-audit.json"))
    parser.add_argument("--expected-verses", type=int, default=10165)
    parser.add_argument("--expected-records", type=int, default=10189)
    args = parser.parse_args()

    corpus = Corpus.from_tex(args.corpus, use_cache=False)
    issues = corpus.validate()
    errors = [issue for issue in issues if issue.level == "error"]
    warnings = [issue for issue in issues if issue.level == "warning"]
    missing_hebrew = sum(not verse.hebrew for verse in corpus.records)
    missing_english = sum(not verse.english for verse in corpus.records)
    raw_sources = Counter(span.source for verse in corpus.records for span in verse.hebrew_spans)
    checks = {
        "analytical_verse_count": len(corpus) == args.expected_verses,
        "record_count": len(corpus.records) == args.expected_records,
        "all_primary_history_books": set(PRIMARY_HISTORY) <= set(corpus.book_names),
        "core_sources_present": {"J", "E", "P"} <= set(raw_sources),
        "no_span_errors": not errors,
        "hebrew_coverage": missing_hebrew / max(1, len(corpus.records)) < 0.02,
        "english_coverage": missing_english / max(1, len(corpus.records)) < 0.02,
    }
    report = {
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "summary": corpus.summary(),
        "missing_hebrew": missing_hebrew,
        "missing_english": missing_english,
        "validation_errors": [issue.__dict__ for issue in errors],
        "validation_warnings": [issue.__dict__ for issue in warnings],
        "source_record_spans": dict(raw_sources),
    }
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
