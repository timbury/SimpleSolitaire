#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/.venv/bin/python}"

if [ ! -x "$PYTHON_BIN" ]; then
  printf "Python executable not found at %s\n" "$PYTHON_BIN" >&2
  printf "Create a virtual environment first or set PYTHON_BIN.\n" >&2
  exit 1
fi

"$PYTHON_BIN" -m pip install -r "$ROOT_DIR/requirements-build.txt"
rm -rf "$ROOT_DIR/build" "$ROOT_DIR/dist" "$ROOT_DIR/SimpleSolitaire.spec"

"$PYTHON_BIN" -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "SimpleSolitaire" \
  --specpath "$ROOT_DIR" \
  --distpath "$ROOT_DIR/dist" \
  --workpath "$ROOT_DIR/build" \
  --paths "$ROOT_DIR" \
  --add-data "$ROOT_DIR/assets:assets" \
  "$ROOT_DIR/main.py"

printf "\nBuild complete.\n"
printf "macOS app bundle: %s\n" "$ROOT_DIR/dist/SimpleSolitaire.app"
printf "Binary folder: %s\n" "$ROOT_DIR/dist/SimpleSolitaire"
