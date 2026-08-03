LATEXMK ?= latexmk
ENGINE ?= xelatex
TEXMFVAR ?= /tmp/dude-index-texmf-var
TEXMFCONFIG ?= /tmp/dude-index-texmf-config
TEXMFCACHE ?= /tmp/dude-index-texmf-cache
XDG_CACHE_HOME ?= /tmp/dude-index-cache

export TEXMFVAR := $(abspath $(TEXMFVAR))
export TEXMFCONFIG := $(abspath $(TEXMFCONFIG))
export TEXMFCACHE := $(abspath $(TEXMFCACHE))
export XDG_CACHE_HOME := $(abspath $(XDG_CACHE_HOME))

.PHONY: all clean

all: main.pdf

main.pdf: main.tex
	mkdir -p "$(TEXMFVAR)" "$(TEXMFCONFIG)" "$(TEXMFCACHE)" "$(XDG_CACHE_HOME)"
	$(LATEXMK) -pdf -$(ENGINE) -interaction=nonstopmode -halt-on-error main.tex

clean:
	$(LATEXMK) -C main.tex
