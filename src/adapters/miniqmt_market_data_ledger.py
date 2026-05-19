from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EvidenceRunResult:
    status: str
    dataset_version: str
    row_count: int
    field_mapping_version: str
    evidence_path: Path
    raw_report_path: Path
    evidence_sha256: str
    raw_report_sha256: str
    raw_report_size: int


@dataclass(frozen=True)
class MarketDatasetEvidenceRecord:
    evidence_key: str
    evidence_type: str
    dataset_version: str
    lineage_id: str
    payload_hash: str
    rows_hash: str
    artifact_hash: str
    artifact_type: str
    artifact_uri: str
    schema_version: str
    quality_status: str
    maturity: str
    field_mapping_version: str
    row_count: int
    sample_compare_summary: dict[str, Any]
    dry_run_status: str
    result_summary: dict[str, Any]
    raw_report_sha256: str
    evidence_json_sha256: str
    raw_source_file: str
    source_command: str
    environment_summary: dict[str, Any]
    consumer_build: dict[str, Any]
    related_function_tree_node: str
    retention_decision: str

    @classmethod
    def from_run_result(
        cls,
        result: EvidenceRunResult,
        *,
        evidence: dict[str, Any],
        raw_report: dict[str, Any],
    ) -> "MarketDatasetEvidenceRecord":
        dataset = raw_report.get("dataset") or {}
        artifact = raw_report.get("artifact") or {}
        dry_run = raw_report.get("dry_run") or {}
        return cls(
            evidence_key=str(evidence["evidence_key"]),
            evidence_type=str(evidence["evidence_type"]),
            dataset_version=result.dataset_version,
            lineage_id=str(evidence["lineage_id"]),
            payload_hash=str(evidence["payload_hash"]),
            rows_hash=str(dataset["rows_hash"]),
            artifact_hash=str(artifact["hash"]),
            artifact_type=str(artifact["type"]),
            artifact_uri=str(artifact["uri"]),
            schema_version=str(dataset["schema_version"]),
            quality_status=str(dataset["quality_status"]),
            maturity=str(dataset["maturity"]),
            field_mapping_version=result.field_mapping_version,
            row_count=result.row_count,
            sample_compare_summary=dict(dry_run.get("comparison_summary") or {}),
            dry_run_status=result.status,
            result_summary=dict(evidence["result_summary"]),
            raw_report_sha256=result.raw_report_sha256,
            evidence_json_sha256=result.evidence_sha256,
            raw_source_file=str(evidence["raw_source_file"]),
            source_command=str(evidence["source_command"]),
            environment_summary=dict(evidence.get("environment") or {}),
            consumer_build=dict(evidence.get("consumer_build") or {}),
            related_function_tree_node=str(evidence["related_function_tree_node"]),
            retention_decision=str(evidence["retention_decision"]),
        )


class MarketDatasetEvidenceLedger:
    """Persist MyStocks-side controlled evidence metadata through a DB-API connection."""

    INSERT_SQL = """
        INSERT INTO market_dataset_evidence_runs (
            evidence_key,
            evidence_type,
            dataset_version,
            lineage_id,
            payload_hash,
            rows_hash,
            artifact_hash,
            artifact_type,
            artifact_uri,
            schema_version,
            quality_status,
            maturity,
            field_mapping_version,
            row_count,
            sample_compare_summary,
            dry_run_status,
            result_summary,
            raw_report_sha256,
            evidence_json_sha256,
            raw_source_file,
            source_command,
            environment_summary,
            consumer_build,
            related_function_tree_node,
            retention_decision
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s::jsonb,
            %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s
        )
        ON CONFLICT (dataset_version, evidence_key, evidence_type) DO UPDATE SET
            lineage_id = EXCLUDED.lineage_id,
            payload_hash = EXCLUDED.payload_hash,
            rows_hash = EXCLUDED.rows_hash,
            artifact_hash = EXCLUDED.artifact_hash,
            artifact_type = EXCLUDED.artifact_type,
            artifact_uri = EXCLUDED.artifact_uri,
            schema_version = EXCLUDED.schema_version,
            quality_status = EXCLUDED.quality_status,
            maturity = EXCLUDED.maturity,
            field_mapping_version = EXCLUDED.field_mapping_version,
            row_count = EXCLUDED.row_count,
            sample_compare_summary = EXCLUDED.sample_compare_summary,
            dry_run_status = EXCLUDED.dry_run_status,
            result_summary = EXCLUDED.result_summary,
            raw_report_sha256 = EXCLUDED.raw_report_sha256,
            evidence_json_sha256 = EXCLUDED.evidence_json_sha256,
            raw_source_file = EXCLUDED.raw_source_file,
            source_command = EXCLUDED.source_command,
            environment_summary = EXCLUDED.environment_summary,
            consumer_build = EXCLUDED.consumer_build,
            related_function_tree_node = EXCLUDED.related_function_tree_node,
            retention_decision = EXCLUDED.retention_decision,
            updated_at = NOW()
        RETURNING id
    """

    UPDATE_MINIQMT_STATUS_SQL = """
        UPDATE market_dataset_evidence_runs
        SET
            miniqmt_validation_status = %s,
            miniqmt_preview_status = %s,
            miniqmt_apply_status = %s,
            operator_notes = %s,
            updated_at = NOW()
        WHERE dataset_version = %s
          AND evidence_key = %s
          AND evidence_type = %s
        RETURNING id
    """

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def insert_run(self, record: MarketDatasetEvidenceRecord) -> int | None:
        params = (
            record.evidence_key,
            record.evidence_type,
            record.dataset_version,
            record.lineage_id,
            record.payload_hash,
            record.rows_hash,
            record.artifact_hash,
            record.artifact_type,
            record.artifact_uri,
            record.schema_version,
            record.quality_status,
            record.maturity,
            record.field_mapping_version,
            record.row_count,
            json.dumps(record.sample_compare_summary, ensure_ascii=False, sort_keys=True),
            record.dry_run_status,
            json.dumps(record.result_summary, ensure_ascii=False, sort_keys=True),
            record.raw_report_sha256,
            record.evidence_json_sha256,
            record.raw_source_file,
            record.source_command,
            json.dumps(record.environment_summary, ensure_ascii=False, sort_keys=True),
            json.dumps(record.consumer_build, ensure_ascii=False, sort_keys=True),
            record.related_function_tree_node,
            record.retention_decision,
        )
        cursor = self.connection.cursor()
        cursor.execute(self.INSERT_SQL, params)
        row = cursor.fetchone()
        self.connection.commit()
        return int(row[0]) if row else None

    def update_miniqmt_status(
        self,
        *,
        dataset_version: str,
        evidence_key: str,
        evidence_type: str,
        validation_status: str,
        preview_status: str,
        apply_status: str,
        operator_notes: str | None = None,
    ) -> int | None:
        params = (
            validation_status,
            preview_status,
            apply_status,
            operator_notes,
            dataset_version,
            evidence_key,
            evidence_type,
        )
        cursor = self.connection.cursor()
        cursor.execute(self.UPDATE_MINIQMT_STATUS_SQL, params)
        row = cursor.fetchone()
        self.connection.commit()
        return int(row[0]) if row else None
