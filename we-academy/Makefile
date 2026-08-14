TEX = lualatex
TEXFLAGS = -interaction=nonstopmode -halt-on-error
NAME ?= eden
PDF = $(NAME).pdf
export TEXMFVAR := $(CURDIR)/.texmf-var

.PHONY: all default make pdf long short open-pdf clean

all default make: pdf

pdf: open-pdf

long:
	$(MAKE) NAME=eden-long pdf

short:
	$(MAKE) NAME=eden-short pdf

open-pdf: $(PDF)
	@if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$(PDF)" >/dev/null 2>&1 & \
	else \
		echo "Built $(PDF)"; \
	fi

$(PDF): welibc.tex $(NAME).tex
	$(TEX) $(TEXFLAGS) "$(NAME).tex"
	$(TEX) $(TEXFLAGS) "$(NAME).tex"

clean:
	rm -rf .texmf-var
	rm -f eden*.aux eden*.log eden*.out eden*.pdf eden*.toc
