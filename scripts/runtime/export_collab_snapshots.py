from __future__ import annotations

import argparse
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


if __name__ == "__main__":
    raise SystemExit(main())
