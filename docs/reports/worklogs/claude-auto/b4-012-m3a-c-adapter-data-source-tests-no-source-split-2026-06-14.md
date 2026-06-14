# B4.012-M3a-C adapter and data-source tests no-source split

Date: 2026-06-14
Mode: no-source split audit, no test/source/runtime cleanup authorization
Parent gate: `b4-012-m3a-tests-residual-domain-audit`

## Scope

This audit splits the adapter and data-source test dirty domain into narrower future packages.

Included:

- adapter unit tests under `tests/adapters/**`
- root adapter compatibility tests
- unit adapter/data-source manager tests
- data-source registry and metrics tests

Explicitly excluded:

- API/backend overlap already routed through M3a-B1/B2/B3
- contract-engine tests already routed through M3a-B4
- generated AI/tooling tests
- untracked `tests/unit/data_source/**`, which requires M3a-U provenance review
- any source, runtime, OpenSpec, OpenStock, deletion, restore, or staging action

## Current Dirty Summary

Measured from `git status --porcelain=v1 -- tests` on 2026-06-14.

Refined M3a-C tracked candidate count: 25.

All 25 candidates are tracked modified files:

- `tests/adapters/test_akshare_adapter/helpers.py`
- `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part1.py`
- `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part2.py`
- `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part3.py`
- `tests/adapters/test_financial_adapter_refactored.py`
- `tests/adapters/test_tdx_adapter_refactored.py`
- `tests/data_sources/test_query_builder.py`
- `tests/test_akshare_adapter.py`
- `tests/test_tdx_adapter.py`
- `tests/unit/adapters/test_akshare_adapter.py`
- `tests/unit/adapters/test_akshare_adapter_real.py`
- `tests/unit/adapters/test_baostock_adapter_real.py`
- `tests/unit/adapters/test_byapi_adapter_basic.py`
- `tests/unit/adapters/test_customer_adapter_basic.py`
- `tests/unit/adapters/test_data_source_manager.py`
- `tests/unit/adapters/test_data_source_manager_basic.py`
- `tests/unit/adapters/test_data_source_manager_fixed.py`
- `tests/unit/adapters/test_financial_adapter_real.py`
- `tests/unit/adapters/test_financial_adapter_simple.py`
- `tests/unit/adapters/test_tdx_connection_manager.py`
- `tests/unit/adapters/test_tushare_adapter_basic.py`
- `tests/unit/core/test_datasource_registry_redis_runtime.py`
- `tests/unit/test_data_source_metrics_integration.py`
- `tests/unit/test_datasource/test_health.py`
- `tests/unit/test_datasource/test_registry.py`

## Boundary Findings

The initial broad regex found 30 adapter/data-source-named dirty paths. This split keeps the standalone adapter/data-source tracked set at 25 and routes overlaps separately:

- API overlap remains in M3a-B1/B2:
  - `tests/api/file_tests/test_akshare_market_api.py`
  - `tests/api/file_tests/test_realtime_mtm_adapter_api.py`
  - `tests/api/file_tests/test_realtime_mtm_init_api.py`
  - `tests/api/test_akshare_market_file.py`
  - `tests/api/test_multi_source_file.py`
- backend overlap remains in M3a-B3:
  - `tests/backend/test_data_adapter_regression.py`
- generated/tooling overlap is not accepted into C:
  - `tests/generated/test_new_market_data_adapter_new_feature.py`
- untracked data-source contract candidate is routed to M3a-U:
  - `tests/unit/data_source/test_data_source_client_contract.py`

## Suggested Follow-Up Packages

1. `B4.012-M3a-C1 adapter unit compatibility authorization prep`
   - Candidate scope: `tests/adapters/**`, root `tests/test_*adapter.py`, and `tests/unit/adapters/test_*adapter*.py`.
   - Gate: adapter contract review and external data-source assumption review.

2. `B4.012-M3a-C2 data-source manager and registry authorization prep`
   - Candidate scope: data-source manager, datasource registry, query builder, and metrics tests.
   - Gate: source manager/registry behavior truth review.

3. `B4.012-M3a-C-U data-source untracked provenance review`
   - Candidate scope: `tests/unit/data_source/test_data_source_client_contract.py`.
   - Gate: provenance and preserve/delete/ignore decision before staging.

## Non-Goals

- No test edits.
- No source, backend, API, frontend, runtime, OpenSpec, OpenStock, ST-HOLD, or marketKlineData edits.
- No test deletion, restore, or untracked staging.
- No acceptance of external data-source behavior changes.

## Required Gates For This Audit Package

- exact staged allowlist of governance/report files only
- `git diff --cached --check`
- Function Tree validation
- GitNexus staged verification
- GitNexus staged detect-changes
- OPENDOG blocker check
- post-commit GitNexus index refresh

## Current Status

`source_edits_authorized: false`

This no-source split does not authorize adapter or data-source test implementation.
