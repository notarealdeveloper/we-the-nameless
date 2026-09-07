MAIN  := master
PDF   := $(MAIN).pdf
# Keep the active settings in $(MAIN).tex as the defaults.  Command-line and
# environment assignments still take precedence through ?=.
read-config = $(strip $(shell sed -n 's/^[[:space:]]*\\def\\$(1)[[:space:]]*{\([^}]*\)}.*/\1/p' "$(MAIN).tex" | head -n 1))
OUTPUT_MODE ?= $(call read-config,ConfigOutputMode)
THEME ?= $(call read-config,ConfigTheme)
VERSE_LAYOUT ?= $(call read-config,ConfigVerseLayout)
COMMENTARY ?= $(call read-config,ConfigCommentary)
TRANSLATION ?= $(call read-config,ConfigEnglishTranslation)
TITLE_PAGE_STYLE ?= $(call read-config,IndividualBookTitlePageStyle)
COLORS ?= $(call read-config,ConfigColors)
APOCRYPHA ?= $(call read-config,ConfigApocrypha)
REDACTOR ?= $(call read-config,ConfigRedactor)
COVER ?= $(call read-config,ConfigCover)
BUILD ?= build/$(OUTPUT_MODE)-$(THEME)
CACHE = $(BUILD)/texmf-var
TRANSLATION_LUA = $(BUILD)/translation-$(TRANSLATION).lua
LATEX_CONFIG = \def\ConfigOutputMode{$(OUTPUT_MODE)}\def\ConfigTheme{$(THEME)}\def\ConfigVerseLayout{$(VERSE_LAYOUT)}\def\ConfigCommentary{$(COMMENTARY)}\def\ConfigEnglishTranslation{$(TRANSLATION)}\def\IndividualBookTitlePageStyle{$(TITLE_PAGE_STYLE)}\def\ConfigColors{$(COLORS)}\def\ConfigApocrypha{$(APOCRYPHA)}\def\ConfigRedactor{$(REDACTOR)}\def\ConfigCover{$(COVER)}\def\ConfigEnglishTranslationLuaFile{$(TRANSLATION_LUA)}
KDP_LATEX_CONFIG = $(LATEX_CONFIG)\def\ConfigKDP{true}\def\KDPAssetDir{build/kdp-assets}
LATEX_INPUT = $(LATEX_CONFIG)\input{$(MAIN).tex}

BUILD_MODES := book-lite book-dark tech-lite tech-dark

LATEX      := lualatex
LATEXFLAGS = -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=$(BUILD)

TEX_SOURCES := $(shell find . -path './build' -prune -o -name '*.tex' -print)
SUBSET_TARGETS := $(shell bin/book-subset --make-targets)
BOOK_TARGETS := $(shell bin/book-subset --make-book-targets)
CHAPTER_TARGETS := $(shell bin/book-subset --make-chapter-targets)
COMMENT_BOOK_TARGETS := $(addprefix comment-,$(BOOK_TARGETS))
UNCOMMENT_BOOK_TARGETS := $(addprefix uncomment-,$(BOOK_TARGETS))
EBOOK_BOOKS := genesis exodus leviticus numbers deuteronomy joshua judges samuel kings dudetheyreontome
EBOOK_TARGETS := $(addsuffix -ebook,$(EBOOK_BOOKS))
KDP_TARGETS := $(addsuffix -kdp,$(SUBSET_TARGETS))
COVER_TARGETS := $(addsuffix -cover,$(SUBSET_TARGETS))
COVER_INTERIOR ?= 01-genesis.pdf
COVER_PAPER ?= standard-color
COVER_STYLE ?= simple
COVER_VOLUME ?=
COVER_OUTPUT ?= 01-genesis-cover.pdf
COVER_BUILD ?= build/cover
KDP_INPUT ?=
KDP_OUTPUT ?=

export TEXMFVAR = $(CACHE)
# Keep every aux-file marker on its own line without splitting any of the
# Pentateuch paths themselves.
export max_print_line = 60

.PHONY: all pdf build-pdf ci view open clean distclean debug progress parallel all-modes ebook ebook-validate cover kdp kdp-preflight $(KDP_TARGETS) $(COVER_TARGETS) $(EBOOK_TARGETS) $(BUILD_MODES) build-prepare build-translation clean-stray-aux draft c x comment halfcomment uncomment again help list $(SUBSET_TARGETS) $(CHAPTER_TARGETS) $(COMMENT_BOOK_TARGETS) $(UNCOMMENT_BOOK_TARGETS)

define publish-and-open
	@set -e; \
	if [ "$(OUTPUT_MODE)-$(THEME)" = "book-lite" ]; then \
		published="mistress.pdf"; \
	else \
		published="master.pdf"; \
	fi; \
	cp "$(1)" "$$published"; \
	if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$published" >/dev/null 2>&1 & \
	else \
		echo "Built $$published"; \
	fi
endef

all: $(BUILD)/$(PDF)
	$(call publish-and-open,$(BUILD)/$(PDF))

help:
	@printf '%s\n' \
		'Public targets:' \
		'  make              Build and open master.pdf (tech-dark) or mistress.pdf (book-lite).' \
		'  make pdf          Build master.pdf without opening it.' \
		'  make book-lite    Build build/book-lite/master.pdf (also: book-dark, tech-lite, tech-dark).' \
		'  make all-modes    Build all four mode/theme combinations concurrently.' \
		'  make OUTPUT_MODE=tech THEME=lite pdf  Build one explicit combination.' \
		'  make THEME=lite COLORS=lighter pdf  Use the lighter lite-mode palette.' \
		'  make APOCRYPHA=canonical pdf  Build without apocrypha (default: apocryphal).' \
		'  make VERSE_LAYOUT=vertical COMMENTARY=false pdf  Override verse layout and commentary.' \
		'  make TITLE_PAGE_STYLE=plain REDACTOR=censored pdf  Override title pages and redaction.' \
		'  make COVER=none pdf  Build without the configured cover image.' \
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
		'  make genesis-kdp  Build 01-genesis-kdp.pdf and its 01-genesis-cover.pdf wrap.' \
		'  make genesis-cover  Build the matching wrap from an existing 01-genesis.pdf.' \
		'  make kdp KDP_INPUT=file.pdf KDP_OUTPUT=file-kdp.pdf  Preflight any existing interior PDF.' \
		'  make kdp-preflight KDP_INPUT=file.pdf  Report without changing the PDF.' \
		'  make genesis-1    Build only Genesis 1 as test-genesis-1.pdf and open it.' \
		'  make 1-samuel-1   Build only 1 Samuel 1; chapter targets share build/test/.' \
		'  make samuel       Build 08-samuel.pdf; use 1-samuel or 2-samuel for the individual books.' \
		'  make ebook        Build ebook/we-the-nameless.epub.' \
		'  make genesis-ebook  Build ebook/genesis.epub; equivalent targets exist for each book.' \
		'  make ebook-validate  Validate the complete EPUB (building it first if needed).' \
		'  make cover        Build a KDP paperback wrap as 01-genesis-cover.pdf from 01-genesis.pdf.' \
		'                    Set COVER_STYLE=simple|fancy; COVER_PAPER defaults to standard-color.' \
		'  make kings        Build 09-kings.pdf; use 1-kings or 2-kings for the individual books.' \
		'  make clean        Remove transient TeX aux files.' \
		'  make distclean    Remove build outputs and master.pdf.'

list:
	bin/book-subset --list

ebook:
	$(MAKE) -C ebook all

ebook-validate:
	$(MAKE) -C ebook validate

cover:
	@bin/kdp-cover "$(COVER_INTERIOR)" "$(COVER_PAPER)" "$(COVER_OUTPUT)" "$(COVER_BUILD)" "$(COVER_STYLE)" "$(COVER_VOLUME)"

kdp:
	@test -n "$(KDP_INPUT)" || { echo 'KDP_INPUT is required' >&2; exit 2; }
	@bin/kdp-pdf "$(KDP_INPUT)" "$(if $(KDP_OUTPUT),$(KDP_OUTPUT),$(basename $(KDP_INPUT))-kdp.pdf)"

kdp-preflight:
	@test -n "$(KDP_INPUT)" || { echo 'KDP_INPUT is required' >&2; exit 2; }
	@bin/kdp-preflight "$(KDP_INPUT)"

$(KDP_TARGETS): %-kdp:
	@$(MAKE) "$*"
	@$(MAKE) "$*-cover"
	@basename="$$(bin/book-subset --output-name "$*")"; \
	bin/kdp-pdf "$$basename.pdf" "$$basename-kdp.pdf"

$(COVER_TARGETS): %-cover:
	@set -e; \
	basename="$$(bin/book-subset --output-name "$*")"; \
	title="$$(printf '%s\n' "$${basename#??-}" | awk -F- '{ for (i=1; i<=NF; i++) { if ($$i ~ /^[a-z]/) $$i=toupper(substr($$i,1,1)) substr($$i,2); printf "%s%s", (i > 1 ? " " : ""), $$i } }')"; \
	interior="$(if $(filter command line environment override,$(origin COVER_INTERIOR)),$(COVER_INTERIOR),)"; \
	output="$(if $(filter command line environment override,$(origin COVER_OUTPUT)),$(COVER_OUTPUT),)"; \
	bin/kdp-cover "$${interior:-$$basename.pdf}" "$(COVER_PAPER)" "$${output:-$$basename-cover.pdf}" "$(COVER_BUILD)/$$basename/$(COVER_STYLE)" "$(COVER_STYLE)" "$(if $(COVER_VOLUME),$(COVER_VOLUME),$${title})"

$(EBOOK_TARGETS):
	$(MAKE) -C ebook "$(@:%-ebook=%)"

pdf: build-pdf

ci: build-pdf

again:
	@if [ -f $(PDF) ]; then mv $(PDF) mister.pdf; fi
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
	@$(MAKE) BUILD="$(BUILD)/parallel" TRANSLATION="$(TRANSLATION)" build-translation
	WTN_BUILD_DIR="$(BUILD)/parallel" WTN_OUTPUT_MODE="$(OUTPUT_MODE)" WTN_THEME="$(THEME)" WTN_VERSE_LAYOUT="$(VERSE_LAYOUT)" WTN_COMMENTARY="$(COMMENTARY)" WTN_TRANSLATION="$(TRANSLATION)" WTN_TRANSLATION_LUA="$(BUILD)/parallel/translation-$(TRANSLATION).lua" WTN_TITLE_PAGE_STYLE="$(TITLE_PAGE_STYLE)" WTN_COLORS="$(COLORS)" WTN_APOCRYPHA="$(APOCRYPHA)" WTN_REDACTOR="$(REDACTOR)" WTN_COVER="$(COVER)" bin/parallel-build
	$(call publish-and-open,$(BUILD)/parallel/$(PDF))

$(SUBSET_TARGETS): BUILD = build/$@
$(SUBSET_TARGETS):
	$(MAKE) BUILD="$(BUILD)" TRANSLATION="$(TRANSLATION)" build-translation
	@set -e; \
	basename="$$(bin/book-subset --output-name "$@")"; \
	bin/book-subset --build-dir "$(BUILD)" "$@"; \
	$(LATEX) $(LATEXFLAGS) "$(LATEX_CONFIG)\input{$(BUILD)/$$basename.tex}"
	$(MAKE) clean-stray-aux
	@basename="$$(bin/book-subset --output-name "$@")"; \
	cp "$(BUILD)/$$basename.pdf" "$$basename.pdf"

$(CHAPTER_TARGETS): BUILD = build/test
$(CHAPTER_TARGETS):
	@$(MAKE) BUILD="build/test" TRANSLATION="$(TRANSLATION)" build-translation
	@set -e; \
	basename="$$(bin/book-subset --output-name "$@")"; \
	bin/book-subset --build-dir "build/test" "$@"; \
	$(LATEX) $(LATEXFLAGS) -jobname="test-$@" "$(LATEX_CONFIG)\input{build/test/$$basename.tex}"
	@$(MAKE) clean-stray-aux
	@cp "build/test/test-$@.pdf" "test-$@.pdf"
	@if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "test-$@.pdf" >/dev/null 2>&1 & \
	else \
		echo "Built test-$@.pdf"; \
	fi
