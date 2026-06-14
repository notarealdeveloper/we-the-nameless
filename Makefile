MAIN       := main
PDF        := $(MAIN).pdf
BUILD      := build
CACHE      := $(abspath $(BUILD)/texmf-var)
LATEX      := lualatex
LATEXFLAGS := -interaction=nonstopmode -output-directory=$(BUILD)

export TEXMFVAR := $(CACHE)

INCLUDES := $(shell grep -Po '(?<=^\\include[{]).*(?=[}])' $(MAIN).tex)
INCLUDE_BUILD_DIRS := $(addprefix $(BUILD)/,$(sort $(dir $(INCLUDES))))

.PHONY: all clean debug progress open build-prepare

all: $(PDF) open

build-prepare:
	mkdir -p $(BUILD) $(CACHE) $(INCLUDE_BUILD_DIRS)

$(PDF): $(MAIN).tex build-prepare
	$(LATEX) $(LATEXFLAGS) $(MAIN).tex
	cp $(BUILD)/$(MAIN).log .
	( sleep 5 && rm $(MAIN).log ) &

open:
	xdg-open $(BUILD)/$(PDF) >/dev/null 2>&1 &

clean:
	rm -rf $(BUILD)
	rm -f $(MAIN).pdf
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
