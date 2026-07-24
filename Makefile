MAIN  := master
PDF   := $(MAIN).pdf
BUILD := build
CACHE := $(BUILD)/texmf-var

LATEX      := lualatex
LATEXFLAGS := -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=$(BUILD)

TEX_SOURCES := $(shell find . -path './$(BUILD)' -prune -o -name '*.tex' -print)

export TEXMFVAR := $(CACHE)

.PHONY: all pdf ci view open clean distclean debug progress build-prepare clean-stray-aux draft c x comment halfcomment uncomment again

all: $(PDF) open

pdf: $(PDF)

ci: $(PDF)

again:
	@if [ -f $(PDF) ]; then mv $(PDF) mistress.pdf; fi
	$(MAKE) all

build-prepare:
	@mkdir -p "$(BUILD)" "$(CACHE)"
	@sed -n 's|^[[:space:]]*\\include{\([^}]*\)}.*|\1|p' "$(MAIN).tex" | \
		while IFS= read -r include; do \
			dir=$$(dirname -- "$$include"); \
			mkdir -p "$(BUILD)/$$dir"; \
		done

$(PDF): $(TEX_SOURCES) | build-prepare
	$(LATEX) $(LATEXFLAGS) "$(MAIN).tex"
	@if grep -q 'Rerun to get cross-references right' "$(BUILD)/$(MAIN).log"; then \
		$(LATEX) $(LATEXFLAGS) "$(MAIN).tex"; \
	fi
	$(MAKE) clean-stray-aux
	cp "$(BUILD)/$(MAIN).pdf" .

draft: $(MAIN).tex | build-prepare
	$(LATEX) $(LATEXFLAGS) -draftmode "$(MAIN).tex"
	$(MAKE) clean-stray-aux

clean-stray-aux:
	@find . -path "./$(BUILD)" -prune -o -type f \( \
		-name '*.aux' -o \
		-name '*.log' -o \
		-name '*.toc' -o \
		-name '*.out' -o \
		-name '*.fls' -o \
		-name '*.fdb_latexmk' \
	\) -exec rm -f {} +
	@find The Nameless -depth -type d -empty -delete 2>/dev/null || true

comment:
	bin/comments --comment $(MAIN).tex

halfcomment:
	bin/comments --halfcomment $(MAIN).tex

uncomment:
	bin/comments --uncomment $(MAIN).tex

view open: $(PDF)
	@if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$(PDF)" >/dev/null 2>&1 & \
	else \
		echo "Built $(PDF)"; \
	fi

clean: clean-stray-aux
	@if [ -d $(BUILD) ]; then \
		find "$(BUILD)" -type f \( \
			-name '*.aux' -o \
			-name '*.log' -o \
			-name '*.toc' -o \
			-name '*.out' -o \
			-name '*.fls' -o \
			-name '*.fdb_latexmk' \
		\) -delete; \
	fi

distclean:
	rm -rf "$(BUILD)"
	rm -f "$(MAIN).pdf"

# for giving examples of the format to agents
c:
	cat $(MAIN).tex
	cat 01-genesis/01.tex
	cat 01-genesis/02.tex
	cat 01-genesis/03.tex

x:
	$(MAKE) c | xc

debug:
	codex exec "$$(printf '%s\n\n%s' \
		'This LuaLaTeX build failed. Read the log below and explain the likely cause and exact fix.' \
		"$$(cat $(BUILD)/$(MAIN).log)")"

progress:
	echo master.tex 01-genesis/0[12345]*.tex | lines | while IFS= read -r f; do xdg-open "$$f" >/dev/null 2>&1 & done
