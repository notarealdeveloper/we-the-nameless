# yhwh

Read and search the source-colored Hebrew/English TeX in *We The Nameless*.

```bash
cd pkg/yhwh
python -m pip install -e .
export WE_THE_NAMELESS=/path/to/We\ The\ Nameless
```

```python
from yhwh import Corpus

corpus = Corpus.from_tex()
verse = corpus.verse("Genesis", 1, 1)
print(verse.hebrew)
print(verse.english)
print(verse.sources())

for verse in corpus.grep_english("and he said"):
    print(verse)

for verse in corpus.grep_hebrew("באש"):
    print(verse)
```

`Corpus.from_tex()` looks first at an explicit path, then `$WE_THE_NAMELESS`,
then the older `$YHWH_CORPUS`, and finally the current directory. A corpus root
contains chapter files at `[01][0-9]-*/*.tex`.

Run the tutorial and tests with:

```bash
make check
```

See `tests/test_tutorial.py` for small, executable examples of parsing, browsing,
searching, counting, and source inspection.
