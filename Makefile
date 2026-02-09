.PHONY: setup run build clean lint lint-fix package smoke

.DEFAULT_GOAL := check

setup:
	uv venv
	uv sync --extra dev

run:
	uv run python src/garmincli/__main__.py

lint:
	uv run ruff check src/
	uv run ruff format --check src/

lint-fix:
	uv run ruff check --fix src/
	uv run ruff format src/

test:
	uv run pytest

check: lint test

build:
	uv run pyinstaller \
		--onefile \
		--name gc \
		--target-arch arm64 \
		--add-data "src/garmincli/commands:garmincli/commands" \
		--collect-all garminconnect \
		--hidden-import garth \
		src/garmincli/__main__.py

package: build
	@set -e; 
	VERSION=$$(grep '^version' pyproject.toml | head -1 | cut -d'"' -f2); 
	echo "Packaging gc v$$VERSION..."; 
	cd dist && 
	tar -czf "garmin-cli-$$VERSION-macos.tar.gz" gc && 
	shasum -a 256 "garmin-cli-$$VERSION-macos.tar.gz"

smoke: build
	@set -e; \
	tmp_home="$$(mktemp -d)"; \
	trap 'rm -rf "$$tmp_home"' EXIT; \
	env -i PATH="/usr/bin:/bin:/usr/sbin:/sbin" HOME="$$tmp_home" \
		PYTHONNOUSERSITE=1 PYTHONPATH= PYTHONHOME= \
		VIRTUAL_ENV= CONDA_PREFIX= CONDA_DEFAULT_ENV= PIPENV_ACTIVE= \
		PYENV_VERSION= UV_PROJECT_ENV= \
		./dist/gc --help

clean:
	rm -rf dist build __pycache__ src/garmincli/__pycache__
