from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.symphony.service import SymphonyService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Symphony orchestration service.")
    parser.add_argument("workflow_path", nargs="?", default="WORKFLOW.md", help="Path to WORKFLOW.md")
    parser.add_argument("--port", type=int, default=None, help="Optional status API port")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    workflow_path = Path(args.workflow_path)
    service = SymphonyService(workflow_path=workflow_path, port=args.port)
    service.run_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
