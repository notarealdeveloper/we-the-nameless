# Kindle ebook

`we-the-nameless.epub` is a reflowable EPUB 3 suitable for Kindle Previewer,
Kindle Create, KDP upload, or Send to Kindle. It preserves right-to-left Hebrew,
English translation, source-layer classes, commentary, footnotes, and navigation.

Build it with:

```sh
make -C ebook
```

To build one top-level book, use its lowercase name as the target; for example:

```sh
make -C ebook genesis
make -C ebook samuel
```

This writes `genesis.epub`, `samuel.epub`, and so on.

The build requires Pandoc 3. The generated EPUB is intentionally committed as a
distribution artifact; `build.py`, `metadata.yaml`, and `epub.css` are its
reproducible sources. Edit `metadata.yaml` before publication to add the final
author, publisher, identifier/ISBN, date, and rights statement.
