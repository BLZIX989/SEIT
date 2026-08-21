#!/usr/bin/env bash
# Runs the real compiler end-to-end (python3 -m compiler.run_compiler):
# rebuilds every canonical registry (object/transformation/equation/
# chainlink/protocol/...), the self-audit report, and the Master
# Calculation Workbook, from the current source -- exactly what the
# console's "Run" button (POST /api/runs) invokes under the hood.
#
# Usage:  bash scripts/run_compiler.sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
  echo "No .venv found -- run 'bash scripts/mac_setup.sh' first."
  exit 1
fi
# shellcheck disable=SC1091
source .venv/bin/activate

python3 -m compiler.run_compiler
