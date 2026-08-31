from pathlib import Path

from yhwh import Corpus, build_dataset
from yhwh.cli import main

FIXTURE = Path(__file__).parent / "fixtures" / "mini"


def test_dataset_jsonl_sqlite_roundtrip(tmp_path):
    corpus = Corpus.from_tex(FIXTURE, use_cache=False)
    paths = build_dataset(
        corpus,
        tmp_path,
        with_frequencies=False,
        with_models=False,
    )
    jsonl = Corpus.from_dataset(paths["jsonl"])
    sqlite = Corpus.from_dataset(paths["sqlite"])
    assert [v.to_dict(include_raw=False) for v in jsonl] == [v.to_dict(include_raw=False) for v in sqlite]
    assert (tmp_path / "manifest.json").exists()


def test_cli_search_and_freq(capsys):
    assert main(["--corpus", str(FIXTURE), "search", "באש", "--language", "hebrew"]) == 0
    assert "Genesis 1:2" in capsys.readouterr().out
    assert main(["--corpus", str(FIXTURE), "freq", "--scope", "all", "--top", "3"]) == 0
    assert capsys.readouterr().out
