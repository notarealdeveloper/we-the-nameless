# sefaria

Small, boring Python tools for fetching texts from Sefaria.

It gives you:

- `sefaria`, a command-line tool
- `sefaria`, an importable Python package
- simple calls for Hebrew originals, translations, version discovery, index lookup, and related content

## Install

```sh
make develop
```

Or:

```sh
python -m pip install -e '.[dev]'
```

## Common commands

```sh
sefaria hebrew 'Genesis 1:1'
sefaria hebrew 'Genesis 1'
sefaria hebrew Genesis

sefaria text 'Genesis 1:1' --lang en
sefaria text 'Genesis 1:1' --lang en --version-title 'The Contemporary Torah, Jewish Publication Society, 2006'
sefaria text 'Genesis 1' --lang es

sefaria versions Genesis
sefaria versions Genesis --lang en
sefaria index Genesis
sefaria toc
sefaria related 'Genesis 1:1'
sefaria langs
```

Add `--json` to most commands when you want the raw Sefaria response.

## Python

```python
from sefaria import SefariaClient

s = SefariaClient()

print(s.get_hebrew("Genesis 1:1").plain())
print(s.get_text("Genesis 1:1", lang="en").plain())

versions = s.versions("Genesis")
for version in versions.for_lang("en"):
    print(version.version_title)
```

## Development

```sh
make develop
make check
make build
```

## Notes

- Refs are Sefaria refs: `Genesis 1:1`, `Genesis 1`, `Genesis`, etc.
- Language aliases work: `he`, `hebrew`, `en`, `english`, `es`, `spanish`, etc.
- The repo intentionally uses PyPA packaging tools plus ordinary Python modules.
