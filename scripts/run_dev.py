#!/usr/bin/env python3
"""Development launcher for UNIVO-SVIS."""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if __name__ == "__main__":
    sys.exit(
        subprocess.call(
            [sys.executable, "-m", "univo_svis.main"],
            cwd=str(PROJECT_ROOT),
            env={**__import__("os").environ, "PYTHONPATH": str(PROJECT_ROOT / "src")},
        )
    )
