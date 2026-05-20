-- MyStocks-side controlled evidence ledger for miniQMT Market Data Platform dry-run rehearsals.
-- This table is a consumer audit ledger. It is not the miniQMT promotion evidence registry.

CREATE TABLE IF NOT EXISTS market_dataset_evidence_runs (
    id BIGSERIAL PRIMARY KEY,
    evidence_key TEXT NOT NULL,
    evidence_type TEXT NOT NULL,
    dataset_version TEXT NOT NULL,
    lineage_id TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    rows_hash TEXT NOT NULL,
    artifact_hash TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    artifact_uri TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    quality_status TEXT NOT NULL,
    maturity TEXT NOT NULL,
    field_mapping_version TEXT NOT NULL,
    row_count INTEGER NOT NULL CHECK (row_count >= 0),
    sample_compare_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    dry_run_status TEXT NOT NULL,
    result_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    raw_report_sha256 TEXT NOT NULL,
    evidence_json_sha256 TEXT NOT NULL,
    raw_source_file TEXT NOT NULL,
    source_command TEXT NOT NULL,
    environment_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    consumer_build JSONB NOT NULL DEFAULT '{}'::jsonb,
    related_function_tree_node TEXT NOT NULL,
    retention_decision TEXT NOT NULL,
    miniqmt_validation_status TEXT NOT NULL DEFAULT 'not_submitted',
    miniqmt_preview_status TEXT NOT NULL DEFAULT 'not_submitted',
    miniqmt_apply_status TEXT NOT NULL DEFAULT 'not_submitted',
    operator_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_market_dataset_evidence_runs_unique_evidence
    ON market_dataset_evidence_runs (dataset_version, evidence_key, evidence_type);

CREATE INDEX IF NOT EXISTS idx_market_dataset_evidence_runs_dataset
    ON market_dataset_evidence_runs (dataset_version, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_market_dataset_evidence_runs_status
    ON market_dataset_evidence_runs (dry_run_status, miniqmt_preview_status, miniqmt_apply_status);
