TEX = lualatex
NAME ?= master
BUILDDIR = build
TEXFLAGS = -interaction=nonstopmode -halt-on-error -output-directory="$(BUILDDIR)"
PDF = $(NAME).pdf
BUILDPDF = $(BUILDDIR)/$(PDF)
export TEXMFVAR := $(CURDIR)/$(BUILDDIR)/texmf-var

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

$(PDF): $(BUILDPDF)
	cp "$(BUILDPDF)" "$(PDF)"

$(BUILDPDF): welibc.tex $(NAME).tex | $(BUILDDIR)
	$(TEX) $(TEXFLAGS) "$(NAME).tex"
	$(TEX) $(TEXFLAGS) "$(NAME).tex"

$(BUILDDIR):
	mkdir -p "$(BUILDDIR)"

clean:
	rm -rf "$(BUILDDIR)"
	rm -f eden*.aux eden*.log eden*.out eden*.pdf eden*.toc
