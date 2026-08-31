.DEFAULT_GOAL := pdf

TEX := master.tex
PDF := master.pdf
FONTS := ../../fonts/paleo-hebrew-regular.ttf \
	../../fonts/paleo-hebrew-evyoni.ttf \
	../../fonts/paleo-hebrew-alphabet.ttf
TEXMFVAR := $(CURDIR)/.texlive-cache

.PHONY: pdf view clean

pdf: $(PDF)

view: $(PDF)
	@xdg-open $(PDF) >/dev/null 2>&1 &

$(PDF): $(TEX) $(FONTS)
	TEXMFVAR="$(TEXMFVAR)" latexmk -lualatex -interaction=nonstopmode -halt-on-error $(TEX)

clean:
	TEXMFVAR="$(TEXMFVAR)" latexmk -C $(TEX)
