TEX = lualatex
TEXFLAGS = -interaction=nonstopmode -halt-on-error
export TEXMFVAR := $(CURDIR)/.texmf-var

.PHONY: all clean

all: master.pdf

master.pdf: master.tex welibc.tex eden.tex
	$(TEX) $(TEXFLAGS) master.tex
	$(TEX) $(TEXFLAGS) master.tex

clean:
	rm -rf .texmf-var
	rm -f master.aux master.log master.out master.pdf master.toc
