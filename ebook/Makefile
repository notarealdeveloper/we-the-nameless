BOOKS := genesis exodus leviticus numbers deuteronomy joshua judges samuel kings dudetheyreontome

.PHONY: all clean $(BOOKS)

all: we-the-nameless.epub

we-the-nameless.epub: build.py epub.css metadata.yaml ../master.tex
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

$(BOOKS): build.py epub.css metadata.yaml ../master.tex
	./build.py --book "$(BOOK)" --output "$@.epub"

clean:
	rm -f we-the-nameless.epub $(BOOKS:%=%.epub) manuscript.generated.md
