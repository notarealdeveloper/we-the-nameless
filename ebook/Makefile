.DEFAULT_GOAL := all
SUBSETS := $(shell ../bin/book-subset --make-targets) $(shell ../bin/book-subset --make-chapter-targets)
COVER ?= we-cover-8
RELEASE ?=

.PHONY: all release validate test clean $(SUBSETS) $(addprefix validate-,$(SUBSETS))

# Always rebuild on request: source selection and cover options are inputs too.
all:
	./build.py --cover "$(COVER)" $(RELEASE)

release:
	$(MAKE) all RELEASE=--require-epubcheck

$(SUBSETS):
	./build.py --subset "$@" --cover "$(COVER)" $(RELEASE)

# Checking an existing file never builds it. A missing checker is a release error.
validate:
	./validate.py we-the-nameless.epub
	epubcheck we-the-nameless.epub

$(addprefix validate-,$(SUBSETS)): validate-%:
	@set -e; output="$$(python3 -c 'import build; print(build.subset_edition("$*")[1] + ".epub")')"; \
	./validate.py "$$output"; \
	epubcheck "$$output"

test:
	python3 -m unittest -v test_build.py

clean:
	rm -f *.epub manuscript.generated.md
