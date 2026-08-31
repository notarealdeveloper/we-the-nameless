"""A small executable tutorial: read this file from top to bottom."""

from pathlib import Path

import pytest

from yhwh import Corpus, find_english, find_hebrew, frequency_text


@pytest.fixture
def corpus():
    return Corpus.from_tex(Path(__file__).parent / "fixtures" / "mini", use_cache=False)


def test_text_tools_need_no_corpus():
    assert find_english("Fire and firewood", "fire")[0].text == "Fire"
    assert find_hebrew("בְּ אֵשׁ", "באש")[0].text == "בְּ אֵשׁ"
    assert frequency_text("one two two").most_common(1) == [("two", 2.0)]


def test_open_the_project_from_the_environment(monkeypatch, tmp_path):
    root = tmp_path / "the-book"
    chapter = root / "01-genesis"
    chapter.mkdir(parents=True)
    (chapter / "01.tex").write_text(r"\Chapter{1}\Verse{1}\hJ{בראשית}\eJ{In beginning}")
    monkeypatch.setenv("WE_THE_NAMELESS", str(root))
    monkeypatch.chdir(tmp_path)
    corpus = Corpus.from_tex(use_cache=False)
    assert len(corpus) == 1
    assert corpus.book_names == ("Genesis",)
    assert corpus.verse("Genesis", 1, 1).hebrew == "בראשית"
    assert corpus.verse("Genesis", 1, 1).english == "In beginning"


def test_walk_search_and_count(corpus):
    assert corpus.book("Genesis").chapter(1).verse(1).ref.id == "Genesis.1.1"
    assert corpus.grep_english("appeared")[0].english == "And he appeared in fire—and it burned."
    assert corpus.grep_hebrew("באש")[0].ref.id == "Genesis.1.2"
    assert corpus.verse("Genesis", 1, 1).sources() == ("P", "R")
    assert corpus.frequency("english")["beginning"] == 1
