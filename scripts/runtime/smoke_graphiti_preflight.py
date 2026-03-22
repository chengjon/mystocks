from __future__ import annotations

import argparse
import io
import json
import os
import shlex
import subprocess
import sys
from contextlib import redirect_stdout
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from pymongo import MongoClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.runtime import coordctl
from src.services.maestro.collab.authz import ActorIdentity
from src.services.maestro.collab.backends.mongo.store import MongoCollaborationStore
from src.services.maestro.collab.services import CoordinationService
from src.services.maestro.collab.store.models import WorkItemRecord
from src.utils.mongo_runtime_config import build_mongo_connection_uri, get_mongo_connection_kwargs

SMOKE_WORK_ITEM_ID = "GRAPHITI-PREFLIGHT-SMOKE"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a Mongo-backed Graphiti preflight smoke flow.")
    parser.add_argument("--mongo-uri", default=None)
    parser.add_argument("--mongo-db", default=None, help="Optional Mongo database name. Defaults to a temporary smoke DB.")
    parser.add_argument("--actor-cli", required=True)
    parser.add_argument("--max-wait-seconds", type=int, default=60)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run_smoke(
        mongo_uri=args.mongo_uri,
        mongo_db=args.mongo_db,
        actor_cli=args.actor_cli,
        max_wait_seconds=args.max_wait_seconds,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def run_smoke(
    *,
    mongo_uri: str | None,
    mongo_db: str | None = None,
    actor_cli: str,
    max_wait_seconds: int = 60,
) -> dict[str, object]:
    db_name = mongo_db or f"graphiti_preflight_smoke_{uuid4().hex[:8]}"
    effective_mongo_uri = _resolve_effective_mongo_uri(mongo_uri)
    client = _build_mongo_client(effective_mongo_uri)
    should_drop_database = False

    try:
        database = client[db_name]
        store = MongoCollaborationStore(database)
        service = CoordinationService(store)
        should_drop_database = True
        now = datetime.now(UTC)
        work_item = WorkItemRecord(
            work_item_id=SMOKE_WORK_ITEM_ID,
            task_key="graphiti-preflight-smoke",
            title="Graphiti preflight smoke",
            objective="Validate Mongo-backed Graphiti preflight through shared CLI",
            branch="main",
            owner_cli=actor_cli,
            status="dispatched",
            allowed_paths=["scripts/runtime", "src/services/maestro/collab"],
            forbidden_paths=[],
            acceptance_checks=[],
            openspec=None,
            created_at=now,
            updated_at=now,
        )
        service.upsert_work_item(ActorIdentity(cli_name="main", role="main_cli"), work_item)

        command = ["--mongo-uri", effective_mongo_uri, "--mongo-db", db_name]
        command.extend(
            [
                "graphiti",
                "preflight",
                "--work-item-id",
                SMOKE_WORK_ITEM_ID,
                "--actor-cli",
                actor_cli,
                "--write-memory",
                "--max-wait-seconds",
                str(max_wait_seconds),
                "--output",
                "json",
            ]
        )
        payload = _run_coordctl_json(command)

        return {
            "db_name": db_name,
            "work_item_id": SMOKE_WORK_ITEM_ID,
            "actor_cli": actor_cli,
            "server_status": payload.get("server_status"),
            "ingest_status": payload.get("ingest_status"),
            "search_outcome": payload.get("search_outcome"),
            "search_summary": payload.get("search_summary"),
            "episode_uuid": payload.get("episode_uuid"),
        }
    finally:
        try:
            if should_drop_database:
                client.drop_database(db_name)
        finally:
            client.close()


def _build_mongo_client(mongo_uri: str | None) -> MongoClient:
    if mongo_uri:
        return MongoClient(mongo_uri)
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    return MongoClient(**get_mongo_connection_kwargs(server_selection_timeout_ms=3000))


def _resolve_effective_mongo_uri(mongo_uri: str | None) -> str:
    if mongo_uri:
        return mongo_uri
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    return build_mongo_connection_uri()


def _run_coordctl_json(argv: list[str]) -> dict[str, object]:
    command_prefix = os.getenv("GRAPHITI_SMOKE_COMMAND")
    if command_prefix:
        command = [*shlex.split(command_prefix), *argv]
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = completed.stdout.strip()
        if not payload:
            raise RuntimeError(f"external smoke command returned no output for argv={argv!r}")
        return json.loads(payload)

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = coordctl.main(argv)
    if exit_code != 0:
        raise RuntimeError(f"coordctl failed for argv={argv!r}")
    payload = buffer.getvalue().strip()
    if not payload:
        raise RuntimeError(f"coordctl returned no output for argv={argv!r}")
    return json.loads(payload)


if __name__ == "__main__":
    raise SystemExit(main())
