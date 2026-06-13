MAIN      := main
PDF       := $(MAIN).pdf
BUILD     := build
LATEX     := lualatex
LATEXFLAGS := -interaction=nonstopmode -halt-on-error -file-line-error \
              -output-directory=$(BUILD)

.PHONY: all clean debug progress open

all: $(PDF) open

$(BUILD):
	mkdir -p $(BUILD)

$(PDF): $(MAIN).tex | $(BUILD)
	$(LATEX) $(LATEXFLAGS) $(MAIN).tex
	$(LATEX) $(LATEXFLAGS) $(MAIN).tex
	cp $(BUILD)/$(PDF) .

open:
	xdg-open $(PDF) >/dev/null 2>&1 &

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
	@test -f $(BUILD)/$(MAIN).log || { echo "No log at $(BUILD)/$(MAIN).log"; exit 1; }
	codex exec "$$(printf '%s\n\n%s' \
		'This LuaLaTeX build failed. Read the log below and explain the likely cause and exact fix.' \
		"$$(cat $(BUILD)/$(MAIN).log)")"

progress:
	texmaker -master $(MAIN).tex &
	grep -Po '(?<=^\\include[{]).*(?=[}])' $(MAIN).tex \
		| sed -E 's@(.*)@\1.tex@' \
		| xargs -r -n1 xdg-open
