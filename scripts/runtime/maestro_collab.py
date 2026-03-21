from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from pymongo import MongoClient

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
from src.services.maestro.collab.authz import ActorIdentity, AuthorizationError
from src.services.maestro.collab.backends.mongo import MongoCollaborationStore
from src.services.maestro.collab.services import CoordinationService, GraphitiPreflightService
from src.services.maestro.collab.store.models import WorkItemRecord, WorkRequestRecord, WorkUpdateRecord
from src.services.maestro.profiles.mystocks import COLLAB_CONTROL_PLANE_DEFAULTS
from src.utils.mongo_runtime_config import get_mongo_connection_kwargs
from scripts.runtime.export_collab_snapshots import render_task_markdown, render_task_report_markdown

GRAPHITI_CLI_EXAMPLES = """Examples:
  python scripts/runtime/coordctl.py graphiti preflight --work-item-id MT-100 --actor-cli cli-1 --task-path TASK.md --output json
  python scripts/runtime/coordctl.py graphiti remember --actor-cli cli-1 --group-id mystocks_spec_docs --name "Architecture Note" --body "Document the Graphiti flow." --output json
  python scripts/runtime/coordctl.py graphiti search --actor-cli cli-1 --query "Graphiti workflow guide" --group-id mystocks_spec_docs --output json
"""


@dataclass(frozen=True)
class _IssueRef:
    identifier: str
    id: str | None = None


class _MongoCoordinationFacade:
    def __init__(self, service: CoordinationService) -> None:
        self._service = service
        self._graphiti_preflight = GraphitiPreflightService(service=service)

    def create_work_item(self, payload: dict) -> dict:
        now = _utcnow()
        work_item = WorkItemRecord(
            work_item_id=payload["work_item_id"],
            task_key=payload["task_key"],
            title=payload["title"],
            objective=payload["objective"],
            branch=payload["branch"],
            owner_cli=payload["owner_cli"],
            status=payload.get("status", "created"),
            allowed_paths=payload.get("allowed_paths", []),
            forbidden_paths=payload.get("forbidden_paths", []),
            acceptance_checks=payload.get("acceptance_checks", []),
            openspec=payload.get("openspec"),
            created_at=now,
            updated_at=now,
        )
        stored = self._service.upsert_work_item(ActorIdentity(cli_name="main", role="main_cli"), work_item)
        return stored.model_dump(mode="json")

    def get_work_item(self, work_item_id: str) -> dict | None:
        work_item = self._service.get_work_item(ActorIdentity(cli_name="main", role="main_cli"), work_item_id)
        if work_item is None:
            return None
        return work_item.model_dump(mode="json")

    def list_work_items(self) -> list[dict]:
        return [item.model_dump(mode="json") for item in self._service.list_work_items(ActorIdentity(cli_name="main", role="main_cli"))]

    def list_work_updates(self, work_item_id: str) -> list[dict]:
        return [
            item.model_dump(mode="json")
            for item in self._service.list_work_updates(ActorIdentity(cli_name="main", role="main_cli"), work_item_id)
        ]

    def list_work_requests(self, work_item_id: str) -> list[dict]:
        return [
            item.model_dump(mode="json")
            for item in self._service.list_work_requests(ActorIdentity(cli_name="main", role="main_cli"), work_item_id)
        ]

    def list_work_events(self, work_item_id: str) -> list[dict]:
        return [
            item.model_dump(mode="json")
            for item in self._service.list_work_events(ActorIdentity(cli_name="main", role="main_cli"), work_item_id)
        ]

    def get_worker_status_view(self, work_item_id: str) -> dict | None:
        status_view = self._service.get_worker_status_view(ActorIdentity(cli_name="main", role="main_cli"), work_item_id)
        return None if status_view is None else status_view.model_dump(mode="json")

    def transition_work_item(self, work_item_id: str, status: str, actor_cli: str) -> dict:
        work_item = self._service.get_work_item(ActorIdentity(cli_name="main", role="main_cli"), work_item_id)
        if work_item is None:
            raise KeyError(f"Unknown work item: {work_item_id}")
        updated = work_item.model_copy(update={"status": status, "updated_at": _utcnow()})
        role = "main_cli" if actor_cli == "main" else "worker_cli"
        stored = self._service.upsert_work_item(ActorIdentity(cli_name=actor_cli, role=role), updated)
        return stored.model_dump(mode="json")

    def create_work_update(self, work_item_id: str, actor_cli: str, summary: str, status: str) -> dict:
        update = WorkUpdateRecord(
            work_item_id=work_item_id,
            update_id=f"upd-{uuid4().hex}",
            actor_cli=actor_cli,
            status=status,
            summary=summary,
            details={},
            created_at=_utcnow(),
        )
        stored = self._service.append_work_update(ActorIdentity(cli_name=actor_cli, role="worker_cli"), update)
        return stored.model_dump(mode="json")

    def create_work_request(self, work_item_id: str, actor_cli: str, request_id: str, request_type: str, summary: str) -> dict:
        request = WorkRequestRecord(
            work_item_id=work_item_id,
            request_id=request_id,
            actor_cli=actor_cli,
            status="pending",
            request_type=request_type,
            summary=summary,
            payload={},
            created_at=_utcnow(),
            reviewed_at=None,
            reviewed_by=None,
        )
        stored = self._service.create_work_request(ActorIdentity(cli_name=actor_cli, role="worker_cli"), request)
        return stored.model_dump(mode="json")

    def review_work_request(self, work_item_id: str, request_id: str, reviewed_by: str, status: str) -> dict:
        reviewed = self._service.review_work_request(
            ActorIdentity(cli_name=reviewed_by, role="main_cli"),
            work_item_id=work_item_id,
            request_id=request_id,
            reviewed_by=reviewed_by,
            status=status,
        )
        return reviewed.model_dump(mode="json")

    def run_graphiti_preflight(
        self,
        work_item_id: str,
        actor_cli: str,
        task_path: str | None = None,
        write_memory: bool = False,
        max_wait_seconds: int = 60,
    ) -> dict:
        role = "main_cli" if actor_cli == "main" else "worker_cli"
        result = self._graphiti_preflight.run(
            actor=ActorIdentity(cli_name=actor_cli, role=role),
            work_item_id=work_item_id,
            task_path=Path(task_path) if task_path else None,
            write_memory=write_memory,
            max_wait_seconds=max_wait_seconds,
        )
        payload = result.to_dict()
        payload["actor_cli"] = actor_cli
        payload["task_path"] = task_path
        payload["write_memory"] = write_memory
        payload["max_wait_seconds"] = max_wait_seconds
        return payload

    def run_graphiti_remember(
        self,
        work_item_id: str,
        actor_cli: str,
        task_path: str | None = None,
        max_wait_seconds: int = 60,
    ) -> dict:
        role = "main_cli" if actor_cli == "main" else "worker_cli"
        result = self._graphiti_preflight.remember(
            actor=ActorIdentity(cli_name=actor_cli, role=role),
            work_item_id=work_item_id,
            task_path=Path(task_path) if task_path else None,
            max_wait_seconds=max_wait_seconds,
        )
        payload = result.to_dict()
        payload["actor_cli"] = actor_cli
        payload["task_path"] = task_path
        payload["max_wait_seconds"] = max_wait_seconds
        return payload


class _GraphitiFacade:
    def __init__(self, service: CoordinationService | None = None) -> None:
        self._graphiti = GraphitiPreflightService(service=service)

    def run_graphiti_preflight(
        self,
        work_item_id: str,
        actor_cli: str,
        task_path: str | None = None,
        write_memory: bool = False,
        max_wait_seconds: int = 60,
    ) -> dict:
        role = "main_cli" if actor_cli == "main" else "worker_cli"
        result = self._graphiti.run(
            actor=ActorIdentity(cli_name=actor_cli, role=role),
            work_item_id=work_item_id,
            task_path=Path(task_path) if task_path else None,
            write_memory=write_memory,
            max_wait_seconds=max_wait_seconds,
        )
        payload = result.to_dict()
        payload["actor_cli"] = actor_cli
        payload["task_path"] = task_path
        payload["write_memory"] = write_memory
        payload["max_wait_seconds"] = max_wait_seconds
        return payload

    def run_graphiti_remember(
        self,
        work_item_id: str,
        actor_cli: str,
        task_path: str | None = None,
        max_wait_seconds: int = 60,
    ) -> dict:
        role = "main_cli" if actor_cli == "main" else "worker_cli"
        result = self._graphiti.remember(
            actor=ActorIdentity(cli_name=actor_cli, role=role),
            work_item_id=work_item_id,
            task_path=Path(task_path) if task_path else None,
            max_wait_seconds=max_wait_seconds,
        )
        payload = result.to_dict()
        payload["actor_cli"] = actor_cli
        payload["task_path"] = task_path
        payload["max_wait_seconds"] = max_wait_seconds
        return payload

    def run_graphiti_generic_remember(
        self,
        *,
        actor_cli: str,
        group_id: str,
        name: str,
        body: str,
        max_wait_seconds: int = 60,
    ) -> dict:
        result = self._graphiti.remember_generic(
            actor_cli=actor_cli,
            group_id=group_id,
            name=name,
            body=body,
            max_wait_seconds=max_wait_seconds,
        )
        payload = result.to_dict()
        payload["actor_cli"] = actor_cli
        payload["name"] = name
        payload["body"] = body
        payload["max_wait_seconds"] = max_wait_seconds
        return payload

    def run_graphiti_generic_search(
        self,
        *,
        actor_cli: str,
        query: str,
        group_ids: list[str],
        query_type: str = "all",
        max_nodes: int = 5,
        max_facts: int = 5,
    ) -> dict:
        result = self._graphiti.search_generic(
            actor_cli=actor_cli,
            query=query,
            group_ids=group_ids,
            query_type=query_type,
            max_nodes=max_nodes,
            max_facts=max_facts,
        )
        payload = result.to_dict()
        payload["actor_cli"] = actor_cli
        return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Maestro collaboration state.",
        epilog=GRAPHITI_CLI_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--sqlite-path", default=".symphony/tracker.db", help="Path to the local tracker sqlite DB.")
    parser.add_argument(
        "--mongo-uri",
        default=None,
        help="MongoDB URI for coordination state. If omitted, use env/config-driven Mongo connection settings.",
    )
    parser.add_argument(
        "--mongo-db",
        default=COLLAB_CONTROL_PLANE_DEFAULTS["mongo_db"],
        help="MongoDB database name for coordination state.",
    )

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
    suggest_parser.add_argument("--ownership-path", default=".FILE_OWNERSHIP", help="Path to the repository ownership rules file.")
    suggest_parser.add_argument("--task-path", default=None, help="Optional TASK.md path used to derive path hints.")
    suggest_parser.add_argument("--path", dest="paths", action="append", default=[], help="Explicit candidate path. Can be provided multiple times.")
    suggest_parser.add_argument("--fallback-owner", default="main", help="Fallback owner when no explicit ownership rule matches.")

    subparsers.add_parser("list-workspaces", help="List persisted workspaces")
    subparsers.add_parser("list-stale", help="List stale persisted heartbeats")

    work_parser = subparsers.add_parser("work", help="Manage Mongo-backed work items")
    work_subparsers = work_parser.add_subparsers(dest="work_command", required=True)

    work_create = work_subparsers.add_parser("create", help="Create a work item")
    work_create.add_argument("--work-item-id", required=True)
    work_create.add_argument("--task-key", required=True)
    work_create.add_argument("--title", required=True)
    work_create.add_argument("--objective", required=True)
    work_create.add_argument("--branch", required=True)
    work_create.add_argument("--owner-cli", required=True)
    work_create.add_argument("--status", default="created")
    work_create.add_argument("--allowed-path", action="append", default=[])
    work_create.add_argument("--forbidden-path", action="append", default=[])
    work_create.add_argument("--acceptance-check", action="append", default=[])
    work_create.add_argument("--openspec-json", default=None)
    work_create.add_argument("--output", choices=("json", "text"), default="json")

    work_list = work_subparsers.add_parser("list", help="List work items")
    work_list.add_argument("--output", choices=("json", "text"), default="json")

    work_show = work_subparsers.add_parser("show", help="Show one work item")
    work_show.add_argument("work_item_id")
    work_show.add_argument("--output", choices=("json", "text"), default="json")

    work_preflight = work_subparsers.add_parser("preflight", help="Run repo-local Graphiti preflight for a work item")
    work_preflight.add_argument("work_item_id")
    work_preflight.add_argument("--actor-cli", required=True)
    work_preflight.add_argument("--task-path", default=None)
    work_preflight.add_argument("--write-memory", action="store_true")
    work_preflight.add_argument("--max-wait-seconds", type=int, default=60)
    work_preflight.add_argument("--output", choices=("json", "text"), default="json")

    work_remember = work_subparsers.add_parser("remember", help="Record an explicit Graphiti memory for a work item")
    work_remember.add_argument("work_item_id")
    work_remember.add_argument("--actor-cli", required=True)
    work_remember.add_argument("--task-path", default=None)
    work_remember.add_argument("--max-wait-seconds", type=int, default=60)
    work_remember.add_argument("--output", choices=("json", "text"), default="json")

    work_export_task = work_subparsers.add_parser("export-task", help="Export TASK.md snapshot from Mongo state")
    work_export_task.add_argument("work_item_id")
    work_export_task.add_argument("--output-path", default=None)
    work_export_task.add_argument("--output", choices=("json", "text"), default="json")

    work_export_report = work_subparsers.add_parser("export-task-report", help="Export TASK-REPORT.md snapshot from Mongo state")
    work_export_report.add_argument("work_item_id")
    work_export_report.add_argument("--output-path", default=None)
    work_export_report.add_argument("--output", choices=("json", "text"), default="json")

    work_transition = work_subparsers.add_parser("transition", help="Transition work item status")
    work_transition.add_argument("work_item_id")
    work_transition.add_argument("--to", required=True)
    work_transition.add_argument("--actor-cli", default="main")
    work_transition.add_argument("--output", choices=("json", "text"), default="json")

    work_mark = work_subparsers.add_parser("mark", help="Mark owned work with a status update")
    work_mark.add_argument("work_item_id")
    work_mark.add_argument("--status", required=True)
    work_mark.add_argument("--actor-cli", required=True)
    work_mark.add_argument("--summary", default=None)
    work_mark.add_argument("--output", choices=("json", "text"), default="json")

    update_parser = subparsers.add_parser("update", help="Manage work updates")
    update_subparsers = update_parser.add_subparsers(dest="update_command", required=True)
    update_add = update_subparsers.add_parser("add", help="Append a work update")
    update_add.add_argument("work_item_id")
    update_add.add_argument("--actor-cli", required=True)
    update_add.add_argument("--summary", required=True)
    update_add.add_argument("--status", required=True)
    update_add.add_argument("--output", choices=("json", "text"), default="json")

    request_parser = subparsers.add_parser("request", help="Manage work requests")
    request_subparsers = request_parser.add_subparsers(dest="request_command", required=True)
    request_create = request_subparsers.add_parser("create", help="Create a work request")
    request_create.add_argument("work_item_id")
    request_create.add_argument("--actor-cli", required=True)
    request_create.add_argument("--request-id", required=True)
    request_create.add_argument("--request-type", required=True)
    request_create.add_argument("--summary", required=True)
    request_create.add_argument("--output", choices=("json", "text"), default="json")

    request_review = request_subparsers.add_parser("review", help="Review a work request")
    request_review.add_argument("work_item_id")
    request_review.add_argument("request_id")
    request_review.add_argument("--reviewed-by", default="main")
    request_review.add_argument("--status", required=True)
    request_review.add_argument("--output", choices=("json", "text"), default="json")

    graphiti_parser = subparsers.add_parser("graphiti", help="Run Graphiti memory operations")
    graphiti_subparsers = graphiti_parser.add_subparsers(dest="graphiti_command", required=True)

    graphiti_preflight = graphiti_subparsers.add_parser("preflight", help="Run Mongo-backed Graphiti preflight")
    graphiti_preflight.add_argument("--work-item-id", required=True)
    graphiti_preflight.add_argument("--actor-cli", required=True)
    graphiti_preflight.add_argument("--task-path", default=None)
    graphiti_preflight.add_argument("--write-memory", action="store_true")
    graphiti_preflight.add_argument("--max-wait-seconds", type=int, default=60)
    graphiti_preflight.add_argument("--output", choices=("json", "text"), default="json")

    graphiti_remember = graphiti_subparsers.add_parser("remember", help="Record Graphiti memory")
    graphiti_remember.add_argument("--work-item-id", default=None)
    graphiti_remember.add_argument("--actor-cli", default="main")
    graphiti_remember.add_argument("--task-path", default=None)
    graphiti_remember.add_argument("--group-id", default=None)
    graphiti_remember.add_argument("--name", default=None)
    graphiti_remember.add_argument("--body", default=None)
    graphiti_remember.add_argument("--body-file", default=None)
    graphiti_remember.add_argument("--max-wait-seconds", type=int, default=60)
    graphiti_remember.add_argument("--output", choices=("json", "text"), default="json")

    graphiti_search = graphiti_subparsers.add_parser("search", help="Search Graphiti memory directly")
    graphiti_search.add_argument("--actor-cli", default="main")
    graphiti_search.add_argument("--query", required=True)
    graphiti_search.add_argument("--group-id", dest="group_ids", action="append", default=[])
    graphiti_search.add_argument("--query-type", choices=("all", "nodes", "facts"), default="all")
    graphiti_search.add_argument("--max-nodes", type=int, default=5)
    graphiti_search.add_argument("--max-facts", type=int, default=5)
    graphiti_search.add_argument("--output", choices=("json", "text"), default="json")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        if args.command == "suggest":
            ownership_index = FileOwnershipIndex(load_file_ownership(Path(args.ownership_path)))
            task_path_hints = extract_task_path_hints(Path(args.task_path)) if args.task_path else []
            suggestion = OwnershipSuggestionEngine(
                ownership_index,
                fallback_owner=args.fallback_owner,
            ).suggest(candidate_paths=args.paths, task_path_hints=task_path_hints)
            _emit(suggestion, output="json")
            return 0

        if args.command in {"work", "update", "request"}:
            service = _build_coordination_service(args)
            payload, output = _handle_coordination_command(args, service)
            _emit(payload, output=output)
            return 0
        if args.command == "graphiti":
            service = _build_graphiti_facade(args)
            payload, output = _handle_graphiti_command(args, service)
            _emit(payload, output=output)
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
                _emit(registry.get_issue_state(args.issue_identifier)["assignment"], output="json")
                return 0

            if args.command == "state":
                _emit(registry.get_issue_state(args.issue_identifier), output="json")
                return 0

            if args.command == "list-workspaces":
                _emit({"items": registry.list_workspaces()}, output="json")
                return 0

            if args.command == "list-stale":
                _emit({"items": registry.list_stale_heartbeats()}, output="json")
                return 0
        finally:
            registry.close()
    except (AuthorizationError, KeyError, ValueError) as exc:
        output = getattr(args, "output", "json")
        _emit_error(exc, output=output)
        return 1

    return 1


def _build_coordination_service(args: argparse.Namespace) -> _MongoCoordinationFacade:
    client = _build_mongo_client(args.mongo_uri)
    database = client[args.mongo_db]
    store = MongoCollaborationStore(database)
    service = CoordinationService(store)
    return _MongoCoordinationFacade(service)


def _build_graphiti_facade(args: argparse.Namespace) -> _GraphitiFacade:
    needs_coordination = args.graphiti_command == "preflight" or (
        args.graphiti_command == "remember" and getattr(args, "work_item_id", None)
    )
    if not needs_coordination:
        return _GraphitiFacade()

    client = _build_mongo_client(args.mongo_uri)
    database = client[args.mongo_db]
    store = MongoCollaborationStore(database)
    service = CoordinationService(store)
    return _GraphitiFacade(service)


def _build_mongo_client(mongo_uri: str | None) -> MongoClient:
    if mongo_uri:
        return MongoClient(mongo_uri)

    load_dotenv(PROJECT_ROOT / ".env", override=False)
    return MongoClient(**get_mongo_connection_kwargs(server_selection_timeout_ms=3000))


def _handle_coordination_command(args: argparse.Namespace, service: _MongoCoordinationFacade) -> tuple[dict | list[dict] | str, str]:
    if args.command == "work":
        if args.work_command == "create":
            openspec = json.loads(args.openspec_json) if args.openspec_json else None
            payload = service.create_work_item(
                {
                    "work_item_id": args.work_item_id,
                    "task_key": args.task_key,
                    "title": args.title,
                    "objective": args.objective,
                    "branch": args.branch,
                    "owner_cli": args.owner_cli,
                    "status": args.status,
                    "allowed_paths": args.allowed_path,
                    "forbidden_paths": args.forbidden_path,
                    "acceptance_checks": args.acceptance_check,
                    "openspec": openspec,
                }
            )
            return payload, args.output
        if args.work_command == "list":
            return service.list_work_items(), args.output
        if args.work_command == "show":
            payload = service.get_work_item(args.work_item_id)
            if payload is None:
                raise KeyError(f"Unknown work item: {args.work_item_id}")
            return payload, args.output
        if args.work_command == "preflight":
            return (
                service.run_graphiti_preflight(
                    args.work_item_id,
                    actor_cli=args.actor_cli,
                    task_path=args.task_path,
                    write_memory=args.write_memory,
                    max_wait_seconds=args.max_wait_seconds,
                ),
                args.output,
            )
        if args.work_command == "remember":
            return (
                service.run_graphiti_remember(
                    args.work_item_id,
                    actor_cli=args.actor_cli,
                    task_path=args.task_path,
                    max_wait_seconds=args.max_wait_seconds,
                ),
                args.output,
            )
        if args.work_command == "export-task":
            work_item = service.get_work_item(args.work_item_id)
            if work_item is None:
                raise KeyError(f"Unknown work item: {args.work_item_id}")
            status_view = service.get_worker_status_view(args.work_item_id)
            markdown = render_task_markdown(work_item=work_item, status_view=status_view)
            if args.output_path:
                output_path = Path(args.output_path)
                output_path.write_text(markdown, encoding="utf-8")
                return {
                    "artifact": "TASK.md",
                    "output_path": str(output_path),
                    "work_item_id": args.work_item_id,
                }, args.output
            return markdown, "raw"
        if args.work_command == "export-task-report":
            work_item = service.get_work_item(args.work_item_id)
            if work_item is None:
                raise KeyError(f"Unknown work item: {args.work_item_id}")
            status_view = service.get_worker_status_view(args.work_item_id)
            updates = service.list_work_updates(args.work_item_id)
            requests = service.list_work_requests(args.work_item_id)
            events = service.list_work_events(args.work_item_id)
            markdown = render_task_report_markdown(
                work_item=work_item,
                updates=updates,
                requests=requests,
                status_view=status_view,
                events=events,
            )
            if args.output_path:
                output_path = Path(args.output_path)
                output_path.write_text(markdown, encoding="utf-8")
                return {
                    "artifact": "TASK-REPORT.md",
                    "output_path": str(output_path),
                    "work_item_id": args.work_item_id,
                }, args.output
            return markdown, "raw"
        if args.work_command == "transition":
            return service.transition_work_item(args.work_item_id, args.to, args.actor_cli), args.output
        if args.work_command == "mark":
            summary = args.summary or f"status marked to {args.status}"
            return service.create_work_update(args.work_item_id, args.actor_cli, summary, args.status), args.output

    if args.command == "update" and args.update_command == "add":
        return service.create_work_update(args.work_item_id, args.actor_cli, args.summary, args.status), args.output

    if args.command == "request":
        if args.request_command == "create":
            return (
                service.create_work_request(
                    args.work_item_id,
                    args.actor_cli,
                    args.request_id,
                    args.request_type,
                    args.summary,
                ),
                args.output,
            )
        if args.request_command == "review":
            return (
                service.review_work_request(args.work_item_id, args.request_id, args.reviewed_by, args.status),
                args.output,
            )

    raise ValueError("Unsupported coordination command")


def _handle_graphiti_command(args: argparse.Namespace, service: _GraphitiFacade) -> tuple[dict | list[dict] | str, str]:
    if args.graphiti_command == "preflight":
        return (
            service.run_graphiti_preflight(
                args.work_item_id,
                actor_cli=args.actor_cli,
                task_path=args.task_path,
                write_memory=args.write_memory,
                max_wait_seconds=args.max_wait_seconds,
            ),
            args.output,
        )

    if args.graphiti_command == "remember":
        if args.work_item_id:
            return (
                service.run_graphiti_remember(
                    args.work_item_id,
                    actor_cli=args.actor_cli,
                    task_path=args.task_path,
                    max_wait_seconds=args.max_wait_seconds,
                ),
                args.output,
            )

        if not args.group_id:
            raise ValueError("Generic Graphiti remember requires --group-id")
        if not args.name:
            raise ValueError("Generic Graphiti remember requires --name")
        body = args.body
        if args.body_file:
            body = Path(args.body_file).read_text(encoding="utf-8")
        if not body:
            raise ValueError("Generic Graphiti remember requires --body or --body-file")

        return (
            service.run_graphiti_generic_remember(
                actor_cli=args.actor_cli,
                group_id=args.group_id,
                name=args.name,
                body=body,
                max_wait_seconds=args.max_wait_seconds,
            ),
            args.output,
        )

    if args.graphiti_command == "search":
        return (
            service.run_graphiti_generic_search(
                actor_cli=args.actor_cli,
                query=args.query,
                group_ids=args.group_ids,
                query_type=args.query_type,
                max_nodes=args.max_nodes,
                max_facts=args.max_facts,
            ),
            args.output,
        )

    raise ValueError("Unsupported graphiti command")


def _emit(payload: dict | list[dict] | str, *, output: str) -> None:
    if output == "raw":
        print(payload)
        return
    if output == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return

    if isinstance(payload, list):
        for item in payload:
            print(_format_text(item))
        return
    print(_format_text(payload))


def _emit_error(error: Exception, *, output: str) -> None:
    payload = {
        "error_code": error.__class__.__name__,
        "message": str(error),
        "audit_id": f"err-{uuid4().hex[:12]}",
    }
    _emit(payload, output=output)


def _format_text(payload: dict) -> str:
    parts = []
    for key in sorted(payload):
        value = payload[key]
        if isinstance(value, (dict, list)):
            rendered = json.dumps(value, ensure_ascii=False, sort_keys=True)
        else:
            rendered = str(value)
        parts.append(f"{key}={rendered}")
    return " ".join(parts)


def _utcnow() -> datetime:
    return datetime.now(UTC)


if __name__ == "__main__":
    raise SystemExit(main())
