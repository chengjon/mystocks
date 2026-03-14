from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pymongo import MongoClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.maestro.collab.runtime_registry import MongoCollaborationRegistry
from src.services.maestro.collab.backends.mongo.store import MongoCollaborationStore
from src.services.maestro.collab.store.models import WorkItemRecord, WorkUpdateRecord


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Migrate SQLite collab runtime state into MongoDB.")
    parser.add_argument("--sqlite-path", default=".symphony/tracker.db")
    parser.add_argument("--mongo-uri", default="mongodb://localhost:27017")
    parser.add_argument("--mongo-db", default="mystocks_coord")
    parser.add_argument("--task-path", default=None)
    parser.add_argument("--report-path", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    mongo_database = MongoClient(args.mongo_uri)[args.mongo_db]
    counts = migrate_runtime_registry(sqlite_path=Path(args.sqlite_path), mongo_database=mongo_database)
    if args.task_path or args.report_path:
        task_counts = migrate_markdown_contract(
            task_path=Path(args.task_path) if args.task_path else Path("TASK.md"),
            report_path=Path(args.report_path) if args.report_path else Path("TASK-REPORT.md"),
            mongo_database=mongo_database,
        )
        counts.update(task_counts)
    print(json.dumps(counts, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def migrate_runtime_registry(*, sqlite_path: Path, mongo_database: Any) -> dict[str, int]:
    registry = MongoCollaborationRegistry(mongo_database)
    counts = {"assignments": 0, "workspaces": 0, "heartbeats": 0}

    with sqlite3.connect(sqlite_path) as connection:
        connection.row_factory = sqlite3.Row
        if _table_exists(connection, "issue_assignments"):
            for row in connection.execute("SELECT * FROM issue_assignments ORDER BY issue_identifier ASC").fetchall():
                registry._assignments.replace_one(  # noqa: SLF001
                    {"issue_identifier": str(row["issue_identifier"])},
                    dict(row),
                    upsert=True,
                )
                counts["assignments"] += 1

        if _table_exists(connection, "worktree_registry"):
            for row in connection.execute("SELECT * FROM worktree_registry ORDER BY issue_identifier ASC").fetchall():
                registry._workspaces.replace_one(  # noqa: SLF001
                    {"issue_identifier": str(row["issue_identifier"])},
                    dict(row),
                    upsert=True,
                )
                counts["workspaces"] += 1

        if _table_exists(connection, "worker_heartbeats"):
            for row in connection.execute("SELECT * FROM worker_heartbeats ORDER BY issue_identifier ASC").fetchall():
                registry._heartbeats.replace_one(  # noqa: SLF001
                    {"issue_identifier": str(row["issue_identifier"])},
                    dict(row),
                    upsert=True,
                )
                counts["heartbeats"] += 1

    return counts


def migrate_markdown_contract(*, task_path: Path, report_path: Path, mongo_database: Any) -> dict[str, int]:
    task_text = task_path.read_text(encoding="utf-8") if task_path.exists() else ""
    report_text = report_path.read_text(encoding="utf-8") if report_path.exists() else ""

    work_item_id = _extract_backticked_value(task_text, "Issue Identifier")
    if not work_item_id:
        return {"work_items": 0, "work_updates": 0}

    title = _extract_backticked_value(task_text, "Issue Title") or work_item_id
    owner_cli = _extract_backticked_value(task_text, "Assigned Worker CLI") or "main"
    acceptance_summary = _extract_backticked_value(task_text, "Acceptance Summary")
    latest_progress = _extract_plain_value(report_text, "Latest Progress")
    now = datetime.now(UTC)

    store = MongoCollaborationStore(mongo_database)
    store.upsert_work_item(
        WorkItemRecord(
            work_item_id=work_item_id,
            task_key=work_item_id.lower(),
            title=title,
            objective=acceptance_summary or title,
            branch="",
            owner_cli=owner_cli,
            status="imported",
            allowed_paths=[],
            forbidden_paths=[],
            acceptance_checks=[acceptance_summary] if acceptance_summary else [],
            openspec=None,
            created_at=now,
            updated_at=now,
        )
    )

    work_updates = 0
    if latest_progress:
        store.append_work_update(
            WorkUpdateRecord(
                work_item_id=work_item_id,
                update_id=f"import-{work_item_id.lower()}",
                actor_cli=owner_cli,
                status="imported",
                summary=latest_progress,
                details={},
                created_at=now,
            )
        )
        work_updates = 1

    return {"work_items": 1, "work_updates": work_updates}


def _extract_backticked_value(markdown: str, label: str) -> str | None:
    pattern = rf"- {re.escape(label)}:\s*`([^`]+)`"
    match = re.search(pattern, markdown)
    return match.group(1).strip() if match else None


def _extract_plain_value(markdown: str, label: str) -> str | None:
    pattern = rf"- {re.escape(label)}:\s*(.+)"
    match = re.search(pattern, markdown)
    return match.group(1).strip() if match else None


def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    row = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


if __name__ == "__main__":
    raise SystemExit(main())
