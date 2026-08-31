#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def marker(name: str) -> bool:
    return (ROOT / name).exists()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def main() -> None:
    audit = ROOT / "audit"
    audit.mkdir(exist_ok=True)
    for name in (
        "compile.log",
        "import.log",
        "pytest.log",
        "selfcheck.log",
        "corpus-info.json",
        "corpus-info.err",
        "full-corpus-audit.json",
        "full-audit.log",
        "dataset-build.log",
        "dataset-build-no-models.log",
        "dataset-build-core.log",
        "audit-status.txt",
    ):
        source = ROOT / name
        if source.exists():
            shutil.copy2(source, audit / name)

    checks: dict[str, Any] = {
        "python_compilation": marker(".compile-pass"),
        "package_import": marker(".import-pass"),
        "unit_tests": marker(".test-pass"),
        "dependency_free_selfcheck": marker(".selfcheck-pass"),
        "full_corpus_parse": marker(".corpus-pass"),
        "expected_full_corpus_invariants": marker(".full-audit-pass"),
        "complete_dataset_build": marker(".dataset-pass"),
        "dataset_with_frequencies_without_models": marker(".dataset-core-plus-frequencies-pass"),
        "core_dataset_build": marker(".dataset-core-pass"),
    }
    full = load_json(ROOT / "full-corpus-audit.json")
    manifest = load_json(ROOT / "dataset" / "manifest.json")
    smoke: dict[str, Any] = {}
    try:
        from yhwh import Corpus, SourceAttributor

        jsonl = ROOT / "dataset" / "primary-history.jsonl.gz"
        if jsonl.exists():
            corpus = Corpus.from_dataset(jsonl)
            smoke["dataset_load"] = True
            smoke["dataset_analytical_verses"] = len(corpus)
            smoke["dataset_records"] = len(corpus.records)
            smoke["hebrew_cross_boundary_api"] = isinstance(corpus.grep_hebrew("באש"), list)
        else:
            smoke["dataset_load"] = False
        model_path = ROOT / "dataset" / "models" / "torah-hebrew-hybrid.json.gz"
        if model_path.exists():
            model = SourceAttributor.load(model_path)
            result = model.attribute("וַיֹּאמֶר יְהוָה")
            smoke["model_load_and_score"] = True
            smoke["model_smoke_winner"] = result.winner
            smoke["model_smoke_sources"] = list(result.posterior)
        else:
            smoke["model_load_and_score"] = False
    except Exception as error:
        smoke["exception"] = f"{type(error).__name__}: {error}"
        smoke["traceback"] = traceback.format_exc()

    status = {
        "checks": checks,
        "full_corpus_audit": full,
        "dataset_manifest": manifest,
        "release_smoke": smoke,
    }
    status["release_ready"] = bool(
        checks["python_compilation"]
        and checks["package_import"]
        and checks["dependency_free_selfcheck"]
        and checks["full_corpus_parse"]
        and smoke.get("dataset_load")
    )
    (audit / "release-audit.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# Release audit",
        "",
        "This report is generated from marker files and executable smoke checks, not hand-edited.",
        "",
        f"**Release ready:** `{status['release_ready']}`",
        "",
        "## Checks",
        "",
    ]
    for key, value in checks.items():
        lines.append(f"- `{key}`: `{value}`")
    if full:
        lines.extend(["", "## Full corpus", ""])
        summary = full.get("summary", {})
        for key in ("analytical_verses", "records", "duplicates", "books", "source_suffixes", "warnings"):
            if key in summary:
                lines.append(f"- `{key}`: `{summary[key]}`")
        lines.append(f"- invariant status: `{full.get('status')}`")
    if manifest:
        lines.extend(["", "## Dataset", ""])
        for key in ("records", "analytical_verses", "duplicates_retained", "books", "source_suffixes"):
            if key in manifest:
                lines.append(f"- `{key}`: `{manifest[key]}`")
        lines.append(f"- generated files: `{len(manifest.get('files', {}))}`")
    lines.extend(["", "## Executable release smoke test", ""])
    for key, value in smoke.items():
        if key != "traceback":
            lines.append(f"- `{key}`: `{value}`")
    (ROOT / "AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
