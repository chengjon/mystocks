## 1. Contract And Fixtures

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [x] 1.1 Add a fixture bundle that mirrors the upstream promotion bundle layout, including `bundle_manifest.json` and the required evidence template/request/validator files.
- [x] 1.2 Add fixture manifest and artifact data for `kline_daily` with deterministic hashes.
- [x] 1.3 Add tests proving `dataset_version` is required and `latest` is rejected.
- [x] 1.4 Add tests proving manifest identity fields are mandatory.
- [x] 1.5 Add tests proving raw/candidate/job artifact paths are rejected.

## 2. Release Client And Artifact Verification

- [x] 2.1 Implement the miniQMT Market Data Platform release client in bundle/fixture mode.
- [x] 2.2 Add HTTP mode interfaces without making live HTTP required in unit tests.
- [x] 2.3 Implement artifact selection with Parquet preference and JSON/CSV development fallback.
- [x] 2.4 Implement SHA-256 artifact verification.
- [x] 2.5 Add fail-closed tests for missing artifact, unsupported artifact type, and hash mismatch.
- [x] 2.6 Add local published manifest/artifact pair mode for miniQMT-provided dataset identity and Parquet artifacts.

## 3. Dry-Run Import Rehearsal

- [x] 3.1 Define the `kline_daily` field mapping into MyStocks `DataClassification.DAILY_KLINE`.
- [x] 3.2 Implement dry-run row parsing and mapping without writing formal market-data tables.
- [x] 3.3 Add row count, field mapping version, and sample compare summary output.
- [x] 3.4 Integrate existing data quality checks where they can run without production services.
- [x] 3.5 Add tests proving dry-run reads real rows and fails on empty/template-only runs.
- [x] 3.6 Add Parquet row reading for real miniQMT published dataset artifacts.

## 4. PostgreSQL Evidence Ledger

- [x] 4.1 Add a migration/model for `market_dataset_evidence_runs`.
- [x] 4.2 Persist dataset identity, artifact identity, dry-run result, raw report hash, evidence hash, build metadata, and miniQMT preview/apply status.
- [x] 4.3 Add tests for insert, duplicate dataset/evidence-key handling, and status update behavior.
- [x] 4.4 Document that the ledger is a MyStocks audit record, not a formal market-data import and not the miniQMT promotion registry.

## 5. Evidence JSON Generation

- [x] 5.1 Generate `mystocks_dry_run` `evidence.v1` JSON from real dry-run results.
- [x] 5.2 Include `source_command`, `run_at`, `environment`, `raw_source_file`, `redaction_notes`, `hash_or_size`, `related_function_tree_node`, and `retention_decision`.
- [x] 5.3 Include `consumer_system = "mystocks_spec"` and consumer build commit metadata.
- [x] 5.4 Redact credentials, tokens, account identifiers, full local user paths, raw market rows, and database secrets.
- [x] 5.5 Add tests proving placeholders cannot pass generation.
- [x] 5.6 Add a schema assertion for the evidence JSON shape so `related_function_tree_node` and `hash_or_size` remain mandatory.
- [x] 5.7 Add miniQMT review-aligned evidence audit fields for `result_summary.dry_run`, `environment`, and artifact/raw-report hash summaries.

## 6. CLI And Operator Handoff

- [x] 6.1 Add `scripts/market_data/run_miniqmt_controlled_evidence.py`.
- [x] 6.2 Support `--dataset-version`, `--bundle-path`, `--manifest-url`, `--output-dir`, and dry-run-only database target options.
- [x] 6.3 Print evidence file path, raw report path, hashes, `field_mapping_version`, row count, and pass/fail status.
- [x] 6.4 Document miniQMT operator follow-up: validate evidence, preview apply, then apply to miniQMT registry.
- [x] 6.5 Document that `miniqmt_preview_status` and `miniqmt_apply_status` are updated from explicit operator-supplied miniQMT results, not automatic promotion.
- [x] 6.6 Support `--manifest-path` and `--artifact-path` for miniQMT workspace published dataset handoff.

## 7. Verification

- [x] 7.1 Run focused unit tests for the release client, verifier, dry-run service, ledger, and evidence generator.
- [x] 7.2 Run the CLI against the fixture bundle and store generated evidence under `docs/reports/evidence/miniqmt/`.
- [x] 7.3 Run `openspec validate add-miniqmt-market-data-controlled-evidence-consumer --strict`.
- [x] 7.4 Record downstream miniQMT validator, preview, and apply completion for the MyStocks `mystocks_dry_run` raw/candidate evidence.
  - miniQMT commit `05c5788` records MyStocks dry-run evidence acceptance.
  - miniQMT receive-attempt record shows `local validator executed: yes`, `server preview executed: yes`, and `server apply executed: yes`.
  - Applied identity: `payload_hash=61eedd9cd029f6c0a3324b3e66be0d9b83402279cbd0aed75885459822ec13d1` raw/candidate dataset.
- [x] 7.5 Run MyStocks evidence generation against the real miniQMT published dataset manifest/artifact identity and place the generated evidence JSON in the miniQMT `DOCS/xtdata-api/evidence/` handoff path.
- [x] 7.6 Close MyStocks-side implementation scope for the completed raw/candidate `mystocks_dry_run` slot.
- [x] 7.7 Publish a MyStocks closeout report and artifact index so future operators treat the audit snapshot and any later ledger backfill as MyStocks consumer audit only, not miniQMT business-state truth.
- [x] 7.8 Publish a separate external follow-up tracker for Quantix regression, validated forward identity, authoritative-ready governance, and optional ledger backfill.
- [x] 7.9 Refresh local verification on 2026-05-19 and record the result in the closeout report.
  - Focused pytest for `tests/unit/adapters/test_miniqmt_market_data.py` passed with `--no-cov`: 19 passed.
  - Ruff check passed for the release client, CLI, and focused unit tests.
  - OpenSpec strict validation passed.
  - Evidence and raw report hashes still match the operator snapshot, and the raw report still records `writes_performed=false`, `failed_checks=0`, `row_count=2`, `field_mapping_version=miniqmt.kline_daily.v1`, `artifact_sha256_verified=true`, and `placeholder_count=0`.
- [x] 7.10 Publish a reviewer handoff checklist in the closeout report, covering consumer-only scope, raw/candidate identity binding, operator snapshot role, separate Quantix / validated-forward tracks, manual authoritative-ready gate, and focused re-run commands.
- [x] 7.11 Split the consumer audit ledger helpers into `src/adapters/miniqmt_market_data_ledger.py` so the release client/evidence service facade stays below the production Python file-size guardrail while preserving existing public imports.
- [x] 7.12 Sync post-Quantix follow-up state: Quantix validated forward `quantix_regression` evidence is accepted, while MyStocks validated forward `mystocks_dry_run`, miniQMT manual promote to `validated`, and authoritative-ready approval / rollback readiness remain external follow-up tracks.

## 8. External Follow-Up, Not MyStocks Implementation Blockers

- Quantix: real validated forward `quantix_regression` evidence has been accepted by miniQMT validator / preview / apply and is no longer the blocking follow-up.
- MyStocks validated forward identity: generate a separate `mystocks_dry_run` evidence path for `payload_hash=268b62bb0fb0891833ef1998d4993d6531cc6a9d84aaecb911da0cd559d2357e` if authoritative-ready promotion becomes the target.
- miniQMT manual promote: after required evidence is accepted, promote the dataset to `validated` through the miniQMT owner/operator path.
- MyStocks ledger backfill: optional operator-supplied consumer audit snapshot only; not miniQMT promotion-state truth.
- Promotion governance: keep authoritative-ready as an explicit manual gate with rollback/fallback constraints; do not infer source cutover from MyStocks evidence apply.
