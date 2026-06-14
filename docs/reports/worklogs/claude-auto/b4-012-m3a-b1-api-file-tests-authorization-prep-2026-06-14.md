# B4.012-M3a-B1 API file_tests authorization prep

Date: 2026-06-14
Mode: no-source authorization preparation, no test/source edits
Parent split: `b4-012-m3a-b-api-backend-contract-tests-split`

## Scope

This package prepares a narrow future authorization boundary for the API file test subfamily only.

The intended batch is intentionally smaller than the whole API/backend split.

Allowed in this preparation package:

- read-only Git status/reference checks
- exact candidate path list
- authorization scope and non-goal definition
- governance metadata and this report

Forbidden in this preparation package:

- editing, deleting, restoring, formatting, or staging any `tests/**` file
- accepting any untracked test path
- changing source, backend, frontend, API, runtime, OpenSpec, ST-HOLD, `marketKlineData`, config, or external dirty files
- running the dirty test files as acceptance evidence for their future behavior

## Candidate Implementation Scope

Future source/test authorization, if approved, should be limited to these 27 tracked API file-test paths:

- `tests/api/file_tests/test_akshare_market_api.py`
- `tests/api/file_tests/test_backup_recovery_api.py`
- `tests/api/file_tests/test_backup_recovery_secure_api.py`
- `tests/api/file_tests/test_data_lineage_api.py`
- `tests/api/file_tests/test_data_quality_api.py`
- `tests/api/file_tests/test_governance_dashboard_api.py`
- `tests/api/file_tests/test_indicators_api.py`
- `tests/api/file_tests/test_market_v2_api.py`
- `tests/api/file_tests/test_metrics_api.py`
- `tests/api/file_tests/test_monitoring_analysis_api.py`
- `tests/api/file_tests/test_notification_api.py`
- `tests/api/file_tests/test_prometheus_exporter_api.py`
- `tests/api/file_tests/test_realtime_market_api.py`
- `tests/api/file_tests/test_realtime_mtm_adapter_api.py`
- `tests/api/file_tests/test_realtime_mtm_init_api.py`
- `tests/api/file_tests/test_signal_monitoring_api.py`
- `tests/api/file_tests/test_sse_endpoints_api.py`
- `tests/api/file_tests/test_stock_search_api.py`
- `tests/api/file_tests/test_strategy_api.py`
- `tests/api/file_tests/test_strategy_list_mock_api.py`
- `tests/api/file_tests/test_strategy_mgmt_api.py`
- `tests/api/file_tests/test_system_api.py`
- `tests/api/file_tests/test_tasks_api.py`
- `tests/api/file_tests/test_technical_analysis_api.py`
- `tests/api/file_tests/test_trade_routes_api.py`
- `tests/api/file_tests/test_watchlist_api.py`
- `tests/api/file_tests/test_websocket_api.py`

## Explicit Exclusions

Excluded from this batch:

- `tests/api/file_tests/run_file_tests.py` runner overlap
- API root file tests under `tests/api/test_*_file.py`
- backend regression/risk tests
- tracked contract-engine tests
- untracked contract/deployment tests
- M3a-A test-infra/helper batch
- M3a-D frontend/E2E auth specs
- M3a-E security/compliance tests
- M3a-U untracked test provenance review
- any source, runtime, OpenSpec, OpenStock, deletion, restore, or staging action

## Reference Sensitivity

The API file-test family remains high-impact because it has broad route/response coverage:

- many files overlap API route truths and contract shapes
- several files cover monitoring, metrics, real-time, strategy, and websocket behavior
- future implementation should be split further if route or contract drift is discovered

## Proposed Commit Gates For Future Implementation

Before committing any future B1 implementation package:

- exact staged allowlist contains only the 27 approved tracked API file-test paths plus any explicitly approved paired report
- `git diff --cached --check`
- GitNexus staged verification and impact/review as appropriate for the changed API file-test set
- focused pytest for the affected API file-test family
- no untracked test path is staged
- OPENDOG reports no cleanup blockers

## Proposed Closeout Gates

Closeout should report:

- which of the 27 API file-test paths were accepted
- whether `run_file_tests.py` stayed excluded
- focused verification command and result
- whether API root file tests, backend regression tests, contract-engine tests, M3a-D, M3a-E, and M3a-U remain open

## Decision

Prepare B1 as an API file-test-only authorization package.

Do not proceed to source/test edits until explicit human approval is granted for this exact candidate scope.
