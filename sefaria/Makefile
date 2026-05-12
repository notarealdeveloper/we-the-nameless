.PHONY: all install develop dev check test lint format fmt build clean demo

all: check

install:
	python -m pip install .

develop dev:
	python -m pip install -e '.[dev]'

check: test lint

test:
	python -m pytest -q

lint:
	python -m ruff check src tests

format fmt:
	python -m ruff format src tests
	python -m ruff check --fix src tests

build:
	python -m build

clean:
	rm -rf .pytest_cache .ruff_cache dist build *.egg-info src/*.egg-info src/*/*.egg-info

demo:
	sefaria hebrew 'Genesis 1:1'
	sefaria text 'Genesis 1:1' --lang en
	sefaria versions Genesis --lang en
