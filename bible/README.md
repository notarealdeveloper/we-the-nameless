# bible

Small Python package and CLI for querying and plotting the Jewish Bible in
Jewish book order.

The current data sources are the sibling `../eng/` and `../heb/` directories.
Chapter and verse counts are inferred from those files, and `bible grep` can
search English, Hebrew, or both.

Examples:

```sh
bible list gen
bible list "gen 22"
bible list -l both "gen 22:1"
bible grep -l eng "tested Abraham" "gen 22"
bible grep -l heb "אַבְרָהָם" "gen 22:1"
bible plot --output /tmp/books.png
bible plot books --output /tmp/books.png
bible plot verses "gen 22" --output /tmp/genesis-22.png
bible plot chapters exodus --output /tmp/exodus-chapters.png
bible plot chapters exodus --words --output /tmp/exodus-words-by-chapter.png
bible plot chapters exodus --chars --hebrew --output /tmp/exodus-hebrew-chars-by-chapter.png
bible plot chapter "exodus 20" --words --output /tmp/exodus-20-words-by-verse.png
```

The importable API exposes the same data:

```python
from bible import chapter_verses, get_verse_text, parse_ref

counts = chapter_verses()
text = get_verse_text(parse_ref("gen 22:1"), language="heb")
```

Verse-level output is formatted as `Book chapter:verse: text`, with text loaded
from `../eng/`, `../heb/`, or both. Plot commands use the books currently
present in those data directories, so `bible plot` defaults to the loaded-books
plot without requiring any extra reference argument.

`bible plot chapters BOOK` draws one bar for chapter 1, chapter 2, and so on.
By default the bars show verse counts. Add `--words` or `--chars` to total the
English verse text in each chapter, or add `--hebrew` to measure Hebrew text.
Hebrew character counts strip niqqud before counting. `bible plot chapter REF`
does the same kind of text measurement verse by verse inside one chapter.
