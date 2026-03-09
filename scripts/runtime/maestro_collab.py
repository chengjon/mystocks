from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.maestro.collab import (
    FileOwnershipIndex,
    OwnershipSuggestionEngine,
    SQLiteCollaborationRegistry,
    extract_task_path_hints,
    load_file_ownership,
)


@dataclass(frozen=True)
class _IssueRef:
    identifier: str
    id: str | None = None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Maestro collaboration state.")
    parser.add_argument("--sqlite-path", default=".symphony/tracker.db", help="Path to the local tracker sqlite DB.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    assign_parser = subparsers.add_parser("assign", help="Create or update issue assignment")
    assign_parser.add_argument("issue_identifier", help="Issue identifier, e.g. LOCAL-1 or MT-1")
    assign_parser.add_argument("--worker-cli", required=True, help="Assigned worker CLI name")
    assign_parser.add_argument("--assigned-by", default="main", help="Who made the assignment")
    assign_parser.add_argument("--acceptance-summary", default=None, help="Optional acceptance summary")
    assign_parser.add_argument("--status", default="assigned", help="Assignment status")

    state_parser = subparsers.add_parser("state", help="Show collaboration state for one issue")
    state_parser.add_argument("issue_identifier", help="Issue identifier")

    suggest_parser = subparsers.add_parser("suggest", help="Suggest a likely owner from task paths and ownership rules")
    suggest_parser.add_argument(
        "--ownership-path",
        default=".FILE_OWNERSHIP",
        help="Path to the repository ownership rules file.",
    )
    suggest_parser.add_argument(
        "--task-path",
        default=None,
        help="Optional TASK.md path used to derive path hints.",
    )
    suggest_parser.add_argument(
        "--path",
        dest="paths",
        action="append",
        default=[],
        help="Explicit candidate path. Can be provided multiple times.",
    )
    suggest_parser.add_argument(
        "--fallback-owner",
        default="main",
        help="Fallback owner when no explicit ownership rule matches.",
    )

    subparsers.add_parser("list-workspaces", help="List persisted workspaces")
    subparsers.add_parser("list-stale", help="List stale persisted heartbeats")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "suggest":
        ownership_index = FileOwnershipIndex(load_file_ownership(Path(args.ownership_path)))
        task_path_hints = extract_task_path_hints(Path(args.task_path)) if args.task_path else []
        suggestion = OwnershipSuggestionEngine(
            ownership_index,
            fallback_owner=args.fallback_owner,
        ).suggest(candidate_paths=args.paths, task_path_hints=task_path_hints)
        print(json.dumps(suggestion, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    registry = SQLiteCollaborationRegistry(Path(args.sqlite_path))

    try:
        if args.command == "assign":
            issue = _IssueRef(identifier=args.issue_identifier)
            registry.record_assignment(
                issue,
                status=args.status,
                assigned_worker_cli=args.worker_cli,
                assigned_by=args.assigned_by,
                acceptance_summary=args.acceptance_summary,
            )
            print(
                json.dumps(
                    registry.get_issue_state(args.issue_identifier)["assignment"],
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0

        if args.command == "state":
            print(
                json.dumps(
                    registry.get_issue_state(args.issue_identifier), ensure_ascii=False, indent=2, sort_keys=True
                )
            )
            return 0

        if args.command == "list-workspaces":
            print(json.dumps({"items": registry.list_workspaces()}, ensure_ascii=False, indent=2, sort_keys=True))
            return 0

        if args.command == "list-stale":
            print(json.dumps({"items": registry.list_stale_heartbeats()}, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
    finally:
        registry.close()

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
