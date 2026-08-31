PKG = yhwh

install:
	pip install dist/*.tar.gz

develop:
	pip install -e '.[plots,dev]'

check:
	pytest -v tests

build: build-deps
	python -m build

uninstall:
	pip uninstall $(PKG)

clean:
	rm -rvf dist/ build/ src/*.egg-info

build-deps:
	@python -c 'import build' &>/dev/null || pip install build
