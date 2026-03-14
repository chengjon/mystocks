from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.runtime.maestro_collab import main as _delegate


def main(argv: list[str] | None = None) -> int:
    return _delegate(argv)


if __name__ == "__main__":
    raise SystemExit(main())
