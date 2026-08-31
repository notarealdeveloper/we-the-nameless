from pathlib import Path

from yhwh import Corpus, discover_source_suffixes, extract_language, parse_tex_file

FIXTURE = Path(__file__).parent / "fixtures" / "mini"


def test_source_discovery_and_nested_spans():
    file = FIXTURE / "01-genesis" / "01.tex"
    text = file.read_text()
    assert {"J", "E", "P", "R"} <= discover_source_suffixes([text])
    parsed = parse_tex_file(file, source_suffixes={"J", "E", "P", "R"})
    verse = parsed.verses[0]
    assert verse.book == "Genesis"
    assert verse.chapter == 1
    assert "note must not enter" not in verse.english
    start = verse.english.index("really")
    weights = verse.source_weights("english", start, start + len("really"), canonical=False)
    assert weights == {"R": 1.0}
    assert sum(span.length for span in verse.english_spans) == len(verse.english)
    assert sum(span.length for span in verse.hebrew_spans) == len(verse.hebrew)


def test_extract_language_standalone():
    text, spans = extract_language(
        r"{\hJ{one \hE{two} three}} {\eJ{ignored}}", side="h", suffixes={"J", "E"}
    )
    assert text == "one two three"
    assert [(s.source, text[s.start : s.end]) for s in spans] == [
        ("J", "one "),
        ("E", "two"),
        ("J", " three"),
    ]


def test_corpus_search_crosses_hebrew_boundary():
    corpus = Corpus.from_tex(FIXTURE, use_cache=False)
    found = corpus.grep_hebrew("באש")
    assert [v.canonical_id for v in found] == ["Genesis.1.2"]
    assert found.match_info(found[0])[0].text.startswith("בְּ אֵש")


def test_mixed_outer_source_blocks_are_retained():
    corpus = Corpus.from_tex(FIXTURE, use_cache=False)
    verse = corpus.verse("Genesis", 1, 3)
    assert set(verse.sources("hebrew")) == {"J", "E"}
    assert "אָמַר" in verse.hebrew and "מֹשֶׁה" in verse.hebrew
