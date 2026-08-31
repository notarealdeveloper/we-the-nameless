PKG = yhwh
DATA = $(abspath ../..)
TEX = $(wildcard $(DATA)/[01][0-9]-*/*.tex)

build: build-deps
	python -m build

install:
	pip install dist/*.tar.gz

develop:
	pip install -e .

check:
	PYTHONPATH=src pytest -v tests
	PYTHONPATH=src python -m yhwh.cli --data '$(DATA)' grep 'dream' -l english >/dev/null
	PYTHONPATH=src python -m yhwh.cli --data '$(DATA)' grep 'באש' -l hebrew >/dev/null

uninstall:
	pip uninstall $(PKG)

clean:
	rm -rvf dist/ build/ .pytest_cache/ src/*.egg-info

dataset: $(TEX)
	PYTHONPATH=src python -m yhwh.cli --data '$(DATA)' dataset data/primary-history.jsonl.gz

cache-clean:
	PYTHONPATH=src python -c 'import yhwh; yhwh.clean_cache()'

build-deps:
	@python -c 'import build' &>/dev/null || pip install build

test: check
