from __future__ import annotations

from bible.__main__ import main


def test_cat_prints_book_text(capsys):
    assert main(["cat", "genesis"]) == 0

    lines = capsys.readouterr().out.splitlines()
    assert lines[0].startswith("Genesis 1:1 :: In the beginning")
    assert any(line.startswith("Genesis 50:26 :: And Joseph died") for line in lines)


def test_cat_prints_chapter_text(capsys):
    assert main(["cat", "exodus", "15"]) == 0

    lines = capsys.readouterr().out.splitlines()
    assert lines[0].startswith("Exodus 15:1 :: Then Moses")
    assert lines[-1].startswith("Exodus 15:27 :: And they came to Elim")


def test_cat_accepts_language_path_prefix(capsys):
    assert main(["cat", "heb/exodus", "15:1"]) == 0

    assert capsys.readouterr().out.startswith("Exodus 15:1 :: אָז יָשִׁיר")


def test_grep_prints_grep_style_location_and_content(capsys):
    assert main(["grep", "tested Abraham", "gen", "22"]) == 0

    assert capsys.readouterr().out.startswith("Genesis 22:1: And it was after")


def test_grep_defaults_to_all_loaded_books(capsys):
    assert main(["grep", "tested Abraham"]) == 0

    assert "Genesis 22:1: And it was after" in capsys.readouterr().out


def test_grep_returns_one_without_matches(capsys):
    assert main(["grep", "this pattern should not match anything"]) == 1

    assert capsys.readouterr().out == ""
