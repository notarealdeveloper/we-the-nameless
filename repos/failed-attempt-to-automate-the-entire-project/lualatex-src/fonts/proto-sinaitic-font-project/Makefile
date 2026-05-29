FONT_NAME=ProtoSinaiticLocal
OUT=dist/$(FONT_NAME).ttf

all: $(OUT)

$(OUT): glyph_map.tsv glyphs/*.svg scripts/build_font.py
	mkdir -p dist
	fontforge -quiet -script scripts/build_font.py glyph_map.tsv glyphs $(OUT)

install: $(OUT)
	mkdir -p ~/.local/share/fonts
	cp $(OUT) ~/.local/share/fonts/
	fc-cache -fv

clean:
	rm -rf dist/*.ttf dist/*.otf

.PHONY: all install clean
