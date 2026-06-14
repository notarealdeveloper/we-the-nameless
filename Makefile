MAIN       := main
PDF        := $(MAIN).pdf
BUILD      := build
CACHE      := $(abspath $(BUILD)/texmf-var)
LATEXMK    := latexmk
LATEXMKFLAGS := -lualatex \
	-interaction=nonstopmode \
	-halt-on-error \
	-file-line-error

export TEXMFVAR := $(CACHE)

CHAPTER_TEX := $(shell sed -n 's/^\\include{\([^}]*\)}.*/\1.tex/p' $(MAIN).tex)
DEV_CHAPTER_TEX := $(filter-out 1-genesis/apocrypha.tex,$(CHAPTER_TEX))
DEV_ROOT := $(BUILD)/dev
DEV_WRAPPERS := $(DEV_ROOT)/wrappers
DEV_AUX := $(DEV_ROOT)/aux
DEV_PDF := $(DEV_ROOT)/pdf
DEV_CHAPTER_PDFS := $(addprefix $(DEV_PDF)/,$(DEV_CHAPTER_TEX:.tex=.pdf))
DEV_PARTS := \
	$(DEV_PDF)/title.pdf \
	$(DEV_PDF)/cover.pdf \
	$(DEV_CHAPTER_PDFS) \
	$(DEV_PDF)/1-genesis/apocrypha.pdf
DEV_BUILD_PDF := $(DEV_ROOT)/$(PDF)
DEV_JOBS ?= $(shell nproc)

RELEASE_ROOT := $(BUILD)/release
RELEASE_PDF := $(RELEASE_ROOT)/$(PDF)
RELEASE_TEX_DIRS := $(addprefix $(RELEASE_ROOT)/,$(sort $(dir $(CHAPTER_TEX))))

.PHONY: all build dev-parts release clean debug progress open build-prepare

all: build open

build-prepare:
	mkdir -p $(BUILD) $(CACHE) $(DEV_ROOT) $(RELEASE_ROOT) $(RELEASE_TEX_DIRS)

# Development build: compile each independently cached part, then concatenate.
# A chapter edit therefore invokes LuaLaTeX for that chapter only.
build: | build-prepare
	$(MAKE) --no-print-directory -j$(DEV_JOBS) $(DEV_BUILD_PDF)
	@if ! cmp -s $(DEV_BUILD_PDF) $(PDF); then cp $(DEV_BUILD_PDF) $(PDF); fi

dev-parts: $(DEV_PARTS)

$(DEV_BUILD_PDF): $(DEV_PARTS)
	pdfunite $(DEV_PARTS) $@.tmp
	mv $@.tmp $@

$(DEV_PDF)/title.pdf: $(MAIN).tex bin/book-dev-wrapper | build-prepare
	@mkdir -p $(DEV_WRAPPERS) $(DEV_AUX)/title $(DEV_PDF)
	bin/book-dev-wrapper title $(DEV_WRAPPERS)/title.tex
	$(LATEXMK) $(LATEXMKFLAGS) -outdir=$(DEV_AUX)/title $(DEV_WRAPPERS)/title.tex
	cp $(DEV_AUX)/title/title.pdf $@

$(DEV_PDF)/cover.pdf: $(MAIN).tex cover.tex bin/book-dev-wrapper | build-prepare
	@mkdir -p $(DEV_WRAPPERS) $(DEV_AUX)/cover $(DEV_PDF)
	bin/book-dev-wrapper cover $(DEV_WRAPPERS)/cover.tex
	$(LATEXMK) $(LATEXMKFLAGS) -outdir=$(DEV_AUX)/cover $(DEV_WRAPPERS)/cover.tex
	cp $(DEV_AUX)/cover/cover.pdf $@

$(DEV_PDF)/%.pdf: %.tex $(MAIN).tex bin/book-dev-wrapper | build-prepare
	@mkdir -p $(dir $(DEV_WRAPPERS)/$*.tex) $(DEV_AUX)/$* $(dir $@)
	bin/book-dev-wrapper $< $(DEV_WRAPPERS)/$*.tex
	$(LATEXMK) $(LATEXMKFLAGS) -outdir=$(DEV_AUX)/$* $(DEV_WRAPPERS)/$*.tex
	cp $(DEV_AUX)/$*/$(notdir $*).pdf $@

# Production build: one document pass for continuous page numbers and TOC.
release: | build-prepare
	$(LATEXMK) $(LATEXMKFLAGS) -outdir=$(RELEASE_ROOT) $(MAIN).tex
	@if ! cmp -s $(RELEASE_PDF) $(PDF); then cp $(RELEASE_PDF) $(PDF); fi

open: build
	xdg-open $(DEV_BUILD_PDF) >/dev/null 2>&1 &

clean:
	rm -rf $(BUILD)
	find . -type f \( \
		-name '*.aux' -o \
		-name '*.log' -o \
		-name '*.toc' -o \
		-name '*.out' -o \
		-name '*.fls' -o \
		-name '*.fdb_latexmk' -o \
		-name '*.synctex.gz' \
	\) -delete

# for giving examples of the format to agents
c:
	cat $(MAIN).tex
	cat 1-genesis/01.tex
	cat 1-genesis/02.tex
	cat 1-genesis/03.tex

x:
	make c | xc

debug:
	codex exec "$$(printf '%s\n\n%s' \
		'This LuaLaTeX build failed. Read the log below and explain the likely cause and exact fix.' \
		"$$(cat $(RELEASE_ROOT)/$(MAIN).log)")"

list:
	@printf '%s\n' $(CHAPTER_TEX)

progress:
	( printf '%s\n' $(CHAPTER_TEX) | sort | head -n 5 ) \
		| xargs -n1 xdg-open & wait && xdg-open $(MAIN).tex
	( sleep 5 && xdotool key ctrl+0 ) &
