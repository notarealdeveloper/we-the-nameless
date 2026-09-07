INTERIOR ?= 01-genesis.pdf
OUTPUT ?= 01-genesis-cover.pdf
PAPER ?= standard-color
VOLUME ?= Genesis
BUILD ?= build/cover/fancy

.PHONY: all
all:
	$(MAKE) -C ../.. cover COVER_INTERIOR="$(INTERIOR)" COVER_OUTPUT="$(OUTPUT)" COVER_PAPER="$(PAPER)" COVER_VOLUME="$(VOLUME)" COVER_BUILD="$(BUILD)" COVER_STYLE=fancy
