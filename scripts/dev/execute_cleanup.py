#!/usr/bin/env python3
"""
Compatibility wrapper for executing repository cleanup.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.dev.cleanup_temp_files import main as cleanup_main


def main() -> int:
    argv = list(sys.argv[1:])
    if "--execute" not in argv:
        argv.insert(0, "--execute")
    return cleanup_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
