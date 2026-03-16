#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/.build-venv"
CACHE_DIR="$ROOT_DIR/.build-cache"

cd "$ROOT_DIR"
mkdir -p "$CACHE_DIR/pip" "$CACHE_DIR/pyinstaller"
python3 -m venv "$VENV_DIR"
PIP_CACHE_DIR="$CACHE_DIR/pip" "$VENV_DIR/bin/pip" install --upgrade pip -r requirements-build.txt
PYINSTALLER_CONFIG_DIR="$CACHE_DIR/pyinstaller" "$VENV_DIR/bin/pyinstaller" --clean passwordchecker.spec

echo
echo "Build complete: $ROOT_DIR/dist/passwordchecker"
