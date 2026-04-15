#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but not found."
  exit 1
fi

if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

source ".venv/bin/activate"

PIP_FLAGS=(--trusted-host pypi.org --trusted-host files.pythonhosted.org)
if ! python -m pip install "${PIP_FLAGS[@]}" -r requirements.txt; then
  echo "Dependency install failed. Retrying with explicit index URL..."
  python -m pip install "${PIP_FLAGS[@]}" --index-url https://pypi.org/simple -r requirements.txt
fi

echo "Starting AI Exam Timetable Generator at http://127.0.0.1:8000"
python app.py
