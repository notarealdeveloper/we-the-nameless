from pathlib import Path

from yhwh import Corpus, SourceAttributor, Span, Verse, Verses

FIXTURE = Path(__file__).parent / "fixtures" / "mini"


def test_colored_reprs():
    corpus = Corpus.from_tex(FIXTURE, use_cache=False)
    assert "\x1b[90m" in repr(corpus.book("Genesis"))
    assert "\x1b[31m" in repr(corpus.chapter("Genesis", 1))
    assert "\x1b[34m" in repr(corpus.verse("Genesis", 1, 1))


def test_duplicate_records_retained_but_analytical_deduplicated():
    one = Verse("Genesis", 1, "1", "א", "one", (Span(0, 1, "J"),), (Span(0, 3, "J"),))
    two = Verse("Genesis", 1, "1", "אב", "one two", (Span(0, 2, "J"),), (Span(0, 7, "J"),))
    corpus = Corpus([one, two])
    assert len(corpus.records) == 2
    assert len(corpus) == 1
    assert len(corpus.variants("Genesis.1.1")) == 2
    assert corpus.verse("Genesis", 1, 1).english == "one two"


def test_frequency_fractional_source_assignment():
    verse = Verse(
        "Genesis",
        1,
        "1",
        "אב",
        "mixed",
        (Span(0, 1, "J"), Span(1, 2, "E")),
        (Span(0, 3, "J"), Span(3, 5, "E")),
    )
    values = Verses([verse]).frequencies_by_source("english", attribution="fractional")
    assert values["J"]["mixed"] == 3 / 5
    assert values["E"]["mixed"] == 2 / 5


def test_attribution_uses_known_words_and_oov_ngrams(tmp_path):
    verses = []
    for i, (source, text) in enumerate(
        [("J", "אמר יהוה אמר"), ("J", "יהוה ראה"), ("P", "אלהים ברא אלהים"), ("P", "ברא שמים")]
    ):
        verses.append(
            Verse(
                "Genesis",
                1,
                str(i + 1),
                text,
                "",
                (Span(0, len(text), source),),
                (),
            )
        )
    model = SourceAttributor.train(verses, sources=("J", "P"), language="hebrew")
    result = model.attribute("אמר יהוה")
    assert result.winner == "J"
    assert result.posterior["J"] > result.posterior["P"]
    assert result.known_tokens == 2
    oov = model.attribute("אמרר")
    assert oov.total_tokens == 1
    path = model.save(tmp_path / "model.json.gz")
    loaded = SourceAttributor.load(path)
    assert loaded.attribute("אלהים ברא").winner == "P"
