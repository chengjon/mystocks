# Design: miniQMT market-data controlled evidence consumer

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Context

The downstream miniQMT guide at `/mnt/d/MyCode3/miniQMT/DOCS/xtdata-api/2026-05-18-upstream-controlled-evidence-integration-guide.md` defines a Market Data Platform handoff:

- miniQMT owns dataset publish, manifest, lineage, quality, artifact export, evidence slots, validation, promotion preview/apply, registry, and manual maturity promotion.
- MyStocks owns Python adapter/client consumption, release artifact verification, dry-run import rehearsal, sample comparison, field mapping, PostgreSQL/TDengine/Redis import control, and real `mystocks_dry_run` controlled evidence generation.
- miniQMT must not write MyStocks formal stores.
- MyStocks must not consume miniQMT raw/candidate/job internals and must not use implicit `latest`.

The repository already has miniQMT execution-side specs for broker submission and reconciliation. This change is intentionally scoped to Market Data Platform dataset consumption and promotion evidence.

## Goals

- Consume miniQMT Market Data Platform releases through `/api/v1/market-data/*` or an equivalent promotion bundle.
- Bind every run to explicit `dataset_version`, `lineage_id`, `payload_hash`, `rows_hash`, `artifact_hash`, `schema_version`, `quality_status`, and `maturity`.
- Verify release artifact integrity before any dry-run import rehearsal.
- Generate real `mystocks_dry_run` evidence from actual artifact rows and dry-run results.
- Persist MyStocks-side evidence metadata in PostgreSQL for auditability.
- Produce `evidence.v1` JSON that miniQMT can validate, preview, and apply to its promotion evidence registry.
- Match the upstream evidence contract fields that the validator expects, including `related_function_tree_node` and `hash_or_size`.

## Non-Goals

- No automatic formal write into MyStocks market-data tables.
- No automatic maturity promotion in miniQMT.
- No direct dependency on miniQMT raw/candidate/job storage.
- No coupling to miniQMT broker execution bridge runtime.
- No frontend workflow in the first slice.

## Boundary Model

| Capability | miniQMT responsibility | MyStocks responsibility |
|---|---|---|
| Dataset identity | Publish immutable `dataset_version` and hashes | Require explicit identity on every run |
| Manifest/artifact | Expose release manifest and artifact URI/hash | Read only release artifact and verify hash |
| Dry-run import | Not run | Run rehearsal without formal writes |
| Evidence JSON | Validate, preview, apply, and registry-store | Generate real `mystocks_dry_run` evidence |
| MyStocks DB | Never write | Own dry-run ledger and formal write approval |
| Maturity promotion | Manual gate and approval | Provide trusted consumer evidence |

## Proposed Components

### `MiniQmtMarketDataReleaseClient`

Responsibility: retrieve immutable dataset metadata and release manifest/artifact references.

Required behavior:
- Accept explicit `dataset_version`; reject empty values and `latest`.
- Fetch dataset, manifest, maturity, promotion requirements, and promotion gaps when configured for HTTP mode.
- Support bundle mode for offline/fixture testing.
- Select primary release artifact, preferring Parquet, then JSON/CSV only for development slices.
- Return a normalized identity envelope containing dataset and artifact hashes.

### `MiniQmtArtifactVerifier`

Responsibility: verify local or downloaded artifact bytes before rows are parsed.

Required behavior:
- Calculate SHA-256 for the artifact bytes.
- Compare with manifest `artifacts[].hash`.
- Refuse dry-run execution on mismatch.
- Record artifact type, URI, expected hash, actual hash, and verification status.

### `MiniQmtDryRunEvidenceService`

Responsibility: execute the MyStocks-side dry-run and build evidence.

Required behavior:
- Parse artifact rows into a bounded in-memory or temp-file rehearsal pipeline.
- Map fields into MyStocks `DataClassification`, starting with `DAILY_KLINE`.
- Run quality checks and sample comparisons.
- Prove database target is `dry-run-only` for the evidence slice.
- Persist the evidence run metadata to PostgreSQL.
- Generate redacted raw report and `evidence.v1` JSON.
- Support both upstream promotion bundles and miniQMT-published dataset manifests/artifacts so MyStocks can consume a real published dataset identity without copying it into an ad-hoc fixture layout.

### Evidence JSON Shape

The generated evidence should follow the upstream field contract and remain stable enough for direct validator comparison.

```json
{
  "schema_version": "evidence.v1",
  "evidence_key": "mystocks_dry_run",
  "evidence_type": "promotion_consumer_dry_run",
  "consumer_system": "mystocks_spec",
  "dataset_version": "kline_daily_20260518_v1",
  "lineage_id": "lin_kline_daily_20260518_v1",
  "payload_hash": "from_manifest",
  "result_summary": {
    "evidence_type": "promotion_consumer_dry_run",
    "consumer_system": "mystocks_spec",
    "dataset_version": "kline_daily_20260518_v1",
    "lineage_id": "lin_kline_daily_20260518_v1",
    "payload_hash": "from_manifest",
    "row_count": 2,
    "field_mapping_version": "miniqmt.kline_daily.v1",
    "writes_performed": false,
    "dry_run": {
      "passed": true,
      "failed_checks": [],
      "artifact_sha256_verified": true,
      "placeholder_count": 0
    }
  },
  "source_command": "scripts/market_data/run_miniqmt_controlled_evidence.py ...",
  "run_at": "2026-05-18T00:00:00Z",
  "environment": {
    "consumer_system": "mystocks_spec",
    "field_mapping_version": "miniqmt.kline_daily.v1"
  },
  "raw_source_file": "logs/mystocks_dry_run_kline_daily_20260518_v1.json",
  "hash_or_size": {
    "artifact_sha256": "artifact_sha256",
    "raw_report_sha256": "raw_report_sha256",
    "logs/mystocks_dry_run_kline_daily_20260518_v1.json": {
      "sha256": "raw_report_sha256",
      "byte_count": 1234
    }
  },
  "related_function_tree_node": "FUNCTION_TREE.md#8.1 Market Data M1 authoritative-ready 缺口",
  "retention_decision": "keep_minimal_evidence"
}
```

The exact `result_summary` payload can grow over time, but the identity, dry-run audit, hash, and traceability fields above are mandatory.

### Published Dataset Input Mode

When miniQMT provides a published dataset identity directly, the CLI MAY accept `--manifest-path` plus `--artifact-path` to read the manifest and Parquet artifact from the miniQMT workspace without reconstructing a bundle fixture. This mode preserves the upstream `dataset_version`, `lineage_id`, `payload_hash`, `rows_hash`, `quality_status`, `maturity`, and artifact hash values while still producing MyStocks-side `mystocks_dry_run` evidence and the local audit ledger entry.

### PostgreSQL Evidence Ledger

Responsibility: preserve MyStocks-side audit metadata without storing raw market rows or credentials.

Candidate table: `market_dataset_evidence_runs`.

Minimum fields:
- `id`
- `evidence_key`
- `evidence_type`
- `dataset_version`
- `lineage_id`
- `payload_hash`
- `rows_hash`
- `artifact_hash`
- `artifact_type`
- `artifact_uri`
- `schema_version`
- `quality_status`
- `maturity`
- `field_mapping_version`
- `row_count`
- `sample_compare_summary`
- `dry_run_status`
- `result_summary`
- `raw_report_sha256`
- `evidence_json_sha256`
- `consumer_build_repo`
- `consumer_build_commit`
- `source_command`
- `environment_summary`
- `retention_decision`
- `miniqmt_preview_status`
- `miniqmt_apply_status`
- `created_at`
- `updated_at`

The ledger is a consumer audit record. It is not the miniQMT promotion registry and does not imply formal market-data ingestion.
The `miniqmt_preview_status` and `miniqmt_apply_status` columns are informational audit columns in P0; MyStocks updates them from explicit operator-supplied miniQMT validation/preview/apply results, not by automatic promotion.

### Bundle Mode Format

Bundle mode shall accept a directory produced from the upstream promotion bundle workflow, not a loose ad-hoc folder. The bundle is expected to contain the upstream `bundle_manifest.json` plus the promotion-bundle files that miniQMT prepares for MyStocks, including the dataset requirements, gaps, template evidence, request files, validator output, apply output, promotion targets, and README.

In P0 the bundle loader should require the manifest first, then resolve the referenced files from the same directory tree. A bundle missing the manifest or missing any manifest-referenced artifact fails closed.

### CLI

Candidate command:

```bash
python scripts/market_data/run_miniqmt_controlled_evidence.py \
  --dataset-version kline_daily_20260518_v1 \
  --manifest-url http://127.0.0.1:18080/api/v1/market-data/datasets/kline_daily_20260518_v1/manifest \
  --output-dir docs/reports/evidence/miniqmt
```

Required CLI behavior:
- Require `--dataset-version`.
- Reject `latest`.
- Support HTTP mode and bundle/fixture mode.
- Write a redacted raw report and an `evidence.v1` JSON artifact.
- Print only file paths, hashes, row counts, `field_mapping_version`, and pass/fail status.

## P0 Vertical Slice

The first implementation slice SHALL support `kline_daily` only:

1. Fixture/bundle mode for deterministic tests.
2. Manifest identity parsing.
3. Artifact hash verification.
4. `DAILY_KLINE` field mapping report.
5. Dry-run-only import rehearsal.
6. PostgreSQL evidence ledger record.
7. `mystocks_dry_run` `evidence.v1` JSON generation.

HTTP integration with a live miniQMT server is a follow-up once fixture mode proves the contract.

## Fail-Closed Rules

The consumer must fail before dry-run execution when:

- `dataset_version` is missing or equals `latest`.
- manifest identity fields are missing.
- artifact hash verification fails.
- artifact URI points to raw/candidate/job internals instead of a release artifact.
- `quality_status` or `maturity` is outside the accepted dry-run policy.

The consumer must fail evidence generation when:

- no real artifact rows were read.
- dry-run did not execute.
- evidence contains placeholder-only fields.
- `source_command`, `run_at`, `environment`, `raw_source_file`, or `retention_decision` is missing.
- the run wrote to formal MyStocks market-data tables.

## Testing Strategy

- Unit tests for identity parsing, hash verification, fail-closed validation, field mapping, redaction, and evidence JSON schema.
- Integration-style tests with fixture manifest and artifact files.
- Database tests for ledger insert/update behavior using existing PostgreSQL test patterns or a repository-approved temporary database fixture.
- CLI tests that assert no implicit `latest`, deterministic evidence filenames, and redacted output.

## Open Questions

- Whether the P0 fixture artifact should be JSON or Parquet. Parquet matches miniQMT preference, but JSON may be faster for the first deterministic unit slice if the repository lacks a stable Parquet dependency path.
- Whether MyStocks should copy evidence JSON into the miniQMT repo automatically or only emit a path for the operator. The safer P0 default is emit-only.
