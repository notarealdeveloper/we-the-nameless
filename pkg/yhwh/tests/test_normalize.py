from yhwh import (
    find_english,
    find_hebrew,
    get_niqqud,
    normalize_hebrew,
    niqqud,
    set_niqqud,
    whitespace_tokens,
)


def test_hebrew_ignores_spaces_and_niqqud_by_default():
    matches = find_hebrew("בְּ אֵשׁ", "באש")
    assert len(matches) == 1
    assert matches[0].text == "בְּ אֵשׁ"
    assert find_hebrew("בְּ אֵשׁ", "באש", spaces=True) == []
    assert find_hebrew("בְּ אֵשׁ", "בְּאֵשׁ", niqqud=True)


def test_global_niqqud_context():
    old = set_niqqud(False)
    try:
        assert not get_niqqud()
        with niqqud(True):
            assert get_niqqud()
        assert not get_niqqud()
    finally:
        set_niqqud(old)


def test_matres_modes():
    assert normalize_hebrew("שלום", spaces=True, matres="keep") == "שלום"
    assert normalize_hebrew("שלום", spaces=True, matres="internal") == "שלם"
    assert normalize_hebrew("ויהי", spaces=True, matres="all") == ""


def test_english_word_and_phrase_behavior():
    text = "Fire firewood IN FIRE"
    assert [m.text for m in find_english(text, "fire")] == ["Fire", "FIRE"]
    assert [m.text for m in find_english(text, "in fire")] == ["IN FIRE"]
    assert len(find_english(text, "fire", whole_word=False)) == 3


def test_whitespace_is_only_token_boundary():
    tokens = [token for token, _, _ in whitespace_tokens("father-in-law God's אָמַר־יְהוָה")]
    assert tokens == ["father-in-law", "God's", "אָמַר־יְהוָה"]
