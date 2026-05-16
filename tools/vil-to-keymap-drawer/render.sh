#!/bin/sh
# Render imgs/corne-layout.svg from corne.vil.
# Requires keymap-drawer (PyPI: `pipx install keymap-drawer`) — needs Python 3.12+.
set -e
cd "$(dirname "$0")"

REPO_ROOT="$(cd ../.. && pwd)"
VIL="$REPO_ROOT/corne.vil"
YAML="corne.yaml"
SVG="$REPO_ROOT/imgs/corne-layout.svg"

PYTHON="${PYTHON:-python3}"
KEYMAP="${KEYMAP:-keymap}"

mkdir -p "$REPO_ROOT/imgs"
"$PYTHON" vil2yaml.py "$VIL" -o "$YAML"
"$KEYMAP" draw "$YAML" > "$SVG"
echo "wrote $SVG"
