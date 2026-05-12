from sefaria.models import flatten_text


def test_flatten_text():
    assert flatten_text(["a", ["b", "c"], [["d"]]]) == ["a", "b", "c", "d"]
