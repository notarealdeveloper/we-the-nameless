from sefaria.client import normalize_lang


def test_normalize_lang():
    assert normalize_lang("Hebrew") == "he"
    assert normalize_lang("english") == "en"
    assert normalize_lang("es") == "es"
