TEX = lualatex
TEXFLAGS = -interaction=nonstopmode -halt-on-error
NAME ?= eden
PDF = $(NAME).pdf
export TEXMFVAR := $(CURDIR)/.texmf-var

.PHONY: all default make pdf long short clean

all default make: eden.pdf

pdf: $(PDF)

long:
	$(MAKE) NAME=eden-long pdf

short:
	$(MAKE) NAME=eden-short pdf

$(PDF): welibc.tex $(NAME).tex
	$(TEX) $(TEXFLAGS) "$(NAME).tex"
	$(TEX) $(TEXFLAGS) "$(NAME).tex"

clean:
	rm -rf .texmf-var
	rm -f eden*.aux eden*.log eden*.out eden*.pdf eden*.toc
