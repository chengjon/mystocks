from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.symphony.config import DEFAULT_ACTIVE_STATES, DEFAULT_TERMINAL_STATES, TrackerConfig
from src.services.symphony.local_tracker import LocalIssueTrackerClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage the local SQLite Symphony tracker.")
    parser.add_argument(
        "--sqlite-path",
        default=".symphony/tracker.db",
        help="Path to the local tracker sqlite database.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create a new local issue")
    create_parser.add_argument("--title", required=True, help="Issue title")
    create_parser.add_argument("--description", default=None, help="Optional issue description")
    create_parser.add_argument("--state", default="Todo", help="Initial issue state")
    create_parser.add_argument("--priority", type=int, default=None, help="Optional issue priority")
    create_parser.add_argument("--labels", default="", help="Comma-separated labels")

    subparsers.add_parser("list", help="List local issues")

    update_parser = subparsers.add_parser("update-state", help="Update an issue state")
    update_parser.add_argument("identifier", help="Issue identifier, e.g. LOCAL-1")
    update_parser.add_argument("state", help="New issue state")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    tracker = _build_tracker_config(Path(args.sqlite_path))
    client = LocalIssueTrackerClient(tracker)

    try:
        if args.command == "create":
            issue = client.create_issue(
                title=args.title,
                description=args.description,
                state=args.state,
                priority=args.priority,
                labels=_split_labels(args.labels),
            )
            _print_issue(issue)
            return 0

        if args.command == "list":
            for issue in client.list_issues():
                _print_issue(issue)
            return 0

        if args.command == "update-state":
            issue = client.update_issue_state(args.identifier, args.state)
            _print_issue(issue)
            return 0
    finally:
        client.close()

    return 1


def _build_tracker_config(sqlite_path: Path) -> TrackerConfig:
    return TrackerConfig(
        kind="local",
        endpoint="",
        api_key="",
        project_slug="",
        active_states=[state.strip().lower() for state in DEFAULT_ACTIVE_STATES],
        terminal_states=[state.strip().lower() for state in DEFAULT_TERMINAL_STATES],
        sqlite_path=sqlite_path,
        active_state_names=list(DEFAULT_ACTIVE_STATES),
        terminal_state_names=list(DEFAULT_TERMINAL_STATES),
    )


def _split_labels(value: str) -> list[str]:
    return [label.strip() for label in value.split(",") if label.strip()]


def _print_issue(issue) -> None:
    print(f"{issue.identifier}\t{issue.state}\t{issue.title}")


if __name__ == "__main__":
    raise SystemExit(main())
