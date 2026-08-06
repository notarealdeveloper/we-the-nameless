import pytest

from bible.canon import order_books
from bible.refs import BookRef, ChapterRef, parse_ref, resolve_book


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
