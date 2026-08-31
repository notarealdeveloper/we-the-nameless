from yhwh import Frequency, SourceFrequencies, characteristic_words


def test_long_tail_characteristic_metrics():
    values = SourceFrequencies(
        {
            "J": Frequency({"said": 10, "walked": 8, "common": 20}),
            "P": Frequency({"said": 1, "tabernacle": 9, "common": 20}),
        }
    )
    profile = values.profile("tabernacle")
    assert profile["P"].enrichment_log2 > 0
    ranked = characteristic_words(values, source="P", min_count=1, limit=10)
    assert any(value.word == "tabernacle" for value in ranked)
