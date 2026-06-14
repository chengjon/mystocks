# B4.012-M3a-B API backend contract tests no-source split

Date: 2026-06-14
Mode: no-source split audit, no test/source/runtime cleanup authorization
Node: `b4-012-m3a-b-api-backend-contract-tests-split`
Parent gate: `b4-012-m3a-tests-residual-domain-audit`
Baseline HEAD: `fada290da B4.012-M3a-A: prepare tests infra helper authorization`

## Scope

This audit splits the M3a tests residual API/backend/contract dirty domain into narrower future packages.

Included:

- `tests/api/**`
- `tests/backend/**`
- tracked contract-related tests under `tests/unit/api/**` and `tests/unit/contract/**`
- auth/security-adjacent API/backend tests when they are part of API or backend contract coverage

Excluded:

- `tests/security/**` security/compliance implementation details, reserved for M3a-E
- E2E/frontend auth specs, reserved for M3a-D
- untracked contract/deployment tests, reserved for provenance review before preserve/delete/ignore decisions
- any source, runtime, OpenSpec, OpenStock, deletion, restore, or staging action

## Current Dirty Summary

Measured from `git status --porcelain=v1 -- tests` on 2026-06-14.

M3a total tests dirty baseline remains 231 entries.

Broad M3a-B discovery matched 61 unique entries:

- modified: 58
- untracked: 3
- deleted: 0

The 61-entry discovery set is intentionally broader than a future implementation authorization. It includes overlap and routing candidates that must be split before source/test edits.

## Category Matrix

| Category | Count | Status | Decision |
|---|---:|---|---|
| `tests/api/file_tests/**` | 28 | modified | Split into API file-test implementation package; `run_file_tests.py` overlaps M3a-A runner boundary. |
| `tests/api/*.py` | 23 | modified | Split into API root file-test package paired with route/contract truth. |
| `tests/backend/**` | 4 | modified | Split into backend regression/risk package, not mixed with broad API file tests. |
| tracked contract tests | 2 | modified | Split into contract-engine/impact package. |
| untracked contract/deployment tests | 3 | untracked | Do not stage; route through M3a-U provenance and possibly M3a-E runtime/deployment gates. |
| API auth/security-adjacent | 1 API file test | modified | Keep with API package but require security boundary review. |
| E2E auth spec | 1 | modified | Exclude from M3a-B; route to M3a-D. |
| `tests/security/**` domain files | 7 | modified | Exclude from M3a-B; route to M3a-E. |

## API File-Test Candidates

Future package should exclude `tests/api/file_tests/run_file_tests.py` if M3a-A implementation has already claimed runner infrastructure.

- `tests/api/file_tests/run_file_tests.py` (runner overlap with M3a-A)
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

## API Root File-Test Candidates

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

## Backend And Contract Candidates

Backend regression/risk:

- `tests/backend/test_data_adapter_regression.py`
- `tests/backend/test_data_api_regression.py`
- `tests/backend/test_risk_management_core.py`
- `tests/backend/test_risk_management_regression.py`

Tracked contract:

- `tests/unit/api/test_contract_impact_analyzer.py`
- `tests/unit/contract/test_contract_engine_runtime_source.py`

Untracked contract/deployment candidates, not authorized here:

- `tests/integration/contract/test_contract_validation_e2e.py`
- `tests/performance/test_validate_container_deployment_contract.py`
- `tests/performance/test_validate_deployment_env_contract.py`

## Routing Decisions

Recommended follow-up packages:

1. `B4.012-M3a-B1 API file_tests authorization prep`
   - Scope: API file tests, excluding runner overlap unless M3a-A defers it.
   - Gate: route/API contract shape review before implementation.

2. `B4.012-M3a-B2 API root file_tests authorization prep`
   - Scope: `tests/api/test_*_file.py`.
   - Gate: route registry and response-contract review.

3. `B4.012-M3a-B3 backend regression contract authorization prep`
   - Scope: `tests/backend/**`.
   - Gate: backend service/API boundary review.

4. `B4.012-M3a-B4 tracked contract engine tests authorization prep`
   - Scope: tracked contract tests only.
   - Gate: contract engine/runtime source boundary review.

5. Route untracked contract/deployment tests to M3a-U/M3a-E before any preserve/delete/ignore decision.

## Non-Goals

- No test edits.
- No source/backend/API implementation edits.
- No test deletion, restore, or untracked staging.
- No OpenSpec, OpenStock, frontend, E2E, runtime, deployment, or security-domain implementation.
- No acceptance of API response shape changes.

## Required Gates For This Audit Package

- exact staged allowlist of governance/report files only
- `git diff --cached --check`
- Function Tree validation
- GitNexus staged `detect_changes`

## Decision

Move this node to `decision-prepared` with `source_edits_authorized: false`.

M3a-B is too broad for one implementation package. It should remain a decision/split package and feed B1-B4 plus M3a-U/M3a-E follow-ups.
