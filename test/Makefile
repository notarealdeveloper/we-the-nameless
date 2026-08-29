.DEFAULT_GOAL := view

TEX := fonts.tex
PDF := fonts.pdf
FONTS := paleo-hebrew-regular.ttf paleo-hebrew-evyoni.ttf
TEXMFVAR := $(CURDIR)/.texlive-cache

.PHONY: view clean

view: $(PDF)
	@xdg-open $(PDF) >/dev/null 2>&1 &

$(PDF): $(TEX) $(FONTS)
	TEXMFVAR="$(TEXMFVAR)" latexmk -lualatex -interaction=nonstopmode -halt-on-error $(TEX)

clean:
	TEXMFVAR="$(TEXMFVAR)" latexmk -C $(TEX)
