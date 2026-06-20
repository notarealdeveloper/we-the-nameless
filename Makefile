MAIN  := master
PDF   := $(MAIN).pdf
BUILD := build
CACHE := $(abspath $(BUILD)/texmf-var)

LATEX      := lualatex
LATEXFLAGS := -interaction=nonstopmode -halt-on-error -output-directory=$(BUILD)

export TEXMFVAR := $(CACHE)

INCLUDES := $(shell grep -Po '(?<=^\\include[{]).*(?=[}])' $(MAIN).tex)
INCLUDE_SOURCES := $(addsuffix .tex,$(INCLUDES))
INCLUDE_BUILD_DIRS := $(addprefix $(BUILD)/,$(sort $(dir $(INCLUDES))))

SOURCES := $(MAIN).tex $(INCLUDE_SOURCES)

.PHONY: all clean distclean debug progress open build-prepare draft c x list

all: $(PDF) open

build-prepare:
	@mkdir -p $(BUILD) $(CACHE) $(INCLUDE_BUILD_DIRS)

$(PDF): $(SOURCES) | build-prepare
	$(LATEX) $(LATEXFLAGS) $(MAIN).tex
	@if grep -q 'Rerun to get cross-references right' $(BUILD)/$(MAIN).log; then \
		$(LATEX) $(LATEXFLAGS) $(MAIN).tex; \
	fi
	cp $(BUILD)/$(MAIN).pdf .
	cp $(BUILD)/$(MAIN).log .

draft: $(SOURCES) | build-prepare
	$(LATEX) $(LATEXFLAGS) -draftmode $(MAIN).tex

open:
	xdg-open $(BUILD)/$(PDF) >/dev/null 2>&1 &

clean:
	find [12345]-* $(BUILD) -type f \( \
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
	cat 1-genesis/01.tex
	cat 1-genesis/02.tex
	cat 1-genesis/03.tex

x:
	make c | xc

debug:
	codex exec "$$(printf '%s\n\n%s' \
		'This LuaLaTeX build failed. Read the log below and explain the likely cause and exact fix.' \
		"$$(cat $(BUILD)/$(MAIN).log)")"

list:
	@printf '%s\n' $(INCLUDE_SOURCES) | sort

progress:
	( printf '%s\n' $(INCLUDE_SOURCES) | sort | head -n 5 \
		| xargs -n1 xdg-open ) & wait && xdg-open $(MAIN).tex
	( sleep 5 && xdotool key ctrl+0 ) &
