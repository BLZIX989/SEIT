#!/usr/bin/env bash
# One-time local setup for the Forward-MDCL compiler + UOC Research Console
# on macOS (Apple Silicon or Intel). Safe to re-run.
#
# What this does:
#   1. Checks for python3 (3.11+) and node (20+) -- tells you what to
#      install via Homebrew if either is missing, then stops (never
#      installs system packages on your behalf).
#   2. Creates a Python virtual environment at .venv/ and installs the
#      compiler's + console's Python dependencies into it.
#   3. Runs `npm install` inside console/web -- this is REQUIRED even if
#      you received a copy of this repo with console/web/node_modules
#      already present: Vite 8's bundler (Rolldown) and lightningcss both
#      ship platform-specific native binaries, and any node_modules built
#      elsewhere (e.g. Linux) will NOT run on macOS. `npm install` fetches
#      the correct darwin-arm64/x64 binaries for your machine.
#
# Usage:  bash scripts/mac_setup.sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "== Forward-MDCL / UOC Research Console: macOS setup =="
echo "Repository root: $ROOT_DIR"
echo

# ---- 1. Prerequisite checks ----
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Install it first, e.g.:"
  echo "  brew install python@3.12"
  exit 1
fi
PY_VERSION="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
PY_MAJOR="$(python3 -c 'import sys; print(sys.version_info[0])')"
PY_MINOR="$(python3 -c 'import sys; print(sys.version_info[1])')"
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 11 ]; }; then
  echo "python3 $PY_VERSION found, but 3.11+ is required. Install a newer one, e.g.:"
  echo "  brew install python@3.12"
  exit 1
fi
echo "[OK] python3 $PY_VERSION"

if ! command -v node >/dev/null 2>&1; then
  echo "node not found. Install it first, e.g.:"
  echo "  brew install node"
  exit 1
fi
NODE_MAJOR="$(node -e 'console.log(process.versions.node.split(".")[0])')"
if [ "$NODE_MAJOR" -lt 20 ]; then
  echo "node v$(node -v) found, but v20+ is required. Install a newer one, e.g.:"
  echo "  brew install node"
  exit 1
fi
echo "[OK] node $(node -v)"

if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found (should ship with node). Reinstall node via Homebrew."
  exit 1
fi
echo "[OK] npm $(npm -v)"
echo

# ---- 2. Python virtual environment ----
if [ ! -d ".venv" ]; then
  echo "Creating Python virtual environment at .venv ..."
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "Installing Python dependencies (compiler + console) into .venv ..."
pip install --upgrade pip >/dev/null
pip install -r compiler/requirements.txt -r console/requirements.txt
echo "[OK] Python dependencies installed"
echo

# ---- 3. Frontend dependencies (native binaries for THIS machine) ----
echo "Installing frontend dependencies (console/web) -- this fetches macOS-native"
echo "binaries for Vite/Rolldown and lightningcss, required even if node_modules"
echo "already exists from another machine ..."
(cd console/web && npm install)
echo "[OK] Frontend dependencies installed"
echo

echo "== Setup complete =="
echo "Next: run 'bash scripts/run_console.sh' to start the console, or open this"
echo "folder in VS Code and use the 'SEIT: Run Console' task (Cmd+Shift+P ->"
echo "'Tasks: Run Task')."
