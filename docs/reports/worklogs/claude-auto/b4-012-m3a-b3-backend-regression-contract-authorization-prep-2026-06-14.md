# B4.012-M3a-B3 backend regression contract authorization prep

Date: 2026-06-14
Mode: no-source authorization preparation, no test/source edits
Parent split: `b4-012-m3a-b-api-backend-contract-tests-split`

## Scope

This package prepares a narrow future authorization boundary for tracked backend regression and risk-management tests only.

Current no-source status confirms 4 tracked modified candidates:

- `tests/backend/test_data_adapter_regression.py`
- `tests/backend/test_data_api_regression.py`
- `tests/backend/test_risk_management_core.py`
- `tests/backend/test_risk_management_regression.py`

All 4 candidates are tracked modified files. No untracked backend test candidate is included in this batch.

## Explicit Exclusions

Excluded from this batch:

- `tests/api/file_tests/**`
- API root file tests under `tests/api/test_*_file.py`
- tracked contract-engine tests
- untracked contract/deployment tests
- frontend/E2E specs
- security/compliance/performance tests outside this backend regression family
- M3a-A test-infra/helper batch
- M3a-B1 and M3a-B2 API authorization batches
- M3a-U untracked test provenance review
- any source, runtime, OpenSpec, OpenStock, deletion, restore, or staging action

## Risk

Risk level: medium-high.

These tests sit near backend data adapter, API regression, and risk-management behavior. Future implementation must verify backend service/API boundaries and avoid accepting dirty deltas that imply runtime behavior changes without separate source authorization.

## Gate Recommendation

Future implementation authorization, if approved, should allow only the 4 listed backend test files plus a B3 closeout report. It should require:

- exact staged allowlist for B3 paths only
- backend service/API boundary review
- focused backend regression/risk test verification
- GitNexus staged verification and staged change detection
- OPENDOG blocker check

## Verification

No source or test files were modified during this preparation.

Current evidence:

- `git status --porcelain=v1 -- tests/backend` classified 4 tracked modified candidates
- no untracked backend test candidates were accepted
- B3 remains no-source until explicit approval
