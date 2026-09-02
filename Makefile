MAIN  := master
PDF   := $(MAIN).pdf
TRANSLATION ?= default

# Keep the active settings in $(MAIN).tex as the defaults.  Command-line and
# environment assignments still take precedence through ?=.
read-config = $(strip $(shell sed -n 's/^[[:space:]]*\\def\\$(1)[[:space:]]*{\([^}]*\)}.*/\1/p' "$(MAIN).tex" | head -n 1))
OUTPUT_MODE ?= $(call read-config,ConfigOutputMode)
THEME ?= $(call read-config,ConfigTheme)
BUILD ?= build/$(OUTPUT_MODE)-$(THEME)
CACHE = $(BUILD)/texmf-var
TRANSLATION_LUA = $(BUILD)/translation-$(TRANSLATION).lua
LATEX_INPUT = \def\ConfigOutputMode{$(OUTPUT_MODE)}\def\ConfigTheme{$(THEME)}\def\ConfigEnglishTranslation{$(TRANSLATION)}\def\ConfigEnglishTranslationLuaFile{$(TRANSLATION_LUA)}\input{$(MAIN).tex}

BUILD_MODES := book-light book-dark mobile-light mobile-dark

LATEX      := lualatex
LATEXFLAGS = -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=$(BUILD)

TEX_SOURCES := $(shell find . -path './build' -prune -o -name '*.tex' -print)
SUBSET_TARGETS := $(shell bin/book-subset --make-targets)
BOOK_TARGETS := $(shell bin/book-subset --make-book-targets)
CHAPTER_TARGETS := $(shell bin/book-subset --make-chapter-targets)
COMMENT_BOOK_TARGETS := $(addprefix comment-,$(BOOK_TARGETS))
UNCOMMENT_BOOK_TARGETS := $(addprefix uncomment-,$(BOOK_TARGETS))

export TEXMFVAR = $(CACHE)
# Two Deuteronomy aux-file markers occupy exactly TeX's default 79-column
# print width.  Leave room for their separator so LuaTeX does not wrap a
# closing parenthesis onto the next build-output line.
export max_print_line = 80

.PHONY: all pdf build-pdf ci view open clean distclean debug progress parallel all-modes $(BUILD_MODES) build-prepare build-translation clean-stray-aux draft c x comment halfcomment uncomment again help list $(SUBSET_TARGETS) $(CHAPTER_TARGETS) $(COMMENT_BOOK_TARGETS) $(UNCOMMENT_BOOK_TARGETS)

all: $(PDF) open

help:
	@printf '%s\n' \
		'Public targets:' \
		'  make              Build master.pdf and open it.' \
		'  make pdf          Build master.pdf without opening it.' \
		'  make book-light   Build build/book-light/master.pdf (also: book-dark, mobile-light, mobile-dark).' \
		'  make all-modes    Build all four mode/theme combinations concurrently.' \
		'  make OUTPUT_MODE=mobile THEME=light pdf  Build one explicit combination.' \
		'  make TRANSLATION=kjv pdf  Build with translations/kjv instead of inline English.' \
		'  make parallel     Build the book with the parallel chapter workflow.' \
		'  make progress     Open master.tex.' \
		'  make comment      Comment out everything except the progress subset.' \
		'  make halfcomment  Comment out everything except the broader half-comment subset.' \
		'  make uncomment    Uncomment book/include lines in master.tex.' \
		'  make comment-genesis  Comment only Genesis; book aliases work for every book.' \
		'  make uncomment-genesis  Uncomment only Genesis; leave every other book unchanged.' \
		'  make list         List dynamic subset builds.' \
		'  make J            Build J.pdf: Yahwist text only, including records/poems used by J.' \
		'  make E            Build E.pdf: Elohist text only.' \
		'  make JE           Build JE.pdf: J + E + RJE text.' \
		'  make P            Build P.pdf: Priestly text only.' \
		'  make M            Build M.pdf: Mushite text, JE plus Deuteronomistic history.' \
		'  make A            Build A.pdf: Aaronid text, P plus selected Deuteronomistic sections and Ezra-Nehemiah.' \
		'  make j            Build j.pdf: Torah-only J text.' \
		'  make p            Build p.pdf: Torah-only P text.' \
		'  make r            Build r.pdf: full Torah with all sources.' \
		'  make R            Build R.pdf: Genesis through Nehemiah.' \
		'  make D            Build D.pdf: Deuteronomy through 2 Kings.' \
		'  make court        Build court.pdf: 1 Samuel through 1 Kings 2.' \
		'  make genesis      Build 01-genesis.pdf; numbered book targets also accept 1-genesis and 01-genesis forms.' \
		'  make genesis-1    Build only Genesis 1 as test-genesis-1.pdf and open it.' \
		'  make 1-samuel-1   Build only 1 Samuel 1; chapter targets share build/test/.' \
		'  make samuel       Build 08-samuel.pdf; use 1-samuel or 2-samuel for the individual books.' \
		'  make kings        Build 09-kings.pdf; use 1-kings or 2-kings for the individual books.' \
		'  make clean        Remove transient TeX aux files.' \
		'  make distclean    Remove build outputs and master.pdf.'

list:
	bin/book-subset --list

pdf: build-pdf

ci: build-pdf

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

build-translation: build-prepare
	@if [ "$(TRANSLATION)" != "default" ]; then \
		bin/book-translation-lua "$(TRANSLATION)" "$(TRANSLATION_LUA)"; \
	fi

build-pdf: $(BUILD)/$(PDF)
	cp "$(BUILD)/$(MAIN).pdf" .

$(BUILD)/$(PDF): $(TEX_SOURCES)
	$(MAKE) BUILD="$(BUILD)" TRANSLATION="$(TRANSLATION)" build-translation
	$(LATEX) $(LATEXFLAGS) "$(LATEX_INPUT)"
	$(MAKE) clean-stray-aux

$(PDF): build-pdf

$(BUILD_MODES):
	@mode="$(word 1,$(subst -, ,$@))"; \
	theme="$(word 2,$(subst -, ,$@))"; \
	$(MAKE) OUTPUT_MODE="$$mode" THEME="$$theme" BUILD="build/$@" build-pdf

all-modes:
	@$(MAKE) -j4 $(BUILD_MODES)

draft: $(MAIN).tex
	$(MAKE) BUILD="$(BUILD)" TRANSLATION="$(TRANSLATION)" build-translation
	$(LATEX) $(LATEXFLAGS) -draftmode "$(LATEX_INPUT)"
	$(MAKE) clean-stray-aux

clean-stray-aux:
	@find . -path "./build" -prune -o -type f \( \
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

$(COMMENT_BOOK_TARGETS):
	bin/comments --comment-book "$(@:comment-%=%)" $(MAIN).tex

$(UNCOMMENT_BOOK_TARGETS):
	bin/comments --uncomment-book "$(@:uncomment-%=%)" $(MAIN).tex

view open: $(PDF)
	@if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$(PDF)" >/dev/null 2>&1 & \
	else \
		echo "Built $(PDF)"; \
	fi

clean: clean-stray-aux
	@if [ -d build ]; then \
		find build -type f \( \
			-name '*.aux' -o \
			-name '*.log' -o \
			-name '*.toc' -o \
			-name '*.out' -o \
			-name '*.fls' -o \
			-name '*.fdb_latexmk' \
		\) -delete; \
	fi

distclean:
	rm -rf build
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
	xdg-open "$(MAIN).tex" >/dev/null 2>&1 &

parallel:
	bin/parallel-build --passes 1

$(SUBSET_TARGETS): BUILD = build/$@
$(SUBSET_TARGETS):
	$(MAKE) BUILD="$(BUILD)" TRANSLATION="$(TRANSLATION)" build-translation
	@set -e; \
	basename="$$(bin/book-subset --output-name "$@")"; \
	bin/book-subset --build-dir "$(BUILD)" "$@"; \
	$(LATEX) $(LATEXFLAGS) "\def\ConfigEnglishTranslation{$(TRANSLATION)}\def\ConfigEnglishTranslationLuaFile{$(TRANSLATION_LUA)}\input{$(BUILD)/$$basename.tex}"
	$(MAKE) clean-stray-aux
	@basename="$$(bin/book-subset --output-name "$@")"; \
	cp "$(BUILD)/$$basename.pdf" "$$basename.pdf"

$(CHAPTER_TARGETS): BUILD = build/test
$(CHAPTER_TARGETS):
	@$(MAKE) BUILD="build/test" TRANSLATION="$(TRANSLATION)" build-translation
	@set -e; \
	basename="$$(bin/book-subset --output-name "$@")"; \
	bin/book-subset --build-dir "build/test" "$@"; \
	$(LATEX) $(LATEXFLAGS) -jobname="test-$@" "\def\ConfigEnglishTranslation{$(TRANSLATION)}\def\ConfigEnglishTranslationLuaFile{$(TRANSLATION_LUA)}\input{build/test/$$basename.tex}"
	@$(MAKE) clean-stray-aux
	@cp "build/test/test-$@.pdf" "test-$@.pdf"
	@if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "test-$@.pdf" >/dev/null 2>&1 & \
	else \
		echo "Built test-$@.pdf"; \
	fi
