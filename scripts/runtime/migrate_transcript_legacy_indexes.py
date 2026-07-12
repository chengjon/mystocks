from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pymongo.errors import OperationFailure


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.maestro.collab.backends.mongo.store import MongoCollaborationStore
from src.services.maestro.collab.store.models import TranscriptLegacyIndexRecord
from src.utils.cli_error_output import print_cli_error
from src.utils.mongo_runtime_config import (
    build_mongo_auth_runtime_error,
    build_runtime_mongo_client,
    get_runtime_mongo_db_default,
    get_runtime_mongo_uri_default,
    is_mongo_auth_error,
)


@dataclass(frozen=True)
class _LegacyTranscriptBlock:
    legacy_block_kind: str
    legacy_session_label: str
    captured_at: datetime
    source_anchor: str
    body: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create legacy transcript indexes from archived markdown artifacts.")
    parser.add_argument("--mongo-uri", default=get_runtime_mongo_uri_default("mongodb://localhost:27017"))
    parser.add_argument("--mongo-db", default=get_runtime_mongo_db_default("mystocks_coord"))
    parser.add_argument("--artifact-path", action="append", required=True)
    parser.add_argument("--migration-batch-id", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        mongo_database = build_runtime_mongo_client(args.mongo_uri)[args.mongo_db]
        counts = migrate_legacy_transcript_indexes(
            artifact_paths=[Path(path) for path in args.artifact_path],
            mongo_database=mongo_database,
            migration_batch_id=args.migration_batch_id,
        )
        print(json.dumps(counts, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except OperationFailure as exc:
        if is_mongo_auth_error(exc):
            print_cli_error(build_mongo_auth_runtime_error("Mongo legacy transcript migration"))
            return 1
        raise
    except RuntimeError as exc:
        print_cli_error(exc)
        return 1


def migrate_legacy_transcript_indexes(
    *,
    artifact_paths: list[Path],
    mongo_database: Any,
    migration_batch_id: str,
) -> dict[str, int]:
    store = MongoCollaborationStore(mongo_database)
    counts = {
        "legacy_indexes": 0,
        "artifacts_scanned": 0,
        "skipped_missing_work_item": 0,
    }

    for artifact_path in artifact_paths:
        counts["artifacts_scanned"] += 1
        markdown = artifact_path.read_text(encoding="utf-8")
        work_item_id = _extract_backticked_value(markdown, "Issue Identifier")
        if not work_item_id or store.get_work_item(work_item_id) is None:
            counts["skipped_missing_work_item"] += 1
            continue

        blocks = _extract_legacy_transcript_blocks(markdown)
        existing_ids = {record.legacy_index_id for record in store.list_transcript_legacy_indexes(work_item_id)}
        for index, block in enumerate(blocks, start=1):
            legacy_index_id = _build_legacy_index_id(
                work_item_id=work_item_id,
                source_artifact=artifact_path,
                source_anchor=block.source_anchor,
                block_kind=block.legacy_block_kind,
                index=index,
            )
            if legacy_index_id in existing_ids:
                continue
            store.append_transcript_legacy_index(
                TranscriptLegacyIndexRecord(
                    legacy_index_id=legacy_index_id,
                    work_item_id=work_item_id,
                    source_artifact=str(artifact_path),
                    legacy_block_kind=block.legacy_block_kind,
                    legacy_session_label=block.legacy_session_label,
                    captured_at=block.captured_at,
                    source_anchor=block.source_anchor,
                    archive_locator=f"{artifact_path}#{block.source_anchor}",
                    checksum=f"sha256:{hashlib.sha256(block.body.encode('utf-8')).hexdigest()}",
                    migration_batch_id=migration_batch_id,
                    migration_recorded_at=datetime.now(UTC),
                ),
            )
            existing_ids.add(legacy_index_id)
            counts["legacy_indexes"] += 1

    return counts


def _extract_legacy_transcript_blocks(markdown: str) -> list[_LegacyTranscriptBlock]:
    matches = list(
        re.finditer(r"^(?P<level>##+)\s+(?P<heading>(?P<kind>AUTO|MANUAL)\b[^\n]*)$", markdown, flags=re.MULTILINE),
    )
    blocks: list[_LegacyTranscriptBlock] = []

    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        heading = match.group("heading").strip()
        kind = match.group("kind").strip()
        body = markdown[start:end].strip()
        if not body:
            continue
        line_no = markdown[: match.start()].count("\n") + 1
        blocks.append(
            _LegacyTranscriptBlock(
                legacy_block_kind=kind,
                legacy_session_label=heading,
                captured_at=_extract_datetime_from_heading(heading),
                source_anchor=f"L{line_no}",
                body=body,
            ),
        )

    return blocks


def _extract_datetime_from_heading(heading: str) -> datetime:
    if match := re.search(r"(?P<date>\d{4}-\d{2}-\d{2})", heading):
        return datetime.fromisoformat(f"{match.group('date')}T00:00:00+00:00").astimezone(UTC)
    return datetime.now(UTC)


def _extract_backticked_value(markdown: str, label: str) -> str | None:
    pattern = rf"- {re.escape(label)}:\s*`([^`]+)`"
    match = re.search(pattern, markdown)
    return match.group(1).strip() if match else None


def _build_legacy_index_id(
    *,
    work_item_id: str,
    source_artifact: Path,
    source_anchor: str,
    block_kind: str,
    index: int,
) -> str:
    digest = hashlib.sha1(f"{source_artifact}:{source_anchor}:{block_kind}:{index}".encode()).hexdigest()[:12]
    return f"legacy-{work_item_id.lower()}-{block_kind.lower()}-{digest}"


if __name__ == "__main__":
    raise SystemExit(main())
