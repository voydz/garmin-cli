.PHONY: setup run build clean lint lint-fix package smoke print-tarball print-version

.DEFAULT_GOAL := check

UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)

ifeq ($(UNAME_S),Darwin)
PLATFORM := macos
ARCH := $(UNAME_M)
SHA256SUM := shasum -a 256
# --target-arch is Mach-O only; PyInstaller rejects it on other platforms.
TARGET_ARCH_FLAG := --target-arch $(ARCH)
else
PLATFORM := linux
ARCH := $(UNAME_M)
SHA256SUM := sha256sum
TARGET_ARCH_FLAG :=
endif

VERSION := $(shell grep '^version' pyproject.toml | head -1 | cut -d'"' -f2)
TARBALL := garmin-cli-$(VERSION)-$(PLATFORM)-$(ARCH).tar.gz

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
		$(TARGET_ARCH_FLAG) \
		--add-data "src/garmincli/commands:garmincli/commands" \
		--collect-all garminconnect \
		--collect-submodules fit_tool.profile.messages \
		--copy-metadata fit-tool \
		--copy-metadata bitstruct \
		--add-data "THIRD_PARTY_NOTICES.md:." \
		--hidden-import garth \
		src/garmincli/__main__.py

package: build
	@set -e; \
	echo "Packaging gc v$(VERSION) for $(PLATFORM)-$(ARCH)..."; \
	cp THIRD_PARTY_NOTICES.md dist/ && \
	cd dist && \
	tar -czf "$(TARBALL)" gc THIRD_PARTY_NOTICES.md && \
	$(SHA256SUM) "$(TARBALL)"

print-tarball:
	@echo "$(TARBALL)"

print-version:
	@echo "$(VERSION)"

smoke: build
	@set -e; \
	tmp_home="$$(mktemp -d)"; \
	trap 'rm -rf "$$tmp_home"' EXIT; \
	env -i PATH="/usr/bin:/bin:/usr/sbin:/sbin" HOME="$$tmp_home" \
		PYTHONNOUSERSITE=1 PYTHONPATH= PYTHONHOME= \
		VIRTUAL_ENV= CONDA_PREFIX= CONDA_DEFAULT_ENV= PIPENV_ACTIVE= \
		PYENV_VERSION= UV_PROJECT_ENV= \
		./dist/gc --help
	GC_BINARY="$(CURDIR)/dist/gc" uv run pytest tests/test_packaged_fit.py -q

clean:
	rm -rf dist build __pycache__ src/garmincli/__pycache__
