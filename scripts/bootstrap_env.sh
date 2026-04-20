#!/usr/bin/env bash
# Bootstrap development environment for UNIVO-SVIS
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== UNIVO-SVIS Environment Bootstrap ==="
echo "Project root: $PROJECT_ROOT"

# Create virtual environment
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "[1/3] Creating virtual environment..."
    python3.12 -m venv "$PROJECT_ROOT/.venv"
else
    echo "[1/3] Virtual environment already exists"
fi

# Install dependencies
echo "[2/3] Installing dependencies..."
"$PROJECT_ROOT/.venv/bin/pip" install -r "$PROJECT_ROOT/requirements.txt" --quiet

# Run smoke test
echo "[3/3] Running smoke test..."
"$PROJECT_ROOT/.venv/bin/python" "$PROJECT_ROOT/scripts/smoke_test.py"

echo ""
echo "=== Bootstrap complete ==="
echo "Activate: source $PROJECT_ROOT/.venv/bin/activate"
echo "Run app:  python -m univo_svis.main"
echo "Run tests: pytest tests/ -v"
