PROJECT_ROOT := $(abspath ../../..)

INTERIOR ?= $(PROJECT_ROOT)/pub/01-genesis/01-genesis-kdp.pdf
OUTPUT ?= $(PROJECT_ROOT)/pub/01-genesis/01-genesis-cover-simple.pdf
PAPER ?= standard-color
VOLUME ?= Genesis
BUILD ?= $(PROJECT_ROOT)/build/cover/simple

.PHONY: all
all:
	@if [ ! -f "$(INTERIOR)" ]; then \
		printf 'Interior PDF not found: %s\nBuild or provide it with INTERIOR=/path/to/interior.pdf, then run make again.\n' "$(INTERIOR)" >&2; \
		exit 1; \
	fi
	$(MAKE) -C "$(PROJECT_ROOT)" cover COVER_INTERIOR="$(INTERIOR)" COVER_OUTPUT="$(OUTPUT)" COVER_PAPER="$(PAPER)" COVER_VOLUME="$(VOLUME)" COVER_BUILD="$(BUILD)" COVER_STYLE=simple
