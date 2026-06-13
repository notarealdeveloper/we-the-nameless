MAIN       := main
PDF        := $(MAIN).pdf
BUILD      := build
LATEX      := lualatex
LATEXFLAGS := -interaction=nonstopmode -output-directory=$(BUILD)

INCLUDES := $(shell grep -Po '(?<=^\\include[{]).*(?=[}])' $(MAIN).tex)
INCLUDE_BUILD_DIRS := $(addprefix $(BUILD)/,$(sort $(dir $(INCLUDES))))

.PHONY: all clean debug progress open prepare-build

all: $(PDF) open

prepare-build:
	mkdir -p $(BUILD) $(INCLUDE_BUILD_DIRS)

$(PDF): $(MAIN).tex prepare-build
	$(LATEX) $(LATEXFLAGS) $(MAIN).tex
	cp $(BUILD)/$(MAIN).log .

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

debug:
	codex exec "$$(printf '%s\n\n%s' \
		'This LuaLaTeX build failed. Read the log below and explain the likely cause and exact fix.' \
		"$$(cat $(BUILD)/$(MAIN).log)")"

progress:
	( grep -Po '(?<=^\\include[{]).*(?=[}])' $(MAIN).tex | sort \
		| sed -E 's@(.*)@\1.tex@'; ) \
		| xargs -n1 xdg-open & wait && xdg-open $(MAIN).tex && sleep 5 && xdotool key ctrl+0
