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
COVER_STYLE ?= $(call read-config,ConfigCoverStyle)
SPINE ?= $(call read-config,ConfigSpine)
BUILD ?= build/$(OUTPUT_MODE)-$(THEME)
CACHE = $(BUILD)/texmf-var
TRANSLATION_LUA = $(BUILD)/translation-$(TRANSLATION).lua
LATEX_CONFIG = \def\ConfigOutputMode{$(OUTPUT_MODE)}\def\ConfigTheme{$(THEME)}\def\ConfigVerseLayout{$(VERSE_LAYOUT)}\def\ConfigCommentary{$(COMMENTARY)}\def\ConfigEnglishTranslation{$(TRANSLATION)}\def\IndividualBookTitlePageStyle{$(TITLE_PAGE_STYLE)}\def\ConfigColors{$(COLORS)}\def\ConfigApocrypha{$(APOCRYPHA)}\def\ConfigRedactor{$(REDACTOR)}\def\ConfigCover{$(COVER)}\def\ConfigCoverStyle{$(COVER_STYLE)}\def\ConfigSpine{$(SPINE)}\def\ConfigEnglishTranslationLuaFile{$(TRANSLATION_LUA)}
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
EBOOK_SUBSETS := $(SUBSET_TARGETS) $(CHAPTER_TARGETS)
EBOOK_TARGETS := $(foreach suffix,ebook ebook-release ebook-check,$(addsuffix -$(suffix),$(EBOOK_SUBSETS)))
EBOOK_COVER ?= we-cover-8
PRINT_SUBSETS := $(SUBSET_TARGETS) $(CHAPTER_TARGETS)
PRINT_SUFFIXES := $(shell python3 bin/print_publish_config.py)
PRINT_TARGETS := $(foreach suffix,$(PRINT_SUFFIXES),$(addsuffix -$(suffix),$(PRINT_SUBSETS)))
COVER_TARGETS := $(addsuffix -cover,$(SUBSET_TARGETS))
COVER_INTERIOR ?= 01-genesis.pdf
COVER_PAPER ?= standard-color
KDP_PAPER ?= premium-color
KDP_INK ?= premium-color
KDP_BLEED ?= no-bleed
KDP_TRIM ?= default
KDP_COVER_STYLE ?=
KDP_SPINE ?= ld
PRINT_PROCESSING ?=
PRINT_BINDING ?=
PRINT_OUTPUT_DIR ?=
PRINT_PLAN ?=
KDP_HARDCOVER_TEMPLATE ?=
KDP_ARTIFACT ?=
KDP_REFERENCE ?=
# Neutral names apply equally to both publishers; KDP_* remain fallback aliases.
PRINT_PAPER ?= $(KDP_PAPER)
PRINT_INK ?= $(if $(filter command line environment override,$(origin KDP_INK)),$(KDP_INK),$(PRINT_PAPER))
PRINT_BLEED ?= $(KDP_BLEED)
PRINT_TRIM ?= $(KDP_TRIM)
PRINT_COVER_STYLE ?= $(KDP_COVER_STYLE)
PRINT_SPINE ?= $(KDP_SPINE)
PRINT_HARDCOVER_TEMPLATE ?= $(KDP_HARDCOVER_TEMPLATE)
PRINT_OPTIONS = --paper "$(PRINT_PAPER)" --ink "$(PRINT_INK)" --bleed "$(PRINT_BLEED)" --trim "$(PRINT_TRIM)" $(if $(PRINT_COVER_STYLE),--cover-style "$(PRINT_COVER_STYLE)") --spine "$(PRINT_SPINE)" $(if $(PRINT_HARDCOVER_TEMPLATE),--hardcover-template "$(PRINT_HARDCOVER_TEMPLATE)") $(if $(PRINT_PROCESSING),--processing "$(PRINT_PROCESSING)") $(if $(PRINT_BINDING),--binding "$(PRINT_BINDING)") $(if $(PRINT_OUTPUT_DIR),--output-dir "$(PRINT_OUTPUT_DIR)") $(if $(filter 1 true,$(PRINT_PLAN)),--plan)
# Only deliberate display overrides change the stable print presets.
print-override = $(if $(filter command line environment override,$(origin $(1))),--$(2) "$($(1))")
PRINT_OPTIONS += $(call print-override,OUTPUT_MODE,output-mode) $(call print-override,THEME,theme) $(call print-override,VERSE_LAYOUT,verse-layout) $(call print-override,COMMENTARY,commentary) $(call print-override,TRANSLATION,translation) $(call print-override,TITLE_PAGE_STYLE,title-page-style) $(call print-override,COLORS,colors) $(call print-override,APOCRYPHA,apocrypha) $(call print-override,REDACTOR,redactor) $(call print-override,COVER,cover)
KDP_CHECK_OPTIONS = $(if $(KDP_ARTIFACT),--artifact "$(KDP_ARTIFACT)") $(if $(KDP_REFERENCE),--reference "$(KDP_REFERENCE)")
COVER_VOLUME ?=
COVER_OUTPUT ?= 01-genesis-cover.pdf
COVER_BUILD ?= build/cover
KDP_INPUT ?=
KDP_OUTPUT ?=

export TEXMFVAR = $(CACHE)
# Keep every aux-file marker on its own line without splitting any of the
# Pentateuch paths themselves.
export max_print_line = 60

.PHONY: all pdf build-pdf ci view open clean distclean debug progress parallel all-modes ebook ebook-release ebook-check ebook-validate check-ebook cover kdp kdp-preflight genesis-kdp check-genesis-kdp check-kdp-validator check-kdp check-build $(PRINT_TARGETS) $(COVER_TARGETS) $(EBOOK_TARGETS) $(BUILD_MODES) build-prepare build-translation clean-stray-aux draft c x comment halfcomment uncomment again help list $(SUBSET_TARGETS) $(CHAPTER_TARGETS) $(COMMENT_BOOK_TARGETS) $(UNCOMMENT_BOOK_TARGETS)

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
		'Build the complete book:' \
		'  make                                                   Build and open master.pdf (tech-dark) or mistress.pdf (book-lite).' \
		'  make pdf                                               Build master.pdf without opening it.' \
		'  make parallel                                          Build the book with the parallel chapter workflow.' \
		'  make book-lite                                         Build build/book-lite/master.pdf (also: book-dark, tech-lite, tech-dark).' \
		'  make all-modes                                         Build all four mode/theme combinations concurrently.' \
		'' \
		'Configure a build:' \
		'  make OUTPUT_MODE=tech THEME=lite pdf                   Build one explicit combination.' \
		'  make THEME=lite COLORS=lighter pdf                     Use the lighter lite-mode palette.' \
		'  make APOCRYPHA=canonical pdf                           Build without apocrypha (default: apocryphal).' \
		'  make VERSE_LAYOUT=vertical COMMENTARY=false pdf        Override verse layout and commentary.' \
		'  make TITLE_PAGE_STYLE=plain REDACTOR=censored pdf      Override title pages and redaction.' \
		'  make COVER=none pdf                                    Build without the configured cover image.' \
		'  make TRANSLATION=kjv pdf                               Build with translations/kjv instead of inline English.' \
		'' \
		'Build books, chapters, and source subsets:' \
		'  All subset builds open their PDF when finished.' \
		'  make list                                              List dynamic subset builds.' \
		'  make genesis                                           Build 01-genesis.pdf; numbered aliases include 1-genesis and 01-genesis.' \
		'  make samuel                                            Build 08-samuel.pdf; use 1-samuel or 2-samuel for individual books.' \
		'  make kings                                             Build 09-kings.pdf; use 1-kings or 2-kings for individual books.' \
		'  make genesis-1                                         Build Genesis 1 as test-genesis-1.pdf and open it.' \
		'  make 1-samuel-1                                        Build 1 Samuel 1; chapter targets share build/test/.' \
		'  make J                                                 Build J.pdf: Yahwist text, including records/poems used by J.' \
		'  make E                                                 Build E.pdf: Elohist text only.' \
		'  make I                                                 Build I.pdf: J + E + RJE text.' \
		'  make P                                                 Build P.pdf: Priestly text only.' \
		'  make D                                                 Build D.pdf: Deuteronomy through 2 Kings.' \
		'  make R                                                 Build R.pdf: Genesis through Nehemiah.' \
		'  make j                                                 Build j.pdf: Torah-only J text.' \
		'  make e                                                 Build e.pdf: Torah-only E text.' \
		'  make i                                                 Build i.pdf: Torah-only J + E + RJE text.' \
		'  make p                                                 Build p.pdf: Torah-only P text.' \
		'  make r                                                 Build r.pdf: full Torah with all sources.' \
		'  make M                                                 Build M.pdf: Mushite text, I plus Deuteronomistic history.' \
		'  make A                                                 Build A.pdf: Aaronid text, P plus selected D material and Ezra-Nehemiah.' \
		'  make court                                             Build court.pdf: 1 Samuel through 1 Kings 2.' \
		'' \
		'Publish ebooks:' \
		'  make ebook                                             Build ebook/we-the-nameless.epub.' \
		'  make genesis-ebook                                     Build ebook/genesis.epub; all print subset names also work (J, P, genesis-1).' \
		'  make genesis-ebook-release                             Build and validate for release; requires EPUBCheck.' \
		'  make genesis-ebook-check                               Check the existing EPUB with both validators; no build.' \
		'  make ebook-release / ebook-check                       Equivalent commands for the complete EPUB.' \
		'  Set EBOOK_COVER=we-cover-8|none|<image basename>. See PUBLISH.md for the command sequence.' \
		'' \
		'Prepare print PDFs (see PUBLISH.md for defaults and equivalent bin/ commands):' \
		'  make genesis-kdp                                       Simple 7x10 + fancy 8.25x11; vectorize interiors and covers.' \
		'  make genesis-lulu                                      Simple + fancy 7x10; keep searchable originals.' \
		'  make genesis-kdp-simplecover-original-8.25x11           Override artwork, processing, and trim independently.' \
		'  make J-lulu-fancycover-vectorized-7x10                   Any selection, publisher, style, processing, and supported trim.' \
		'  make exodus-lulu-hardcover                             Fancy hardcover 7x10; searchable originals.' \
		'  Only publisher presets and complete cover-processing-trim combinations have Make targets.' \
		'  Each also accepts -build, -vectorize, or -check for one publishing stage.' \
		'  bin/build genesis kdp --cover-style fancy               Partial combinations use the general CLI.' \
		'  bin/build genesis kdp --stage build|vectorize|check      Run one publishing stage.' \
		'  bin/build --help                                       All master.tex settings, publishers, PDF and EPUB options.' \
		'  Add PRINT_PLAN=1 to print resolved parameters and paths without building.' \
		'  make check-kdp                                         Synthetic KDP and Lulu tests; never builds a book.' \
		'  make check-build                                       CLI routing plus synthetic publishing tests; no book build.' \
		'  make check-kdp-validator                               Synthetic visual validator self-test.' \
		'  make cover / genesis-cover                             Standalone cover from an existing PDF.' \
		'  make kdp KDP_INPUT=file.pdf                             Legacy PDF conversion; separate from the print pipeline.' \
		'  make kdp-preflight KDP_INPUT=file.pdf                   Legacy searchable-font check.' \
		'' \
		'Edit the active selection:' \
		'  make progress                                          Open master.tex.' \
		'  make comment                                           Comment out everything except the progress subset.' \
		'  make halfcomment                                       Comment out everything except the broader half-comment subset.' \
		'  make uncomment                                         Uncomment book/include lines in master.tex.' \
		'  make comment-genesis                                   Comment only Genesis; book aliases work for every book.' \
		'  make uncomment-genesis                                 Uncomment only Genesis; leave every other book unchanged.' \
		'' \
		'Maintenance:' \
		'  make clean                                             Remove transient TeX aux files.' \
		'  make distclean                                         Remove build outputs and master.pdf.'

list:
	bin/book-subset --list

ebook:
	@bin/build all ebook --cover "$(EBOOK_COVER)" --apocrypha "$(APOCRYPHA)"

ebook-release:
	@bin/build all ebook --stage release --cover "$(EBOOK_COVER)" --apocrypha "$(APOCRYPHA)"

ebook-check ebook-validate:
	@bin/build all ebook --stage check

check-ebook:
	$(MAKE) -C ebook test

cover:
	@bin/print-cover "$(COVER_INTERIOR)" "$(COVER_PAPER)" "$(COVER_OUTPUT)" "$(COVER_BUILD)" "$(COVER_STYLE)" "$(COVER_VOLUME)" "$(SPINE)"

kdp:
	@test -n "$(KDP_INPUT)" || { echo 'KDP_INPUT is required' >&2; exit 2; }
	@bin/kdp-pdf "$(KDP_INPUT)" "$(if $(KDP_OUTPUT),$(KDP_OUTPUT),$(basename $(KDP_INPUT))-kdp.pdf)"

kdp-preflight:
	@test -n "$(KDP_INPUT)" || { echo 'KDP_INPUT is required' >&2; exit 2; }
	@bin/kdp-preflight "$(KDP_INPUT)"

# Target grammar and defaults live in one Python module, shared with the CLI.
# Enumerate valid targets for tab completion and mark them phony even if a file
# with that name exists. The CLI resolves qualifiers, not Make string slicing.
$(PRINT_TARGETS):
	@bin/build --make-target "$@" $(PRINT_OPTIONS) $(KDP_CHECK_OPTIONS)

check-genesis-kdp:
	@bin/build genesis kdp --stage check $(PRINT_OPTIONS) $(KDP_CHECK_OPTIONS)

check-kdp-validator:
	@python3 bin/print-visual-compare --self-test

check-build: check-kdp
	@python3 -m unittest discover -s tests -p 'test_build_cli.py' -v

check-kdp:
	@python3 -m unittest discover -s tests -p 'test_kdp*.py' -v
	@python3 -m unittest discover -s tests -p 'test_lulu.py' -v

$(COVER_TARGETS): %-cover:
	@set -e; \
	basename="$$(bin/book-subset --output-name "$*")"; \
	title="$$(printf '%s\n' "$${basename#??-}" | awk -F- '{ for (i=1; i<=NF; i++) { if ($$i ~ /^[a-z]/) $$i=toupper(substr($$i,1,1)) substr($$i,2); printf "%s%s", (i > 1 ? " " : ""), $$i } }')"; \
	interior="$(if $(filter command line environment override,$(origin COVER_INTERIOR)),$(COVER_INTERIOR),)"; \
	output="$(if $(filter command line environment override,$(origin COVER_OUTPUT)),$(COVER_OUTPUT),)"; \
	bin/print-cover "$${interior:-$$basename.pdf}" "$(COVER_PAPER)" "$${output:-$$basename-cover.pdf}" "$(COVER_BUILD)/$$basename/$(COVER_STYLE)" "$(COVER_STYLE)" "$(if $(COVER_VOLUME),$(COVER_VOLUME),$${title})" "$(SPINE)"

$(addsuffix -ebook,$(EBOOK_SUBSETS)): %-ebook:
	@bin/build "$*" ebook --cover "$(EBOOK_COVER)" --apocrypha "$(APOCRYPHA)"

$(addsuffix -ebook-release,$(EBOOK_SUBSETS)): %-ebook-release:
	@bin/build "$*" ebook --stage release --cover "$(EBOOK_COVER)" --apocrypha "$(APOCRYPHA)"

$(addsuffix -ebook-check,$(EBOOK_SUBSETS)): %-ebook-check:
	@bin/build "$*" ebook --stage check

pdf: build-pdf

ci: build-pdf

again:
	@if [ -f $(BUILD)/$(PDF) ]; then mv -v $(BUILD)/$(PDF) mister.pdf; fi
	$(MAKE) all

build-prepare:
	@mkdir -p "$(BUILD)" "$(CACHE)"
	@python3 bin/history_structure.py "$(MAIN).tex" "$(BUILD)"

build-translation: build-prepare
	@if [ "$(TRANSLATION)" != "default" ]; then \
		bin/book-translation-lua "$(TRANSLATION)" "$(TRANSLATION_LUA)"; \
	fi

build-pdf: $(BUILD)/$(PDF)
	cp "$(BUILD)/$(MAIN).pdf" .

$(BUILD)/$(PDF): $(TEX_SOURCES) bin/epistles.lua 10-dudetheyreontome
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
	@find . \( -path "./build" -o -path "./pub" \) -prune -o -type f \( \
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
		find build \( -path build/kdp -o -path build/lulu \) -prune -o -type f \( \
			-name '*.aux' -o \
			-name '*.log' -o \
			-name '*.toc' -o \
			-name '*.out' -o \
			-name '*.fls' -o \
			-name '*.fdb_latexmk' \
		\) -exec rm -f {} +; \
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
	python3 bin/latex-rerun.py "$(BUILD)/$$basename.log" $(LATEX) $(LATEXFLAGS) "$(LATEX_CONFIG)\input{$(BUILD)/$$basename.tex}"
	$(MAKE) clean-stray-aux
	@set -e; \
	basename="$$(bin/book-subset --output-name "$@")"; \
	cp "$(BUILD)/$$basename.pdf" "$$basename.pdf"; \
	if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$basename.pdf" >/dev/null 2>&1 & \
	else \
		echo "Built $$basename.pdf"; \
	fi

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
