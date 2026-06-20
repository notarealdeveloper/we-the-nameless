MAIN  := master
PDF   := $(MAIN).pdf
BUILD := build
CACHE := $(abspath $(BUILD)/texmf-var)

LATEX      := lualatex
LATEXFLAGS := -interaction=nonstopmode -halt-on-error -output-directory=$(BUILD)

export TEXMFVAR := $(CACHE)

.PHONY: all clean distclean debug progress open build-prepare draft c x comment uncomment

all: $(PDF) open

build-prepare:
	@mkdir -p $(BUILD) $(CACHE)
	@find . -maxdepth 1 -type d -name '[0-9]*-*' -printf '$(BUILD)/%f\n' | xargs -r mkdir -p

$(PDF): $(MAIN).tex | build-prepare
	$(LATEX) $(LATEXFLAGS) $(MAIN).tex
	@if grep -q 'Rerun to get cross-references right' $(BUILD)/$(MAIN).log; then \
		$(LATEX) $(LATEXFLAGS) $(MAIN).tex; \
	fi
	cp $(BUILD)/$(MAIN).pdf .
	cp $(BUILD)/$(MAIN).log .

draft: $(MAIN).tex | build-prepare
	$(LATEX) $(LATEXFLAGS) -draftmode $(MAIN).tex

comment:
	bin/comments --comment $(MAIN).tex

uncomment:
	bin/comments --uncomment $(MAIN).tex

open:
	xdg-open $(BUILD)/$(PDF) >/dev/null 2>&1 &

clean:
	find [0-9][0-9]-* $(BUILD) -type f \( \
		-name '*.aux' -o \
		-name '*.log' -o \
		-name '*.toc' -o \
		-name '*.out' -o \
		-name '*.fls' -o \
		-name '*.fdb_latexmk' \
	\) -delete
	rm -f $(MAIN).aux $(MAIN).log $(MAIN).toc $(MAIN).out $(MAIN).pdf

distclean:
	rm -rf $(BUILD)
	rm -f $(MAIN).aux $(MAIN).log $(MAIN).toc $(MAIN).out $(MAIN).pdf

# for giving examples of the format to agents
c:
	cat $(MAIN).tex
	cat 01-genesis/01.tex
	cat 01-genesis/02.tex
	cat 01-genesis/03.tex

x:
	make c | xc

debug:
	codex exec "$$(printf '%s\n\n%s' \
		'This LuaLaTeX build failed. Read the log below and explain the likely cause and exact fix.' \
		"$$(cat $(BUILD)/$(MAIN).log)")"

progress:
	xdg-open $(MAIN).tex >/dev/null 2>&1 &
