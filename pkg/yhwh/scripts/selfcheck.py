#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from yhwh import Corpus, SourceAttributor, Span, Verse, build_dataset, find_english, find_hebrew


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    fixture = root / "tests" / "fixtures" / "mini"
    assert len(find_english("Fire firewood FIRE", "fire")) == 2
    assert find_hebrew("בְּ אֵשׁ", "באש")
    corpus = Corpus.from_tex(fixture, use_cache=False)
    assert len(corpus) == 3
    assert corpus.grep_hebrew("באש")[0].canonical_id == "Genesis.1.2"
    verse = corpus.verse("Genesis", 1, 1)
    assert verse.source_weights("english", verse.english.index("really"), verse.english.index("really") + 6) == {"R": 1.0}
    training = [
        Verse("Genesis", 1, "1", "אמר יהוה", "", (Span(0, 8, "J"),), ()),
        Verse("Genesis", 1, "2", "אלהים ברא", "", (Span(0, 9, "P"),), ()),
    ]
    model = SourceAttributor.train(training, sources=("J", "P"), language="hebrew")
    assert model.attribute("אמר").winner == "J"
    with tempfile.TemporaryDirectory() as directory:
        paths = build_dataset(corpus, directory, with_frequencies=False, with_models=False)
        assert len(Corpus.from_dataset(paths["jsonl"])) == 3
        assert len(Corpus.from_dataset(paths["sqlite"])) == 3
    print(json.dumps({"status": "pass", "fixture_verses": len(corpus)}))


if __name__ == "__main__":
    main()
