.PHONY: all clean

all: we-the-nameless.epub

we-the-nameless.epub: build.py epub.css metadata.yaml ../master.tex
	./build.py

clean:
	rm -f we-the-nameless.epub manuscript.generated.md
