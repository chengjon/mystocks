from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from pymongo.errors import OperationFailure


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.maestro.collab.backends.mongo.store import MongoCollaborationStore
from src.services.maestro.collab.runtime_registry import MongoCollaborationRegistry
from src.services.maestro.collab.store.models import WorkItemRecord, WorkUpdateRecord
from src.utils.cli_error_output import print_cli_error
from src.utils.mongo_runtime_config import (
    build_mongo_auth_runtime_error,
    build_runtime_mongo_client,
    get_runtime_mongo_db_default,
    get_runtime_mongo_uri_default,
    is_mongo_auth_error,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Migrate SQLite collab runtime state into MongoDB.")
    parser.add_argument("--sqlite-path", default=".symphony/tracker.db")
    parser.add_argument("--mongo-uri", default=get_runtime_mongo_uri_default("mongodb://localhost:27017"))
    parser.add_argument("--mongo-db", default=get_runtime_mongo_db_default("mystocks_coord"))
    parser.add_argument("--task-path", default=None)
    parser.add_argument("--report-path", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        mongo_database = build_runtime_mongo_client(args.mongo_uri)[args.mongo_db]
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
    except OperationFailure as exc:
        if is_mongo_auth_error(exc):
            print_cli_error(build_mongo_auth_runtime_error("Mongo migration"))
            return 1
        raise
    except RuntimeError as exc:
        print_cli_error(exc)
        return 1


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
        ),
    )

    work_updates = 0
    legacy_updates = _extract_legacy_work_updates(
        report_text,
        work_item_id=work_item_id,
        default_actor_cli=owner_cli,
    )
    if legacy_updates:
        for update in legacy_updates:
            store.append_work_update(update)
        work_updates = len(legacy_updates)
    elif latest_progress:
        store.append_work_update(
            WorkUpdateRecord(
                work_item_id=work_item_id,
                update_id=f"import-{work_item_id.lower()}",
                actor_cli=owner_cli,
                status="imported",
                summary=latest_progress,
                details={},
                created_at=now,
            ),
        )
        work_updates = 1

    return {"work_items": 1, "work_updates": work_updates}


def _extract_legacy_work_updates(markdown: str, *, work_item_id: str, default_actor_cli: str) -> list[WorkUpdateRecord]:
    matches = list(re.finditer(r"^## \[WORK\] (?P<heading>.+)$", markdown, flags=re.MULTILINE))
    updates: list[WorkUpdateRecord] = []

    for index, match in enumerate(matches):
        heading = match.group("heading").strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        body = markdown[start:end]
        parsed_heading = _parse_legacy_work_heading(heading, default_actor_cli=default_actor_cli)
        if parsed_heading is None:
            continue

        summary, actor_cli, created_at = parsed_heading
        details = _parse_legacy_work_details(body)
        updates.append(
            WorkUpdateRecord(
                work_item_id=work_item_id,
                update_id=_build_legacy_update_id(
                    work_item_id=work_item_id, summary=summary, created_at=created_at, index=index
                ),
                actor_cli=actor_cli,
                status="imported",
                summary=summary,
                details=details,
                created_at=created_at + timedelta(seconds=index),
            ),
        )

    return updates


def _parse_legacy_work_heading(heading: str, *, default_actor_cli: str) -> tuple[str, str, datetime] | None:
    actor_cli = default_actor_cli
    heading_without_actor = heading.strip()
    actor_match = re.match(r"(?P<value>.+?)（(?P<actor>[^）]+)）$", heading_without_actor)
    if actor_match:
        heading_without_actor = actor_match.group("value").strip()
        actor_cli = actor_match.group("actor").strip() or default_actor_cli

    date_match = re.match(r"(?P<date>\d{4}-\d{2}-\d{2})(?:\s+(?P<title>.+))?$", heading_without_actor)
    if date_match is None:
        return None

    created_at = datetime.fromisoformat(f"{date_match.group('date')}T00:00:00+00:00").astimezone(UTC)
    summary = (date_match.group("title") or heading_without_actor).strip()
    return summary, actor_cli, created_at


def _parse_legacy_work_details(body: str) -> dict[str, Any]:
    details: dict[str, Any] = {}
    current_label: str | None = None
    current_key: str | None = None
    current_inline: str | None = None
    current_lines: list[str] = []

    def flush_current() -> None:
        nonlocal current_label, current_key, current_inline, current_lines
        if current_label is None:
            return
        items = _parse_legacy_section_items(current_lines, inline_value=current_inline)
        if items:
            key = current_key or "notes"
            if key == "notes" and current_key is None:
                items = [f"{current_label}:"] + items
            details.setdefault(key, []).extend(items)
        current_label = None
        current_key = None
        current_inline = None
        current_lines = []

    for raw_line in body.splitlines():
        if match := re.match(r"^- (?P<label>[^:：]+)[:：]\s*(?P<inline>.*)$", raw_line):
            candidate_label = match.group("label").strip()
            candidate_key = _map_legacy_detail_key(candidate_label)
            candidate_inline = match.group("inline").strip()
            if candidate_key is not None or candidate_inline == "":
                flush_current()
                current_label = candidate_label
                current_key = candidate_key
                current_inline = candidate_inline or None
                continue

        if match := re.match(r"^### (?P<label>.+?)\s*$", raw_line):
            flush_current()
            current_label = match.group("label").strip()
            current_key = _map_legacy_detail_key(current_label)
            current_inline = None
            continue

        current_lines.append(raw_line)

    flush_current()
    _rebalance_nested_status_sections(details)
    return details


def _parse_legacy_section_items(lines: list[str], *, inline_value: str | None = None) -> list[str]:
    items: list[str] = []
    if inline_value:
        items.append(inline_value)

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
            continue
        if stripped.startswith("* "):
            items.append(stripped[2:].strip())
            continue
        items.append(stripped)

    return items


def _map_legacy_detail_key(label: str) -> str | None:
    normalized = re.sub(r"\s+", " ", label.strip().lower())
    return {
        "scope": "scope",
        "root cause": "root_cause",
        "completed": "completed",
        "implemented fixes": "completed",
        "verification evidence": "verification_evidence",
        "verification update": "verification_evidence",
        "quality gate": "quality_gate",
        "current status": "current_status",
        "next": "next",
        "artifacts": "artifacts",
        "notes": "notes",
        "additional observation": "notes",
        "additional observations": "notes",
        "说明": "notes",
    }.get(normalized)


def _build_legacy_update_id(*, work_item_id: str, summary: str, created_at: datetime, index: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", summary.lower()).strip("-")
    if not slug:
        slug = f"work-{index + 1}"
    return f"import-{work_item_id.lower()}-{created_at.date().isoformat()}-{index + 1:03d}-{slug}"


def _rebalance_nested_status_sections(details: dict[str, Any]) -> None:
    current_status = details.get("current_status")
    if not isinstance(current_status, list) or not current_status:
        return

    marker_targets = {
        "next:": "next",
        "next：": "next",
        "additional observation:": "notes",
        "additional observation：": "notes",
        "additional observations:": "notes",
        "additional observations：": "notes",
        "说明:": "notes",
        "说明：": "notes",
        "quality gate:": "quality_gate",
        "quality gate：": "quality_gate",
        "质量门禁状态:": "quality_gate",
        "质量门禁状态：": "quality_gate",
    }

    rebalanced: dict[str, list[str]] = {"current_status": []}
    active_target = "current_status"
    for item in current_status:
        target = marker_targets.get(item.strip().lower())
        if target is not None:
            active_target = target
            rebalanced.setdefault(active_target, [])
            continue
        rebalanced.setdefault(active_target, []).append(item)

    if rebalanced["current_status"]:
        details["current_status"] = rebalanced["current_status"]
    else:
        details.pop("current_status", None)

    for key, values in rebalanced.items():
        if key == "current_status" or not values:
            continue
        details[key] = [*details.get(key, []), *values]


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
