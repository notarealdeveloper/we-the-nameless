import pytest

from bible.canon import available_books, chapter_verses, order_books
from bible.refs import BookRef, ChapterRef, parse_ref, resolve_book
from bible.text import get_verse_text


def test_resolve_book_accepts_prefix_and_case():
    assert resolve_book("gen") == "Genesis"
    assert resolve_book("Genesis") == "Genesis"
    assert resolve_book("GEN") == "Genesis"


def test_parse_quoted_and_unquoted_chapter_refs():
    assert parse_ref(["genesis", "22"]) == ChapterRef("Genesis", 22)
    assert parse_ref("gen 22") == ChapterRef("Genesis", 22)


def test_parse_book_ref():
    assert parse_ref(["gen"]) == BookRef("Genesis")


def test_apocrypha_order_key_exists_but_needs_counts():
    with pytest.raises(NotImplementedError, match="TODO: provide chapter and verse counts"):
        order_books("apo")


def test_chapter_counts_are_loaded_from_local_text_data():
    counts = chapter_verses()
    assert counts["Genesis"][0] == 31
    assert counts["Genesis"][21] == 24
    assert counts["1 Samuel"][0] == 28
    assert "Genesis" in available_books()


def test_deuteronomistic_history_excludes_ruth():
    assert order_books("deu") == (
        "Deuteronomy",
        "Joshua",
        "Judges",
        "1 Samuel",
        "2 Samuel",
        "1 Kings",
        "2 Kings",
    )


def test_english_and_hebrew_text_are_importable():
    ref = parse_ref("gen 22:1")
    assert "God tested Abraham" in get_verse_text(ref)
    assert "אַבְרָהָם" in get_verse_text(ref, language="heb")
