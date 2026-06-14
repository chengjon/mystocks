# B4.012-M3a-B2 API root file tests authorization prep

Date: 2026-06-14
Mode: no-source authorization preparation, no test/source edits
Parent split: `b4-012-m3a-b-api-backend-contract-tests-split`

## Scope

This package prepares a narrow future authorization boundary for tracked API root file tests only.

The intended batch is intentionally separate from `tests/api/file_tests/**`, backend regression tests, contract-engine tests, security/performance tests, frontend/E2E specs, and untracked test provenance review.

Current no-source status confirms 23 tracked modified candidates:

- `tests/api/test_akshare_market_file.py`
- `tests/api/test_backup_recovery_file.py`
- `tests/api/test_cache_file.py`
- `tests/api/test_data_file.py`
- `tests/api/test_data_quality_file.py`
- `tests/api/test_gpu_monitoring_file.py`
- `tests/api/test_health_file.py`
- `tests/api/test_indicator_registry_file.py`
- `tests/api/test_market_v2_file.py`
- `tests/api/test_metrics_file.py`
- `tests/api/test_ml_file.py`
- `tests/api/test_monitoring_file.py`
- `tests/api/test_multi_source_file.py`
- `tests/api/test_notification_file.py`
- `tests/api/test_prometheus_exporter_file.py`
- `tests/api/test_realtime_market_file.py`
- `tests/api/test_signal_monitoring_file.py`
- `tests/api/test_sse_endpoints_file.py`
- `tests/api/test_stock_search_file.py`
- `tests/api/test_system_file.py`
- `tests/api/test_tasks_file.py`
- `tests/api/test_watchlist_file.py`
- `tests/api/test_websocket_file.py`

All 23 candidates are tracked modified files. No untracked `tests/api/*.py` root file-test candidate is included in this batch.

## Explicit Exclusions

Excluded from this batch:

- `tests/api/file_tests/**`
- `tests/api/file_tests/run_file_tests.py`
- backend regression/risk tests under `tests/backend/**`
- tracked contract-engine tests
- untracked contract/deployment tests
- M3a-A test-infra/helper batch
- M3a-B1 API file_tests authorization batch
- M3a-D frontend/E2E auth specs
- M3a-E security/compliance/performance tests
- M3a-U untracked test provenance review
- any source, runtime, OpenSpec, OpenStock, deletion, restore, or staging action

## Risk

Risk level: medium.

These tests sit near API route and response-contract truth, but this package grants no implementation authority yet. Future source/test work must first receive explicit approval and should verify route registry expectations before accepting or standardizing existing dirty deltas.

## Gate Recommendation

Future implementation authorization, if approved, should allow only the 23 listed test files plus a B2 closeout report. It should require:

- exact staged allowlist for B2 paths only
- route registry and response-contract review
- focused API root file-test verification
- GitNexus staged verification and staged change detection
- OPENDOG blocker check

## Verification

No source or test files were modified during this preparation.

Current evidence:

- `git status --porcelain=v1 -- tests/api` classified 23 tracked modified `tests/api/test_*_file.py` candidates
- no `tests/api/*.py` root untracked candidates were accepted
- B2 remains no-source until explicit approval
