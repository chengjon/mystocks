# B4.012-M3a-E3 Governance Script Tests No-Source Split

- Date: 2026-06-21
- Node: `b4-012-m3a-e3-governance-script-tests-split`
- Parent: `b4-012-m3a-e-performance-runtime-security-tests-split`
- Source edits authorized: false

## Boundary

This is a no-source split review only. It does not authorize edits, deletion, restore, migration, staging of untracked files, source/runtime changes, OpenSpec changes, OpenStock provider/runtime changes, frontend/backend source changes, ST-HOLD, or `marketKlineData`.

E1 performance/runtime tracked tests and E2 security/compliance tracked tests are already closed and are not reopened here.

## Current Dirty Surface

### `tests/unit/scripts/**`

Tracked dirty:

- `tests/unit/scripts/test_repository_hygiene_paths.py`

Untracked provenance candidates:

- `tests/unit/scripts/test_collect_tech_debt_baseline.py`
- `tests/unit/scripts/test_gitnexus_workflow_gate.py`
- `tests/unit/scripts/test_graphiti_post_commit_hook_integration.py`

Disposition:

- The tracked repository hygiene file is a valid small E3a authorization candidate.
- The three untracked files remain under the broader `B4.012-M3a-U` untracked provenance review. They must not be accepted, staged, or implemented through E3.

### `scripts/tests/**`

Tracked dirty count: 28.

Family split:

- Legacy frontend/validation tests:
  - `scripts/tests/legacy/test_frontend_comprehensive.py`
  - `scripts/tests/legacy/test_frontend_deep.py`
  - `scripts/tests/legacy/test_sina_adapter.py`
  - `scripts/tests/legacy/test_validation_system.py`
- Security authentication script tests:
  - `scripts/tests/test_security_authentication/authentication_tester_methods/part1.py`
  - `scripts/tests/test_security_authentication/authentication_tester_methods/part2.py`
  - `scripts/tests/test_security_authentication/helpers.py`
  - `scripts/tests/test_security_authentication/utils.py`
- Data source / data utility script tests:
  - `scripts/tests/test_data_quality_validator/mock_data_quality_monitor.py`
  - `scripts/tests/test_data_source_logger.py`
  - `scripts/tests/test_data_source_manager.py`
  - `scripts/tests/test_data_source_validator.py`
  - `scripts/tests/test_data_validator_phase6.py`
  - `scripts/tests/test_price_data_adapter.py`
  - `scripts/tests/test_tdx_server_config.py`
- Performance / scalability script tests:
  - `scripts/tests/test_column_mapper/test_performance_and_scalability.py`
  - `scripts/tests/test_data_format_converter/test_performance_and_scalability.py`
- DB / logging / exception support script tests:
  - `scripts/tests/test_check_db_health.py`
  - `scripts/tests/test_db_connection_retry/test_db_retry_decorator.py`
  - `scripts/tests/test_db_connection_retry/test_integration.py`
  - `scripts/tests/test_exceptions_phase6.py`
  - `scripts/tests/test_logging_config.py`
- API health / integration script tests:
  - `scripts/tests/test_advanced_analysis_api_integration.py`
  - `scripts/tests/test_check_api_health.py`
  - `scripts/tests/test_check_api_health_v2.py`
  - `scripts/tests/test_phase3_integration.py`
- Governance / hygiene script tests:
  - `scripts/tests/test_add_python_headers.py`
  - `scripts/tests/test_validate_gitignore.py`

Disposition:

- `scripts/tests/**` is too broad for the original E3 single-file candidate and must not be mixed with `tests/unit/scripts/test_repository_hygiene_paths.py`.
- It should become a later E4/E5 familyized split, grouped by runtime risk and OpenStock/data-source boundary.
- Data-source-like script tests must preserve the current architecture boundary: MyStocks consumes/adapts data from OpenStock and must not reintroduce provider/data-source runtime ownership.

## Recommended Next Queue

1. `B4.012-M3a-E3a repository hygiene unit script tracked authorization prep`
   - Candidate scope: `tests/unit/scripts/test_repository_hygiene_paths.py`
   - No untracked files.
   - Low/medium risk; verify with `py_compile`, `ruff`, and focused pytest for that explicit file.

2. `B4.012-M3a-E4 scripts/tests family split no-source review`
   - Candidate scope: the 28 tracked `scripts/tests/**` files above.
   - Must split into legacy, security-auth, data-source/data-utility, performance/scalability, DB/logging, API-health, and governance-hygiene groups.

3. `B4.012-M3a-U untracked tests provenance review`
   - Candidate scope includes the 3 untracked `tests/unit/scripts/**` files and the already known untracked performance/deployment candidates.

## Decision

E3 should not be implemented as one broad package. The safe next implementation candidate is E3a with exactly one tracked file: `tests/unit/scripts/test_repository_hygiene_paths.py`.
