#!/usr/bin/env bash
# Starts the UOC Research Console: the FastAPI backend (reads the
# compiler's real registries live from the repo root) on :8000, and the
# Vite dev server (proxies /api to the backend) on :5173, then opens
# your browser. Ctrl+C stops both.
#
# Usage:  bash scripts/run_console.sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
  echo "No .venv found -- run 'bash scripts/mac_setup.sh' first."
  exit 1
fi
if [ ! -d "console/web/node_modules" ]; then
  echo "console/web/node_modules not found -- run 'bash scripts/mac_setup.sh' first."
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

BACKEND_PID=""
FRONTEND_PID=""
cleanup() {
  echo
  echo "Stopping console ..."
  [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null || true
  [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null || true
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Starting backend (FastAPI, http://127.0.0.1:8000) ..."
python3 -m uvicorn console.api.main:app --port 8000 &
BACKEND_PID=$!

echo "Starting frontend (Vite dev server, http://127.0.0.1:5173) ..."
(cd console/web && npm run dev -- --port 5173) &
FRONTEND_PID=$!

sleep 2
if command -v open >/dev/null 2>&1; then
  open "http://127.0.0.1:5173" || true
fi

echo
echo "== UOC Research Console running =="
echo "  Web UI:      http://127.0.0.1:5173"
echo "  API:         http://127.0.0.1:8000/api"
echo "  API docs:    http://127.0.0.1:8000/docs"
echo "Press Ctrl+C to stop."
wait
