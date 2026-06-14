# B4.012-M3a-B3 Backend Regression Contract Closeout

Date: 2026-06-15 Asia/Shanghai
Node: `b4-012-m3a-b3-backend-regression-contract-authorization`
Commit: `73dc60d83 B4.012-M3a-B3: standardize backend regression contracts`

## Scope

Implemented the approved B4.012-M3a-B3 backend regression/contract test batch within the Function Tree `allowed_paths`:

- `tests/backend/test_data_adapter_regression.py`
- `tests/backend/test_data_api_regression.py`
- `tests/backend/test_risk_management_core.py`
- `tests/backend/test_risk_management_regression.py`
- Function Tree governance metadata required to bind the authorization and implementation evidence.

Excluded from this batch:

- source/runtime files
- OpenSpec files
- `tests/api/**`
- `tests/api/file_tests/run_file_tests.py`
- contract-engine tests
- E2E/frontend tests
- security/performance tests
- untracked tests and external dirty files

## Implementation Summary

- Adapted `test_risk_management_core.py` away from the retired `app.api.risk_management_core` import and onto current services-layer risk APIs.
- Converted obsolete static `RiskCalculator`/`RiskService` assertions into assertions against `RiskBase` and `RiskManagementService` public methods.
- Corrected `test_data_api_regression.py` requests to match its directly mounted `app.api.data` router paths.
- Preserved existing backend regression intent: data adapter fallback behavior, data API route regression coverage, and risk calculation/service smoke coverage.

## Verification

- GitNexus impact check on representative `test_risk_calculator_var`: risk `LOW`, direct callers `0`, affected processes `0`.
- `python -m py_compile <4 B3 backend regression tests>`: passed.
- `python -m ruff check <4 B3 backend regression tests>`: passed.
- `python -m pytest --no-cov --tb=short -q <4 B3 backend regression tests>`: `21 passed, 1 warning in 7.01s`.
- `python -m pytest --tb=short -q <4 B3 backend regression tests>`: test body result `21 passed, 1 warning`; process exit was `1` only because repository-level coverage fail-under `80%` is not valid for this focused subset (`Total coverage: 5.39%`).
- `git diff --check`: passed before staging.
- `ft-governance scope-check --files <7 staged files>`: passed.
- `git diff --cached --check`: passed.
- `node .gitnexus/run.cjs verify-staged --repo mystocks --cwd /opt/claude/mystocks_spec --json`: passed.
- `node .gitnexus/run.cjs detect-changes --scope staged --repo mystocks --cwd /opt/claude/mystocks_spec`: affected processes `0`.
- OPENDOG verification: available, required evidence present, no cleanup/refactor blockers.
- GitNexus post-commit index refresh completed after `73dc60d83`.

## Boundary Result

B4.012-M3a-B3 is closed as a tests-only standardization batch. No source, runtime, OpenSpec, ST-HOLD, marketKlineData, `tests/api/**`, untracked tests, or external dirty files were staged or committed.
