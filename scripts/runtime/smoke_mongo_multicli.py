from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from dotenv import load_dotenv
from pymongo import MongoClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.maestro.collab.runtime_registry import MongoCollaborationRegistry
from src.services.maestro.collab.services import CoordinationService
from src.services.maestro.collab.store.models import WorkItemRecord
from src.services.maestro.profiles.mystocks import COLLAB_CONTROL_PLANE_DEFAULTS
from src.services.symphony.config import ServiceConfig
from src.services.symphony.mongo_tracker import MongoWorkItemTrackerClient
from src.services.symphony.models import WorkflowDefinition
from src.services.symphony.orchestrator import SymphonyOrchestrator
from src.services.symphony.status_api import create_status_app
from src.utils.mongo_runtime_config import get_mongo_connection_kwargs


class _SmokeRunnerFactory:
    def __call__(self, issue, attempt):
        return {"issue": issue.identifier, "attempt": attempt}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a real Mongo-backed multi-CLI smoke flow.")
    parser.add_argument("--mongo-uri", default=None)
    parser.add_argument("--mongo-db", default=None, help="Optional Mongo database name. Defaults to a temporary smoke DB.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run_smoke(mongo_uri=args.mongo_uri, mongo_db=args.mongo_db)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def run_smoke(*, mongo_uri: str | None, mongo_db: str | None = None) -> dict[str, object]:
    db_name = mongo_db or f"mystocks_coord_smoke_{uuid4().hex[:8]}"
    client = _build_mongo_client(mongo_uri)

    try:
        database = client[db_name]
        service = CoordinationService(database_store := __import__(
            "src.services.maestro.collab.backends.mongo.store",
            fromlist=["MongoCollaborationStore"],
        ).MongoCollaborationStore(database))
        work_item = WorkItemRecord(
            work_item_id="SMOKE-1",
            task_key="smoke-mongo-runtime",
            title="Mongo smoke flow",
            objective="Validate control-plane and runtime wiring",
            branch="feat/smoke-mongo-runtime",
            owner_cli="cli-9",
            status="dispatched",
            allowed_paths=["src/services/maestro/collab"],
            forbidden_paths=[],
            acceptance_checks=["pytest tests/unit/services/symphony/test_mongo_runtime_flow.py -q"],
            openspec=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        service.upsert_work_item(
            __import__("src.services.maestro.collab.authz.policy", fromlist=["ActorIdentity"]).ActorIdentity(
                cli_name="main", role="main_cli"
            ),
            work_item,
        )

        workflow_definition = WorkflowDefinition(
            config={
                "tracker": {
                    "kind": "mongo",
                    "mongo_uri": mongo_uri or COLLAB_CONTROL_PLANE_DEFAULTS["mongo_uri"],
                    "mongo_db": db_name,
                    "active_states": ["created", "dispatched", "in_progress", "ready_for_review"],
                    "terminal_states": ["verified", "merged", "archived"],
                },
                "runtime": {
                    "cli_name": "cli-9",
                },
            },
            prompt_template="Prompt",
        )
        service_config = ServiceConfig.from_workflow_definition(workflow_definition)
        tracker_client = MongoWorkItemTrackerClient(service_config.tracker, database)
        collab_registry = MongoCollaborationRegistry(database)
        orchestrator = SymphonyOrchestrator(
            workflow_definition=workflow_definition,
            service_config=service_config,
            tracker_client=tracker_client,
            runner_factory=_SmokeRunnerFactory(),
            collab_registry=collab_registry,
        )

        orchestrator.tick_once()
        orchestrator.record_event(
            "SMOKE-1",
            {
                "event": "turn.completed",
                "message": "smoke flow completed",
                "session_id": "smoke-session-1",
            },
        )
        orchestrator.on_worker_exit("SMOKE-1", reason="normal")

        assignment = collab_registry.get_assignment_state("SMOKE-1") or {}
        control_plane = collab_registry.list_control_plane_status_views()
        client_app = TestClient(create_status_app(orchestrator))
        state_payload = client_app.get("/api/v1/state").json()

        return {
            "db_name": db_name,
            "work_item_id": "SMOKE-1",
            "assignment_status": assignment.get("status"),
            "control_plane_status": control_plane[0]["status"] if control_plane else None,
            "status_api_control_plane_count": state_payload["control_plane"]["count"],
        }
    finally:
        client.drop_database(db_name)
        client.close()


def _build_mongo_client(mongo_uri: str | None) -> MongoClient:
    if mongo_uri:
        return MongoClient(mongo_uri)
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    return MongoClient(**get_mongo_connection_kwargs(server_selection_timeout_ms=3000))


if __name__ == "__main__":
    raise SystemExit(main())
