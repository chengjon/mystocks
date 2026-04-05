from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from pymongo.errors import OperationFailure

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.maestro.collab.backends.mongo.store import MongoCollaborationStore
from src.utils.cli_error_output import print_cli_error
from src.utils.mongo_runtime_config import (
    build_mongo_auth_runtime_error,
    build_runtime_mongo_client,
    get_runtime_mongo_db_default,
    get_runtime_mongo_uri_default,
    is_mongo_auth_error,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export Mongo collaboration work items as markdown snapshots.")
    parser.add_argument("--mongo-uri", default=get_runtime_mongo_uri_default("mongodb://localhost:27017"))
    parser.add_argument("--mongo-db", default=get_runtime_mongo_db_default("mystocks_coord"))
    parser.add_argument("--output-dir", default="reports/governance/mongo-collab-snapshots")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        database = build_runtime_mongo_client(args.mongo_uri)[args.mongo_db]
        output_dir = Path(args.output_dir)
        written_paths = export_work_item_snapshots(database=database, output_dir=output_dir)
        for path in written_paths:
            print(path)
        return 0
    except OperationFailure as exc:
        if is_mongo_auth_error(exc):
            print_cli_error(build_mongo_auth_runtime_error("Mongo export"))
            return 1
        raise
    except RuntimeError as exc:
        print_cli_error(exc)
        return 1


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
    metadata = work_item.get("metadata") or {}
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

    _append_optional_section(lines, "Related Plans", metadata.get("related_plans"))
    _append_owner_decision_section(lines, metadata)
    _append_optional_section(lines, "Scope Paths", metadata.get("scope_paths"))
    _append_optional_section(lines, "Validation Commands", metadata.get("validation_commands"))
    _append_optional_section(lines, "Next Steps", metadata.get("next_steps"))
    _append_optional_section(lines, "Blocked Items", metadata.get("blocked_items"))
    _append_optional_section(lines, "Compatibility Notes", metadata.get("compatibility_notes"))
    _append_optional_section(lines, "Rollback Rule", metadata.get("rollback_rule"))
    _append_optional_section(lines, "Artifact Links", metadata.get("artifact_links"))

    lines.append("")
    return "\n".join(lines)


def render_task_report_markdown(
    *,
    work_item: dict[str, Any],
    updates: list[dict[str, Any]],
    requests: list[dict[str, Any]],
    status_view: dict[str, Any] | None = None,
    events: list[dict[str, Any]] | None = None,
    transcripts: list[dict[str, Any]] | None = None,
    graphiti_projection: dict[str, str] | None = None,
) -> str:
    current_status = status_view["status"] if status_view else work_item["status"]
    latest_progress = status_view.get("latest_update") if status_view else None
    pending_request = status_view["has_pending_request"] if status_view else "(unknown)"
    graphiti_projection = graphiti_projection or _extract_graphiti_projection(events or [])

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

    if transcripts:
        lines.extend(["", "## Transcripts"])
        for transcript in transcripts:
            session_label = transcript.get("session_id") or transcript.get("legacy_session_label") or "(unknown)"
            actor_cli = transcript.get("actor_cli") or "(legacy)"
            transcript_kind = transcript.get("transcript_kind") or transcript.get("legacy_block_kind") or "(unknown)"
            started_at = transcript.get("started_at") or transcript.get("captured_at") or "(unknown)"
            hot_body_available = "yes" if transcript.get("hot_body_available") else "no"
            archive_locator = transcript.get("archive_locator") or transcript.get("archive_ref") or "(none)"
            source = transcript.get("source", "ledger")
            lines.append(
                f"- `{session_label}` | source=`{source}` | actor=`{actor_cli}` | kind=`{transcript_kind}` | started=`{started_at}` | hot_body=`{hot_body_available}` | archive_ref=`{archive_locator}`"
            )

    detailed_updates = [update for update in updates if _has_structured_report_details(update.get("details"))]
    if detailed_updates:
        lines.extend(["", "## Detailed Updates"])
        for update in detailed_updates:
            lines.extend(
                [
                    "",
                    f"### `{update['created_at']}` [{update['status']}] {update['actor_cli']}",
                    f"- Summary: {update['summary']}",
                ]
            )
            details = update.get("details") or {}
            _append_optional_section(lines, "Scope", details.get("scope"), level=4)
            _append_optional_section(lines, "Root Cause", details.get("root_cause"), level=4)
            _append_optional_section(lines, "Completed", details.get("completed"), level=4)
            _append_optional_section(lines, "Verification Evidence", details.get("verification_evidence"), level=4)
            _append_optional_section(lines, "Quality Gate", details.get("quality_gate"), level=4)
            _append_optional_section(lines, "Current Status", details.get("current_status"), level=4)
            _append_optional_section(lines, "Next", details.get("next"), level=4)
            _append_optional_section(lines, "Artifacts", details.get("artifacts"), level=4)
            _append_optional_section(lines, "Notes", details.get("notes"), level=4)

    lines.append("")
    return "\n".join(lines)


def _append_owner_decision_section(lines: list[str], metadata: dict[str, Any]) -> None:
    decision_lines: list[str] = []
    if _has_content(metadata.get("suggested_owner")):
        decision_lines.append(f"- Suggested Owner: `{metadata['suggested_owner']}`")
    if _has_content(metadata.get("final_owner")):
        decision_lines.append(f"- Final Owner: `{metadata['final_owner']}`")
    if _has_content(metadata.get("worker_cli")):
        decision_lines.append(f"- Worker CLI: `{metadata['worker_cli']}`")
    if _has_content(metadata.get("decision_basis")):
        decision_lines.append("- Decision Basis:")
        decision_lines.extend(_render_value_lines(metadata["decision_basis"], indent=1))
    if _has_content(metadata.get("suggest_reasons")):
        decision_lines.append("- Suggest Reasons:")
        decision_lines.extend(_render_value_lines(metadata["suggest_reasons"], indent=1))

    if decision_lines:
        lines.extend(["", "## Owner Decision", *decision_lines])


def _append_optional_section(lines: list[str], title: str, value: Any, *, level: int = 2) -> None:
    if not _has_content(value):
        return
    lines.extend(["", f"{'#' * level} {title}"])
    lines.extend(_render_value_lines(value))


def _render_value_lines(value: Any, *, indent: int = 0) -> list[str]:
    prefix = "  " * indent + "- "

    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            if not _has_content(item):
                continue
            if _is_scalar(item):
                lines.append(f"{prefix}`{key}`: {_format_scalar(item)}")
            else:
                lines.append(f"{prefix}`{key}`:")
                lines.extend(_render_value_lines(item, indent=indent + 1))
        return lines or [prefix + "(none)"]

    if isinstance(value, list):
        lines = []
        for item in value:
            if not _has_content(item):
                continue
            if _is_scalar(item):
                lines.append(prefix + str(item))
            elif isinstance(item, dict):
                summary = item.get("summary")
                if isinstance(summary, str) and summary.strip():
                    lines.append(prefix + summary)
                    remaining = {key: item_value for key, item_value in item.items() if key != "summary"}
                    if remaining:
                        lines.extend(_render_value_lines(remaining, indent=indent + 1))
                else:
                    lines.append(prefix + json.dumps(item, ensure_ascii=False, sort_keys=True))
            else:
                lines.append(prefix + str(item))
        return lines or [prefix + "(none)"]

    return [prefix + _format_scalar(value)]


def _format_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return f"`{value}`"
    if isinstance(value, (int, float)):
        return f"`{value}`"
    return str(value)


def _has_content(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) > 0
    return True


def _is_scalar(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool))


def _has_structured_report_details(details: Any) -> bool:
    if not isinstance(details, dict):
        return False
    return any(
        _has_content(details.get(key))
        for key in (
            "scope",
            "root_cause",
            "completed",
            "verification_evidence",
            "quality_gate",
            "current_status",
            "next",
            "artifacts",
            "notes",
        )
    )


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
