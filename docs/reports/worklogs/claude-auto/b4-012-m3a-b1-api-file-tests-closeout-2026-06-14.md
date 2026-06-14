# B4.012-M3a-B1 API file_tests Closeout

Date: 2026-06-14
Node: `b4-012-m3a-b1-api-file-tests-authorization`
Commit: `968daa491 B4.012-M3a-B1: standardize API file tests`

## Scope

Implemented the approved B4.012-M3a-B1 API file_tests batch within the Function Tree `allowed_paths`:

- 27 tracked `tests/api/file_tests/test_*_api.py` files in the B1 authorization.
- Function Tree governance metadata required to bind the authorization and implementation evidence.

Excluded from this batch:

- `tests/api/file_tests/run_file_tests.py`
- API root file tests, backend regression tests, contract-engine tests, E2E/frontend tests, security/performance tests, untracked tests, source/runtime/OpenSpec files, and external dirty files.

## Implementation Summary

- Removed stale unused `tests.api.file_tests.conftest` fixture imports from the approved API file_tests set.
- Preserved the technical analysis API test hardening that validates route-local data-source factory wiring without touching backend runtime code.
- Split two composite trade-route contract assertions into independent assertions to satisfy focused ruff `PT018` without changing test semantics.

## Verification

- GitNexus index refreshed before implementation checks: indexed current HEAD `d18802523835cd11e67149dde4a69609b28c72ed`.
- GitNexus pre-change graph query found API file_tests classes with `0` incoming business/runtime dependents.
- `python -m py_compile <27 B1 API file_tests>`: passed.
- `python -m ruff check <27 B1 API file_tests>`: passed.
- `python -m pytest --no-cov --tb=short -q <27 B1 API file_tests>`: `457 passed in 2.51s`.
- `python -m pytest --tb=short -q <27 B1 API file_tests>`: test body result `457 passed`; process exit was `1` only because repository-level coverage fail-under `80%` is not valid for this focused subset (`Total coverage: 1.81%`).
- `git diff --cached --check`: passed.
- `ft-governance scope-check --files <30 staged files>`: passed.
- `node .gitnexus/run.cjs verify-staged --repo mystocks --cwd /opt/claude/mystocks_spec --json`: passed.
- `node .gitnexus/run.cjs detect-changes --scope staged --repo mystocks --cwd /opt/claude/mystocks_spec`: risk `low`, affected processes `0`.
- OPENDOG verification: available, required evidence present, no cleanup/refactor blockers.
- GitNexus post-commit index refresh completed after `968daa491`.

## Boundary Result

B4.012-M3a-B1 is closed as a tests-only standardization batch. No source, runtime, OpenSpec, ST-HOLD, marketKlineData, untracked tests, or external dirty files were staged or committed.
