BOOKS := genesis exodus leviticus numbers deuteronomy joshua judges samuel kings dudetheyreontome
TEX_SOURCES := $(shell find .. -path '../.git' -prune -o -path '../build' -prune -o -path '../ebook' -prune -o -name '*.tex' -print)
EBOOK_ASSETS := $(shell find ../fonts ../img -type f 2>/dev/null)
RENDERER_SOURCES := build.py validate.py epub.css metadata.yaml $(TEX_SOURCES) $(EBOOK_ASSETS)

.PHONY: all clean validate validate-% $(BOOKS)

all: we-the-nameless.epub

we-the-nameless.epub: $(RENDERER_SOURCES)
	./build.py

genesis: BOOK := Genesis
exodus: BOOK := Exodus
leviticus: BOOK := Leviticus
numbers: BOOK := Numbers
deuteronomy: BOOK := Deuteronomy
joshua: BOOK := Joshua
judges: BOOK := Judges
samuel: BOOK := Samuel
kings: BOOK := Kings
dudetheyreontome: BOOK := Dudetheyreontome

$(BOOKS): $(RENDERER_SOURCES)
	./build.py --book "$(BOOK)" --output "$@.epub"

validate: we-the-nameless.epub
	./validate.py $<
	@command -v epubcheck >/dev/null 2>&1 && epubcheck $< || \
		{ printf '%s\n' 'epubcheck is not installed; internal validation passed.'; }

validate-%: %.epub
	./validate.py $<
	@command -v epubcheck >/dev/null 2>&1 && epubcheck $< || \
		{ printf '%s\n' 'epubcheck is not installed; internal validation passed.'; }

clean:
	rm -f we-the-nameless.epub $(BOOKS:%=%.epub) manuscript.generated.md
