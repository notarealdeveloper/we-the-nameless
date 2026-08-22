name     := $(shell basename $(PWD))
python   := python
pip      := $(python) -m pip
pytest   := $(python) -m pytest

build: build-deps
	$(python) -m build --no-isolation

install:
	$(pip) install dist/*.tar.gz

develop:
	$(pip) install -e .

check:
	PYTHONPATH=src $(pytest) -v tests

clean:
	rm -rvf dist/ build/ src/*.egg-info .pytest_cache

build-deps:
	@$(python) -c 'import build' &>/dev/null || $(pip) install build
