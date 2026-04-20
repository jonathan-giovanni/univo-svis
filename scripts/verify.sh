#!/bin/zsh
# UNIVO-SVIS Comprehensive Quality Gate

set -e # Exit on first error

PROJECT_ROOT=$(dirname "$0")/..
VENV_BIN="$PROJECT_ROOT/.venv/bin"

echo "=================================================="
echo "  UNIVO-SVIS Hardened Quality Gate"
echo "=================================================="

echo "[1/6] Compiling source..."
"$VENV_BIN/python" -m compileall "$PROJECT_ROOT/src" > /dev/null

echo "[2/6] Running Ruff linting..."
"$VENV_BIN/ruff" check "$PROJECT_ROOT/src" "$PROJECT_ROOT/tests"

echo "[3/6] Checking Black formatting..."
"$VENV_BIN/black" --check "$PROJECT_ROOT/src" "$PROJECT_ROOT/tests"

echo "[4/6] Running Pytest unit tests..."
"$VENV_BIN/pytest" -q

echo "[5/6] Running Smoke Test..."
"$VENV_BIN/python" "$PROJECT_ROOT/scripts/smoke_test.py" > /dev/null

echo "[6/6] Verifying Robust GUI Startup..."
export PYTHONPATH="$PROJECT_ROOT/src"
# Use offscreen platform for headless environments and our auto-close flag
QT_QPA_PLATFORM=offscreen UNIVO_SVIS_VERIFY_STARTUP=1 "$VENV_BIN/python" -m univo_svis.main

echo "=================================================="
echo "  ✓ QUALITY GATE PASSED"
echo "=================================================="
