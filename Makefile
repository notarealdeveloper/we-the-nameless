MAIN       := main
PDF        := $(MAIN).pdf
BUILD      := build
BUILD_PDF  := $(BUILD)/$(PDF)
CACHE      := $(abspath $(BUILD)/texmf-var)
LATEXMK    := latexmk
LATEXMKFLAGS := -lualatex \
	-interaction=nonstopmode \
	-halt-on-error \
	-file-line-error \
	-outdir=$(BUILD)

export TEXMFVAR := $(CACHE)

TEX_DIRS := $(sort $(dir $(shell find . -type f -name '*.tex' -not -path './$(BUILD)/*')))
BUILD_TEX_DIRS := $(addprefix $(BUILD)/,$(patsubst ./%,%,$(TEX_DIRS)))

.PHONY: all build clean debug progress open build-prepare

all: build open

build-prepare:
	mkdir -p $(BUILD) $(CACHE) $(BUILD_TEX_DIRS)

# Always ask latexmk to check its recorder database. It only runs LuaLaTeX when
# a source used by the previous build has changed.
build: | build-prepare
	$(LATEXMK) $(LATEXMKFLAGS) $(MAIN).tex
	@if ! cmp -s $(BUILD_PDF) $(PDF); then cp $(BUILD_PDF) $(PDF); fi

$(PDF): build

open: build
	xdg-open $(BUILD_PDF) >/dev/null 2>&1 &

clean:
	$(LATEXMK) -C -outdir=$(BUILD) $(MAIN).tex
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


# for giving examples of the format to agebts
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
	@( grep -Po '(?<=^\\include[{]).*(?=[}])' $(MAIN).tex | sort \
		| sed -E 's@(.*)@\1.tex@'; ) \
		| xargs -n1 echo

progress:
	( grep -Po '(?<=^\\include[{]).*(?=[}])' $(MAIN).tex | sort | head -n 5 \
		| sed -E 's@(.*)@\1.tex@'; ) \
		| xargs -n1 xdg-open & wait && xdg-open $(MAIN).tex
	( sleep 5 && xdotool key ctrl+0 ) &
