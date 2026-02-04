#!/bin/bash
set -e

VERSION=$(grep '^version' pyproject.toml | head -1 | cut -d'"' -f2)
echo "Building gc v${VERSION}..."

uv sync --extra dev

uv run pyinstaller \
    --onefile \
    --name gc \
    --target-arch arm64 \
    --add-data "src/garmincli/commands:garmincli/commands" \
    --collect-all garminconnect \
    --hidden-import garth \
    src/garmincli/__main__.py

cd dist
tar -czf "gc-${VERSION}-macos-arm64.tar.gz" gc
shasum -a 256 "gc-${VERSION}-macos-arm64.tar.gz"

echo "Build complete: dist/gc-${VERSION}-macos-arm64.tar.gz"
