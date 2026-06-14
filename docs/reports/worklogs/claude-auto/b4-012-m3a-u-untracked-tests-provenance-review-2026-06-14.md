# B4.012-M3a-U untracked tests provenance review

Date: 2026-06-14
Mode: no-source provenance review, no test/source/runtime cleanup authorization
Parent gate: `b4-012-m3a-tests-residual-domain-audit`

## Scope

This review inventories untracked `tests/**` rows and routes them to future preserve/delete/ignore decisions.

No untracked file is staged, deleted, restored, moved, or accepted by this review.

## Current Untracked Summary

Measured from `git status --porcelain=v1 -- tests` on 2026-06-14.

Untracked status rows: 13.

Expanded filesystem files: 29.

## Provenance Buckets

### Fixture Promotion Bundle

Status row:

- `tests/fixtures/miniqmt_promotion_bundle/`

Expanded files: 17.

- `tests/fixtures/miniqmt_promotion_bundle/kline_daily_20260518_v1/README.md`
- `tests/fixtures/miniqmt_promotion_bundle/kline_daily_20260518_v1/artifacts/kline_daily.json`
- `tests/fixtures/miniqmt_promotion_bundle/kline_daily_20260518_v1/authoritative_approval.apply.txt`
- `tests/fixtures/miniqmt_promotion_bundle/kline_daily_20260518_v1/authoritative_approval.request.json`
- `tests/fixtures/miniqmt_promotion_bundle/kline_daily_20260518_v1/bundle_manifest.json`
- `tests/fixtures/miniqmt_promotion_bundle/kline_daily_20260518_v1/dataset_manifest.json`
- `tests/fixtures/miniqmt_promotion_bundle/kline_daily_20260518_v1/mystocks_dry_run.request.json`
- `tests/fixtures/miniqmt_promotion_bundle/kline_daily_20260518_v1/mystocks_dry_run.template.evidence.json`
- `tests/fixtures/miniqmt_promotion_bundle/kline_daily_20260518_v1/mystocks_dry_run.validator.txt`
- `tests/fixtures/miniqmt_promotion_bundle/kline_daily_20260518_v1/promotion_bundle.apply.txt`
- `tests/fixtures/miniqmt_promotion_bundle/kline_daily_20260518_v1/promotion_bundle.validate.txt`
- `tests/fixtures/miniqmt_promotion_bundle/kline_daily_20260518_v1/promotion_gaps.json`
- `tests/fixtures/miniqmt_promotion_bundle/kline_daily_20260518_v1/promotion_requirements.json`
- `tests/fixtures/miniqmt_promotion_bundle/kline_daily_20260518_v1/promotion_targets.json`
- `tests/fixtures/miniqmt_promotion_bundle/kline_daily_20260518_v1/quantix_regression.request.json`
- `tests/fixtures/miniqmt_promotion_bundle/kline_daily_20260518_v1/quantix_regression.template.evidence.json`
- `tests/fixtures/miniqmt_promotion_bundle/kline_daily_20260518_v1/quantix_regression.validator.txt`

Disposition: high-review fixture/data provenance package. Do not preserve or delete until fixture ownership, data licensing, and miniqmt promotion context are reviewed.

### Contract E2E

- `tests/integration/contract/test_contract_validation_e2e.py`

Disposition: untracked contract E2E candidate. Route to contract/integration provenance before any preserve/delete/ignore decision.

### Performance And Deployment Runtime

- `tests/performance/test_benchmark_workload_classes.py`
- `tests/performance/test_collect_api_performance_baseline.py`
- `tests/performance/test_collect_frontend_runtime_gate.py`
- `tests/performance/test_validate_api_performance_drift.py`
- `tests/performance/test_validate_backend_runtime_dependencies.py`
- `tests/performance/test_validate_container_deployment_contract.py`
- `tests/performance/test_validate_deployment_env_contract.py`

Disposition: route to M3a-EU performance/deployment provenance. These files are not accepted into M3a-E tracked implementation packages until explicitly preserved.

### Data-Source Contract

- `tests/unit/data_source/test_data_source_client_contract.py`

Disposition: route to M3a-C-U data-source provenance before preservation. Do not mix with tracked M3a-C adapter/data-source cleanup.

### Governance Script Tests

- `tests/unit/scripts/test_collect_tech_debt_baseline.py`
- `tests/unit/scripts/test_gitnexus_workflow_gate.py`
- `tests/unit/scripts/test_graphiti_post_commit_hook_integration.py`

Disposition: route to M3a-EU governance-script provenance. These files may be useful governance coverage, but untracked status requires explicit preservation approval.

## Risk

Risk level: high.

Untracked tests can silently change repository behavior if staged without provenance. The fixture bundle also contains data artifacts and approval/request files, so preserve/delete/ignore must be handled as a separate explicit decision.

## Decision

No untracked test files are accepted in this review.

Future actions require separate explicit authorization:

- preserve as tracked tests/fixtures
- delete local untracked artifacts
- add ignore rules
- move to archive or reports

## Non-Goals

- No test edits.
- No source, backend, API, frontend, runtime, OpenSpec, OpenStock, ST-HOLD, or marketKlineData edits.
- No untracked staging.
- No deletion, restore, move, or ignore-rule changes.

## Required Gates For This Review

- exact staged allowlist of governance/report files only
- `git diff --cached --check`
- Function Tree validation
- GitNexus staged verification
- GitNexus staged detect-changes
- OPENDOG blocker check
- post-commit GitNexus index refresh

## Current Status

`source_edits_authorized: false`

This provenance review does not authorize preservation, deletion, ignore rules, or implementation.
