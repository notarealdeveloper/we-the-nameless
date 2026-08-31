PYTHON ?= python
CORPUS ?= primary-history
DATASET ?= dataset

.PHONY: help install dev test test-full lint typecheck dataset validate dist release clean clean-cache

help:
	@printf '%s\n' \
	  'make install      Install editable package' \
	  'make dev          Install development and plotting extras' \
	  'make test         Run unit tests' \
	  'make test-full    Run tests and parse/validate CORPUS' \
	  'make dataset      Build portable dataset from CORPUS' \
	  'make validate     Validate source-span integrity' \
	  'make dist         Build wheel and sdist' \
	  'make release      Build deterministic repository archives' \
	  'make clean-cache  Remove ~/.cache/yhwh'

install:
	$(PYTHON) -m pip install .

develop:
	$(PYTHON) -m pip install -e '.[all]'

check:
	$(PYTHON) -m pytest -v

check-full: test
	$(PYTHON) -m yhwh --corpus '$(CORPUS)' info
	$(PYTHON) -m yhwh --corpus '$(CORPUS)' validate

lint:
	$(PYTHON) -m ruff check src tests

typecheck:
	$(PYTHON) -m mypy src/yhwh

dataset:
	PYTHONPATH=src $(PYTHON) -m yhwh --corpus '$(CORPUS)' build '$(DATASET)'

validate:
	PYTHONPATH=src $(PYTHON) -m yhwh --corpus '$(CORPUS)' validate

dist:
	$(PYTHON) -m build

release:
	$(PYTHON) scripts/make_release.py --root . --output dist

clean:
	rm -rf build dist .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

clean-cache:
	PYTHONPATH=src $(PYTHON) -m yhwh cache clean
