#!/usr/bin/env bash
# Runs the full Python test suite (compiler/, seit_lang/, scientific_corpus/,
# console/api/ -- everything pytest discovers from the repo root).
#
# Usage:  bash scripts/run_tests.sh [pytest args...]
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
  echo "No .venv found -- run 'bash scripts/mac_setup.sh' first."
  exit 1
fi
# shellcheck disable=SC1091
source .venv/bin/activate

python3 -m pytest -q "$@"
