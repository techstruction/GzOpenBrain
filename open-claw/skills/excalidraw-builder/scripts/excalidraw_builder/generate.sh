#!/bin/bash
# excalidraw-generator wrapper script
# Usage: ./generate.sh <input_json> <output_path>

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
VENV_PATH="$DIR/../../.venv"

# Ensure virtual environment is activated, fallback to system python
if [ -d "$VENV_PATH" ]; then
    "$VENV_PATH/bin/python3" "$DIR/excalidraw_generator.py" "$1" "$2"
else
    # Fallback to system python (e.g., in Docker)
    python3 "$DIR/excalidraw_generator.py" "$1" "$2"
fi
