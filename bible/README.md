# bible

Small Python package and CLI for querying and plotting Bible structure.

The current data sources are the sibling `../eng/` and `../heb/` directories.
Chapter and verse counts are inferred from those files, and `bible grep` can
search English, Hebrew, or both.

Examples:

```sh
bible list gen
bible list "gen 22"
bible grep -l eng "tested Abraham" "gen 22"
bible grep -l heb "אַבְרָהָם" "gen 22:1"
bible plot verses "gen 22" --output /tmp/genesis-22.png
bible plot chapters deut -o deu --output /tmp/deuteronomistic-history.png
```

The importable API exposes the same data:

```python
from bible import chapter_verses, get_verse_text, parse_ref

counts = chapter_verses()
text = get_verse_text(parse_ref("gen 22:1"), language="heb")
```

Orders whose books are not present in `../eng/` or `../heb/` still exist, but
raise `NotImplementedError` with a concrete TODO when counts or text are missing.
