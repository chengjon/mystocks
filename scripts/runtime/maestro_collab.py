from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from pymongo import MongoClient
from pymongo.errors import OperationFailure


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.runtime.export_collab_snapshots import (
    _extract_graphiti_projection,
    render_task_markdown,
    render_task_report_markdown,
)
from src.services.maestro.collab import (
    FileOwnershipIndex,
    OwnershipSuggestionEngine,
    SQLiteCollaborationRegistry,
    extract_task_path_hints,
    load_file_ownership,
)
from src.services.maestro.collab.authz import ActorIdentity, AuthorizationError
from src.services.maestro.collab.backends.mongo import MongoCollaborationStore
from src.services.maestro.collab.integrations import GraphitiAdapter, GraphitiMcpTransport
from src.services.maestro.collab.services import CoordinationService, GraphitiPreflightService, TranscriptLedgerService
from src.services.maestro.collab.store.models import (
    TranscriptLegacyIndexRecord,
    TranscriptSessionRecord,
    WorkItemRecord,
    WorkRequestRecord,
    WorkUpdateRecord,
)
from src.services.maestro.collab.transcript_archive import FilesystemTranscriptArchiveBackend
from src.services.maestro.profiles.mystocks import COLLAB_CONTROL_PLANE_DEFAULTS
from src.utils.cli_error_output import build_cli_error_payload
from src.utils.mongo_runtime_config import (
    build_mongo_auth_runtime_error,
    build_project_runtime_mongo_client,
    get_runtime_mongo_db_default,
    get_runtime_mongo_uri_default,
    is_mongo_auth_error,
)


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
    def __init__(self, service: CoordinationService, *, transcript_service: TranscriptLedgerService) -> None:
        self._service = service
        self._transcript_service = transcript_service
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
            metadata=payload.get("metadata"),
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
        return [
            item.model_dump(mode="json")
            for item in self._service.list_work_items(ActorIdentity(cli_name="main", role="main_cli"))
        ]

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
        status_view = self._service.get_worker_status_view(
            ActorIdentity(cli_name="main", role="main_cli"), work_item_id
        )
        return None if status_view is None else status_view.model_dump(mode="json")

    def transition_work_item(self, work_item_id: str, status: str, actor_cli: str) -> dict:
        work_item = self._service.get_work_item(ActorIdentity(cli_name="main", role="main_cli"), work_item_id)
        if work_item is None:
            raise KeyError(f"Unknown work item: {work_item_id}")
        updated = work_item.model_copy(update={"status": status, "updated_at": _utcnow()})
        role = "main_cli" if actor_cli == "main" else "worker_cli"
        stored = self._service.upsert_work_item(ActorIdentity(cli_name=actor_cli, role=role), updated)
        return stored.model_dump(mode="json")

    def create_work_update(
        self,
        work_item_id: str,
        actor_cli: str,
        summary: str,
        status: str,
        *,
        details: dict | None = None,
    ) -> dict:
        update = WorkUpdateRecord(
            work_item_id=work_item_id,
            update_id=f"upd-{uuid4().hex}",
            actor_cli=actor_cli,
            status=status,
            summary=summary,
            details=details or {},
            created_at=_utcnow(),
        )
        stored = self._service.append_work_update(ActorIdentity(cli_name=actor_cli, role="worker_cli"), update)
        return stored.model_dump(mode="json")

    def create_work_request(
        self, work_item_id: str, actor_cli: str, request_id: str, request_type: str, summary: str
    ) -> dict:
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

    def start_transcript_session(
        self,
        session_id: str,
        work_item_id: str,
        actor_cli: str,
        transcript_kind: str,
        *,
        archive_policy_version: str = "v1",
    ) -> dict:
        work_item = self._service.get_work_item(ActorIdentity(cli_name="main", role="main_cli"), work_item_id)
        if work_item is None:
            raise KeyError(f"Unknown work item: {work_item_id}")

        stored = self._transcript_service.start_session(
            self._actor(actor_cli),
            TranscriptSessionRecord(
                session_id=session_id,
                work_item_id=work_item_id,
                actor_cli=actor_cli,
                branch=work_item.branch,
                transcript_kind=transcript_kind,
                started_at=_utcnow(),
                closed_at=None,
                archive_policy_version=archive_policy_version,
            ),
        )
        return stored.model_dump(mode="json")

    def append_transcript_block(
        self,
        session_id: str,
        actor_cli: str,
        content: str,
        *,
        payload: dict | None = None,
    ) -> dict:
        stored = self._transcript_service.append_block(
            self._actor(actor_cli),
            session_id=session_id,
            event_id=f"tevt-{uuid4().hex}",
            occurred_at=_utcnow(),
            content=content,
            payload=payload,
        )
        return stored.model_dump(mode="json")

    def close_transcript_session(
        self,
        session_id: str,
        actor_cli: str,
        *,
        payload: dict | None = None,
    ) -> dict:
        stored = self._transcript_service.close_session(
            self._actor(actor_cli),
            session_id=session_id,
            event_id=f"tevt-{uuid4().hex}",
            occurred_at=_utcnow(),
            payload=payload,
        )
        return stored.model_dump(mode="json")

    def show_transcript_session(self, session_id: str, actor_cli: str) -> dict:
        actor = self._actor(actor_cli)
        session = self._transcript_service.get_session(actor, session_id)
        if session is None:
            raise KeyError(f"Unknown transcript session: {session_id}")
        events = self._transcript_service.list_session_events(actor, session_id)
        hot_body = self._transcript_service.get_hot_body(actor, session_id)
        hot_body_available = self._is_hot_body_available(hot_body=hot_body, events=events)
        return {
            "session": session.model_dump(mode="json"),
            "event_count": len(events),
            "hot_body_available": hot_body_available,
            "archive_ref": self._archive_ref_from_events(events),
        }

    def export_transcript_session(self, session_id: str, actor_cli: str) -> dict:
        actor = self._actor(actor_cli)
        session = self._transcript_service.get_session(actor, session_id)
        if session is None:
            raise KeyError(f"Unknown transcript session: {session_id}")
        events = self._transcript_service.list_session_events(actor, session_id)
        hot_body = self._transcript_service.get_hot_body(actor, session_id)
        hot_body_available = self._is_hot_body_available(hot_body=hot_body, events=events)
        archive_ref = self._archive_ref_from_events(events)
        return {
            "session": session.model_dump(mode="json"),
            "events": [event.model_dump(mode="json") for event in events],
            "hot_body": hot_body.model_dump(mode="json") if hot_body_available and hot_body is not None else None,
            "archive_ref": None if hot_body_available else archive_ref,
        }

    def list_work_item_transcripts(self, work_item_id: str) -> list[dict]:
        actor = ActorIdentity(cli_name="main", role="main_cli")
        summaries: list[dict] = []
        for session in self._transcript_service.list_work_item_sessions(actor, work_item_id):
            events = self._transcript_service.list_session_events(actor, session.session_id)
            hot_body = self._transcript_service.get_hot_body(actor, session.session_id)
            summaries.append(
                {
                    "session_id": session.session_id,
                    "actor_cli": session.actor_cli,
                    "transcript_kind": session.transcript_kind,
                    "started_at": session.started_at.isoformat(),
                    "hot_body_available": self._is_hot_body_available(hot_body=hot_body, events=events),
                    "archive_locator": self._archive_ref_from_events(events),
                    "source": "ledger",
                },
            )

        for legacy_index in self._transcript_service.list_legacy_indexes(actor, work_item_id):
            summaries.append(
                {
                    "legacy_session_label": legacy_index.legacy_session_label,
                    "legacy_block_kind": legacy_index.legacy_block_kind,
                    "captured_at": legacy_index.captured_at.isoformat(),
                    "archive_locator": legacy_index.archive_locator,
                    "source": "legacy",
                },
            )

        return summaries

    def index_legacy_transcript(
        self,
        *,
        work_item_id: str,
        actor_cli: str,
        legacy_block_kind: str,
        legacy_session_label: str,
        source_artifact: str,
        captured_at: datetime,
        source_anchor: str,
        archive_locator: str,
        checksum: str,
        migration_batch_id: str,
    ) -> dict:
        stored = self._transcript_service.index_legacy_record(
            self._actor(actor_cli),
            TranscriptLegacyIndexRecord(
                legacy_index_id=f"legacy-{uuid4().hex}",
                work_item_id=work_item_id,
                source_artifact=source_artifact,
                legacy_block_kind=legacy_block_kind,
                legacy_session_label=legacy_session_label,
                captured_at=captured_at,
                source_anchor=source_anchor,
                archive_locator=archive_locator,
                checksum=checksum,
                migration_batch_id=migration_batch_id,
                migration_recorded_at=_utcnow(),
            ),
        )
        return stored.model_dump(mode="json")

    @staticmethod
    def _actor(actor_cli: str) -> ActorIdentity:
        role = "main_cli" if actor_cli == "main" else "worker_cli"
        return ActorIdentity(cli_name=actor_cli, role=role)

    @staticmethod
    def _archive_ref_from_events(events: list[Any]) -> str | None:
        archive_ref: str | None = None
        for event in events:
            payload = event.payload if hasattr(event, "payload") else event.get("payload", {})
            event_type = event.event_type if hasattr(event, "event_type") else event.get("event_type")
            if event_type == "transcript.body_archived":
                archive_ref = payload.get("archive_locator")
            elif event_type == "transcript.hot_body_expired":
                archive_ref = payload.get("archive_locator") or archive_ref
        return archive_ref

    @staticmethod
    def _is_hot_body_available(*, hot_body: Any, events: list[Any]) -> bool:
        if hot_body is None:
            return False
        if any(
            (event.event_type if hasattr(event, "event_type") else event.get("event_type"))
            == "transcript.hot_body_expired"
            for event in events
        ):
            return False
        purge_after = hot_body.purge_after if hasattr(hot_body, "purge_after") else hot_body.get("purge_after")
        if isinstance(purge_after, str):
            purge_after = _parse_datetime(purge_after)
        if purge_after is not None and purge_after <= _utcnow():
            return False
        return True


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
        default=get_runtime_mongo_uri_default(COLLAB_CONTROL_PLANE_DEFAULTS["mongo_uri"]),
        help="MongoDB URI for coordination state.",
    )
    parser.add_argument(
        "--mongo-db",
        default=get_runtime_mongo_db_default(COLLAB_CONTROL_PLANE_DEFAULTS["mongo_db"]),
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
    suggest_parser.add_argument(
        "--ownership-path", default=".FILE_OWNERSHIP", help="Path to the repository ownership rules file."
    )
    suggest_parser.add_argument("--task-path", default=None, help="Optional TASK.md path used to derive path hints.")
    suggest_parser.add_argument(
        "--path",
        dest="paths",
        action="append",
        default=[],
        help="Explicit candidate path. Can be provided multiple times.",
    )
    suggest_parser.add_argument(
        "--fallback-owner", default="main", help="Fallback owner when no explicit ownership rule matches."
    )

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
    work_create.add_argument("--metadata-json", default=None)
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

    work_export_report = work_subparsers.add_parser(
        "export-task-report", help="Export TASK-REPORT.md snapshot from Mongo state"
    )
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
    work_mark.add_argument("--details-json", default=None)
    work_mark.add_argument("--output", choices=("json", "text"), default="json")

    update_parser = subparsers.add_parser("update", help="Manage work updates")
    update_subparsers = update_parser.add_subparsers(dest="update_command", required=True)
    update_add = update_subparsers.add_parser("add", help="Append a work update")
    update_add.add_argument("work_item_id")
    update_add.add_argument("--actor-cli", required=True)
    update_add.add_argument("--summary", required=True)
    update_add.add_argument("--status", required=True)
    update_add.add_argument("--details-json", default=None)
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

    transcript_parser = subparsers.add_parser("transcript", help="Manage transcript ledger sessions")
    transcript_subparsers = transcript_parser.add_subparsers(dest="transcript_command", required=True)

    transcript_start = transcript_subparsers.add_parser("start", help="Start a transcript session")
    transcript_start.add_argument("session_id")
    transcript_start.add_argument("--work-item-id", required=True)
    transcript_start.add_argument("--actor-cli", required=True)
    transcript_start.add_argument("--transcript-kind", choices=("AUTO", "MANUAL"), required=True)
    transcript_start.add_argument("--archive-policy-version", default="v1")
    transcript_start.add_argument("--output", choices=("json", "text"), default="json")

    transcript_append = transcript_subparsers.add_parser("append", help="Append a transcript block")
    transcript_append.add_argument("session_id")
    transcript_append.add_argument("--actor-cli", required=True)
    transcript_append_content = transcript_append.add_mutually_exclusive_group(required=True)
    transcript_append_content.add_argument("--content", default=None)
    transcript_append_content.add_argument("--content-file", default=None)
    transcript_append.add_argument("--payload-json", default=None)
    transcript_append.add_argument("--output", choices=("json", "text"), default="json")

    transcript_close = transcript_subparsers.add_parser("close", help="Close a transcript session")
    transcript_close.add_argument("session_id")
    transcript_close.add_argument("--actor-cli", required=True)
    transcript_close.add_argument("--payload-json", default=None)
    transcript_close.add_argument("--output", choices=("json", "text"), default="json")

    transcript_show = transcript_subparsers.add_parser("show-session", help="Show transcript session summary")
    transcript_show.add_argument("session_id")
    transcript_show.add_argument("--actor-cli", required=True)
    transcript_show.add_argument("--output", choices=("json", "text"), default="json")

    transcript_export = transcript_subparsers.add_parser("export-session", help="Export transcript session details")
    transcript_export.add_argument("session_id")
    transcript_export.add_argument("--actor-cli", required=True)
    transcript_export.add_argument("--output", choices=("json", "text"), default="json")

    transcript_legacy = transcript_subparsers.add_parser("index-legacy", help="Record a legacy transcript index")
    transcript_legacy.add_argument("--work-item-id", required=True)
    transcript_legacy.add_argument("--actor-cli", required=True)
    transcript_legacy.add_argument("--legacy-block-kind", choices=("AUTO", "MANUAL"), required=True)
    transcript_legacy.add_argument("--legacy-session-label", required=True)
    transcript_legacy.add_argument("--source-artifact", required=True)
    transcript_legacy.add_argument("--captured-at", required=True)
    transcript_legacy.add_argument("--source-anchor", required=True)
    transcript_legacy.add_argument("--archive-locator", required=True)
    transcript_legacy.add_argument("--checksum", required=True)
    transcript_legacy.add_argument("--migration-batch-id", required=True)
    transcript_legacy.add_argument("--output", choices=("json", "text"), default="json")

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

        if args.command in {"work", "update", "request", "transcript"}:
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
    except OperationFailure as exc:
        output = getattr(args, "output", "json")
        if is_mongo_auth_error(exc):
            _emit_error(build_mongo_auth_runtime_error("Mongo control plane"), output=output)
            return 1
        raise
    except (AuthorizationError, KeyError, ValueError, RuntimeError) as exc:
        output = getattr(args, "output", "json")
        _emit_error(exc, output=output)
        return 1

    return 1


def _build_coordination_service(args: argparse.Namespace) -> _MongoCoordinationFacade:
    client = _build_mongo_client(args.mongo_uri)
    database = client[args.mongo_db]
    store = MongoCollaborationStore(database)
    service = CoordinationService(store)
    transcript_defaults = COLLAB_CONTROL_PLANE_DEFAULTS.get("transcript_archive", {})
    archive_backend = None
    if transcript_defaults.get("backend") == "filesystem":
        archive_backend = FilesystemTranscriptArchiveBackend(
            PROJECT_ROOT / transcript_defaults.get("archive_root", ".maestro/transcript-archive"),
        )
    transcript_service = TranscriptLedgerService(
        store,
        archive_backend=archive_backend,
        hot_retention_days=int(transcript_defaults.get("hot_retention_days", 90)),
    )
    return _MongoCoordinationFacade(service, transcript_service=transcript_service)


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


def _build_live_graphiti_projection(events: list[dict]) -> dict[str, str] | None:
    base_projection = _extract_graphiti_projection(events)
    latest_reference = _latest_graphiti_event(
        events,
        event_types=("automation.graphiti_memory_recorded", "automation.graphiti_preflight_checked"),
    )
    if latest_reference is None:
        return None

    payload = latest_reference.get("payload", {})
    episode_uuid = payload.get("episode_uuid")
    group_id = payload.get("group_id")
    if not episode_uuid or not group_id:
        return base_projection

    try:
        adapter = GraphitiAdapter(transport=GraphitiMcpTransport(timeout_seconds=3))
        live_status = adapter.get_ingest_status(episode_uuid=str(episode_uuid), group_id=str(group_id))
    except Exception:
        return base_projection

    projection = dict(base_projection)
    projection["ingest_status"] = str(live_status.ingest_status or projection.get("ingest_status", "(none)"))
    return projection


def _latest_graphiti_event(events: list[dict], *, event_types: tuple[str, ...]) -> dict | None:
    latest_event: dict | None = None
    latest_created_at = ""
    for event in events:
        if event.get("event_type") not in event_types:
            continue
        created_at = str(event.get("created_at", ""))
        if created_at >= latest_created_at:
            latest_event = event
            latest_created_at = created_at
    return latest_event


def _build_mongo_client(mongo_uri: str | None) -> MongoClient:
    return build_project_runtime_mongo_client(PROJECT_ROOT, mongo_uri, server_selection_timeout_ms=3000)


def _handle_coordination_command(
    args: argparse.Namespace, service: _MongoCoordinationFacade
) -> tuple[dict | list[dict] | str, str]:
    if args.command == "work":
        if args.work_command == "create":
            openspec = json.loads(args.openspec_json) if args.openspec_json else None
            metadata = json.loads(args.metadata_json) if args.metadata_json else None
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
                    "metadata": metadata,
                },
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
                transcripts=service.list_work_item_transcripts(args.work_item_id),
                graphiti_projection=_build_live_graphiti_projection(events),
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
            details = json.loads(args.details_json) if args.details_json else {}
            return (
                service.create_work_update(args.work_item_id, args.actor_cli, summary, args.status, details=details),
                args.output,
            )

    if args.command == "update" and args.update_command == "add":
        details = json.loads(args.details_json) if args.details_json else {}
        return (
            service.create_work_update(args.work_item_id, args.actor_cli, args.summary, args.status, details=details),
            args.output,
        )

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

    if args.command == "transcript":
        if args.transcript_command == "start":
            return (
                service.start_transcript_session(
                    args.session_id,
                    args.work_item_id,
                    args.actor_cli,
                    args.transcript_kind,
                    archive_policy_version=args.archive_policy_version,
                ),
                args.output,
            )
        if args.transcript_command == "append":
            payload = json.loads(args.payload_json) if args.payload_json else {}
            content = args.content
            if args.content_file:
                content = Path(args.content_file).read_text(encoding="utf-8")
            return (
                service.append_transcript_block(
                    args.session_id,
                    args.actor_cli,
                    content or "",
                    payload=payload,
                ),
                args.output,
            )
        if args.transcript_command == "close":
            payload = json.loads(args.payload_json) if args.payload_json else {}
            return (
                service.close_transcript_session(
                    args.session_id,
                    args.actor_cli,
                    payload=payload,
                ),
                args.output,
            )
        if args.transcript_command == "show-session":
            return service.show_transcript_session(args.session_id, args.actor_cli), args.output
        if args.transcript_command == "export-session":
            return service.export_transcript_session(args.session_id, args.actor_cli), args.output
        if args.transcript_command == "index-legacy":
            return (
                service.index_legacy_transcript(
                    work_item_id=args.work_item_id,
                    actor_cli=args.actor_cli,
                    legacy_block_kind=args.legacy_block_kind,
                    legacy_session_label=args.legacy_session_label,
                    source_artifact=args.source_artifact,
                    captured_at=_parse_datetime(args.captured_at),
                    source_anchor=args.source_anchor,
                    archive_locator=args.archive_locator,
                    checksum=args.checksum,
                    migration_batch_id=args.migration_batch_id,
                ),
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
    payload = build_cli_error_payload(error, audit_id=f"err-{uuid4().hex[:12]}")
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


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def _utcnow() -> datetime:
    return datetime.now(UTC)


if __name__ == "__main__":
    raise SystemExit(main())
