.DEFAULT_GOAL := view

TEX := egypt.tex
PDF := egypt.pdf
TEXMFVAR := $(CURDIR)/.texlive-cache

.PHONY: view clean

view: $(PDF)
	@xdg-open $(PDF) >/dev/null 2>&1 &

$(PDF): $(TEX) ../fonts/NewGardiner.ttf
	TEXMFVAR="$(TEXMFVAR)" latexmk -lualatex -interaction=nonstopmode -halt-on-error $(TEX)

clean:
	TEXMFVAR="$(TEXMFVAR)" latexmk -C $(TEX)
