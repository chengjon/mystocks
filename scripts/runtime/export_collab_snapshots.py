from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from pymongo import MongoClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.maestro.collab.backends.mongo.store import MongoCollaborationStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export Mongo collaboration work items as markdown snapshots.")
    parser.add_argument("--mongo-uri", default="mongodb://localhost:27017")
    parser.add_argument("--mongo-db", default="mystocks_coord")
    parser.add_argument("--output-dir", default="reports/governance/mongo-collab-snapshots")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    database = MongoClient(args.mongo_uri)[args.mongo_db]
    output_dir = Path(args.output_dir)
    written_paths = export_work_item_snapshots(database=database, output_dir=output_dir)
    for path in written_paths:
        print(path)
    return 0


def export_work_item_snapshots(*, database: Any, output_dir: Path) -> list[Path]:
    store = MongoCollaborationStore(database)
    output_dir.mkdir(parents=True, exist_ok=True)
    written_paths: list[Path] = []

    for work_item in store.list_work_items():
        updates = store.list_work_updates(work_item.work_item_id)
        requests = store.list_work_requests(work_item.work_item_id)
        content = render_work_item_snapshot(
            work_item=work_item.model_dump(mode="json"),
            updates=[update.model_dump(mode="json") for update in updates],
            requests=[request.model_dump(mode="json") for request in requests],
        )
        snapshot_path = output_dir / f"{work_item.work_item_id}.md"
        snapshot_path.write_text(content, encoding="utf-8")
        written_paths.append(snapshot_path)

    return written_paths


def render_work_item_snapshot(*, work_item: dict[str, Any], updates: list[dict[str, Any]], requests: list[dict[str, Any]]) -> str:
    lines = [
        f"# {work_item['work_item_id']}",
        "",
        f"- Title: {work_item['title']}",
        f"- Objective: {work_item['objective']}",
        f"- Branch: {work_item['branch']}",
        f"- Owner CLI: {work_item['owner_cli']}",
        f"- Status: {work_item['status']}",
        "",
        "## Updates",
    ]

    if updates:
        for update in updates:
            lines.append(f"- [{update['status']}] {update['summary']}")
    else:
        lines.append("- (none)")

    lines.extend(["", "## Requests"])
    if requests:
        for request in requests:
            lines.append(f"- [{request['status']}] {request['request_type']}: {request['summary']}")
    else:
        lines.append("- (none)")

    lines.append("")
    return "\n".join(lines)


def render_task_markdown(*, work_item: dict[str, Any], status_view: dict[str, Any] | None = None) -> str:
    allowed_paths = work_item.get("allowed_paths", [])
    forbidden_paths = work_item.get("forbidden_paths", [])
    acceptance_checks = work_item.get("acceptance_checks", [])
    openspec = work_item.get("openspec")
    tracker_state = status_view["status"] if status_view else work_item["status"]

    lines = [
        "# TASK",
        "",
        "> Exported from Mongo control plane. Do not treat this file as the primary editable task source.",
        "",
        f"- Issue Identifier: `{work_item['work_item_id']}`",
        f"- Issue Title: `{work_item['title']}`",
        f"- Objective: `{work_item['objective']}`",
        f"- Branch: `{work_item['branch']}`",
        f"- Assigned Worker CLI: `{work_item['owner_cli']}`",
        f"- Tracker State: `{tracker_state}`",
        "",
        "## Allowed Paths",
    ]

    if allowed_paths:
        lines.extend(f"- `{path}`" for path in allowed_paths)
    else:
        lines.append("- (none)")

    lines.extend(["", "## Forbidden Paths"])
    if forbidden_paths:
        lines.extend(f"- `{path}`" for path in forbidden_paths)
    else:
        lines.append("- (none)")

    lines.extend(["", "## Acceptance Checks"])
    if acceptance_checks:
        lines.extend(f"- `{check}`" for check in acceptance_checks)
    else:
        lines.append("- (none)")

    lines.extend(["", "## OpenSpec"])
    if openspec:
        lines.append(f"- `{json.dumps(openspec, ensure_ascii=False, sort_keys=True)}`")
    else:
        lines.append("- (none)")

    lines.append("")
    return "\n".join(lines)


def render_task_report_markdown(
    *,
    work_item: dict[str, Any],
    updates: list[dict[str, Any]],
    requests: list[dict[str, Any]],
    status_view: dict[str, Any] | None = None,
    events: list[dict[str, Any]] | None = None,
) -> str:
    current_status = status_view["status"] if status_view else work_item["status"]
    latest_progress = status_view.get("latest_update") if status_view else None
    pending_request = status_view["has_pending_request"] if status_view else "(unknown)"
    graphiti_projection = _extract_graphiti_projection(events or [])

    lines = [
        "# TASK-REPORT",
        "",
        "> Exported from Mongo control plane. Human notes may be appended, but active state lives in Mongo.",
        "",
        f"- Issue Identifier: `{work_item['work_item_id']}`",
        f"- Issue Title: `{work_item['title']}`",
        f"- Assigned Worker CLI: `{work_item['owner_cli']}`",
        f"- Current Status: `{current_status}`",
        f"- Latest Progress: {latest_progress or '(none)'}",
        f"- Pending Request: `{pending_request}`",
        "",
        "## Updates",
    ]

    if updates:
        for update in updates:
            lines.append(
                f"- `{update['created_at']}` [{update['status']}] {update['actor_cli']}: {update['summary']}"
            )
    else:
        lines.append("- (none)")

    lines.extend(["", "## Requests"])
    if requests:
        for request in requests:
            lines.append(
                f"- `{request['created_at']}` [{request['status']}] {request['request_type']} by {request['actor_cli']}: {request['summary']}"
            )
    else:
        lines.append("- (none)")

    lines.extend(
        [
            "",
            "## Graphiti",
            "",
            f"- server_status: `{graphiti_projection['server_status']}`",
            f"- ingest_status: `{graphiti_projection['ingest_status']}`",
            f"- search_summary: `{graphiti_projection['search_summary']}`",
        ]
    )

    lines.append("")
    return "\n".join(lines)


def _extract_graphiti_projection(events: list[dict[str, Any]]) -> dict[str, str]:
    latest_event: dict[str, Any] | None = None
    for event in events:
        if event.get("event_type") != "automation.graphiti_preflight_checked":
            continue
        latest_event = event

    if latest_event is None:
        return {
            "server_status": "(none)",
            "ingest_status": "(none)",
            "search_summary": "(none)",
        }

    payload = latest_event.get("payload", {})
    return {
        "server_status": str(payload.get("server_status", "(none)")),
        "ingest_status": str(payload.get("ingest_status", "(none)")),
        "search_summary": str(payload.get("search_summary", "(none)")),
    }


if __name__ == "__main__":
    raise SystemExit(main())
