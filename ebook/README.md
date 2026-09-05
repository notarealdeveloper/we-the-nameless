# Kindle ebook

`we-the-nameless.epub` is a reflowable EPUB 3 suitable for Kindle Previewer,
Kindle Create, KDP upload, or Send to Kindle. It preserves right-to-left Hebrew,
English translation, source-layer classes, commentary, footnotes, and navigation.

Build it with:

```sh
make -C ebook
```

The build requires Pandoc 3. The generated EPUB is intentionally committed as a
distribution artifact; `build.py`, `metadata.yaml`, and `epub.css` are its
reproducible sources. Edit `metadata.yaml` before publication to add the final
author, publisher, identifier/ISBN, date, and rights statement.
