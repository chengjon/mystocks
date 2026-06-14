# B4.012-M3a-A tests infrastructure/helper boundary authorization prep

Date: 2026-06-14
Mode: no-source authorization preparation, no test/source edits
Node: `b4-012-m3a-a-tests-infra-helper-boundary-authorization`
Parent audit: `b4-012-m3a-tests-residual-domain-audit`
Baseline HEAD: `fc57d9834 B4.012-M3a-GOV: record canonical tests gate correction`

## Scope

This package prepares a narrow follow-up authorization boundary for the first tests residual implementation batch.

The intended batch is test infrastructure and shared helper only. It is not an approval to edit tests yet.

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

Future source/test authorization, if approved, should be limited to these 12 tracked paths:

- `tests/base.py`
- `tests/base_enhanced.py`
- `tests/ci/run_pipeline.py`
- `tests/ci/test_continuous_integration.py`
- `tests/conftest.py`
- `tests/file_level/conftest.py`
- `tests/file_level/fixtures.py`
- `tests/file_level/test_runner.py`
- `tests/helpers/assertions.ts`
- `tests/helpers/sse-tester/part-1.ts`
- `tests/pipeline/test_data_pipeline.py`
- `tests/test_runner.py`

Current status: all 12 candidate paths are tracked modified files.

## Reference Sensitivity

Reference checks indicate this is a high-impact test-support batch, not ordinary isolated test cleanup:

| Path | Exact path references | Basename references |
|---|---:|---:|
| `tests/conftest.py` | 86 | 187 |
| `tests/test_runner.py` | 12 | 22 |
| `tests/base.py` | 6 | 3107 |
| `tests/helpers/assertions.ts` | 5 | 10 |
| `tests/ci/test_continuous_integration.py` | 8 | 11 |
| `tests/ci/run_pipeline.py` | 3 | 5 |
| `tests/base_enhanced.py` | 2 | 3 |
| `tests/file_level/test_runner.py` | 2 | 22 |
| `tests/pipeline/test_data_pipeline.py` | 2 | 4 |
| `tests/file_level/conftest.py` | 1 | 187 |
| `tests/file_level/fixtures.py` | 0 | 9 |
| `tests/helpers/sse-tester/part-1.ts` | 0 | 41 |

The high basename counts are especially important for `base.py`, `conftest.py`, runner, and helper files. Any implementation pass needs focused review and targeted verification rather than broad acceptance by status.

## Explicit Exclusions

Excluded from this batch:

- family-local helper files:
  - `tests/adapters/test_akshare_adapter/helpers.py`
  - `tests/ai/test_ai_assisted_testing/helpers.py`
  - `tests/ai/test_ai_assisted_testing/utils.py`
  - `tests/security/test_security_compliance/helpers.py`
  - `tests/security/test_security_compliance/utils.py`
  - `tests/security/test_security_vulnerabilities/utils.py`
- all 13 untracked tests from the M3a audit
- API/backend contract tests
- adapter/data-source tests
- frontend/E2E tests
- performance/runtime/security governance tests
- source files outside `tests/**`

Family-local helpers should stay with their own domain packages because their behavior is coupled to adapter, AI, or security test semantics.

Untracked tests require a separate provenance review before any preserve/delete/ignore decision.

## Proposed Commit Gates For Future Implementation

Before committing any future M3a-A implementation package:

- exact staged allowlist contains only the 12 approved tracked test paths plus any explicitly approved paired report
- `git diff --cached --check`
- GitNexus impact or staged verification reports low/understood blast radius
- focused pytest for affected shared helpers/runners where feasible
- no untracked test path is staged
- OPENDOG reports no cleanup blockers

## Proposed Closeout Gates

Closeout should report:

- which of the 12 candidate paths were accepted
- whether any candidate path was intentionally deferred
- focused verification command and result
- whether future API/backend, adapter, E2E, performance/security, and untracked-test packages remain open

## Decision

Prepare M3a-A as a small, high-review test-support authorization package.

Function Tree authorization-prepared status remains `source_edits_authorized: false`.

Do not proceed to source/test edits until explicit human approval is granted for this exact candidate scope.

## Implementation Evidence - 2026-06-14

User granted formal implementation authorization for `B4.012-M3a-A tests infra/helper boundary implementation` at HEAD `f05e40618`.

Implementation stayed inside the existing allowed path boundary:

- `tests/base.py`
- `tests/base_enhanced.py`
- `tests/ci/run_pipeline.py`
- `tests/ci/test_continuous_integration.py`
- `tests/conftest.py`
- `tests/file_level/conftest.py`
- `tests/file_level/fixtures.py`
- `tests/file_level/test_runner.py`
- `tests/helpers/assertions.ts`
- `tests/helpers/sse-tester/part-1.ts`
- `tests/pipeline/test_data_pipeline.py`
- `tests/test_runner.py`

Accepted and standardized the existing test helper deltas:

- cleaned unused imports and unused exception variables
- converted bare `except` handlers in focused helper code to `except Exception`
- added governance metadata to existing TODO / skip / `any` compatibility markers
- normalized harmless formatting and f-string lint issues
- added a direct-import fallback for `tests/ci/test_continuous_integration.py` so pytest collection and top-level runner imports work when `tests/ci` is not a package
- corrected focused ruff findings in the same allowed files

No source, runtime, OpenSpec, frontend implementation, ST-HOLD, marketKlineData, untracked tests, or external dirty files were modified or staged.

Verification performed:

- `ft-governance scope-check --files <12 test/helper paths>`: passed, 12 changed files within active authorization
- `python -m ruff check <10 Python allowed paths>`: passed
- `python -m py_compile <10 Python allowed paths>`: passed
- `npx tsc --noEmit --skipLibCheck --target ES2020 --module commonjs --moduleResolution node --types node --esModuleInterop tests/helpers/assertions.ts tests/helpers/sse-tester/part-1.ts`: passed
- Python module import smoke for 9 helper/runner modules: passed
- `python tests/ci/run_pipeline.py --help`: passed

Focused pytest note:

- `python -m pytest tests/ci/test_continuous_integration.py tests/file_level/test_runner.py tests/pipeline/test_data_pipeline.py tests/test_runner.py -q --no-cov -p no:cacheprovider` no longer raises the original `tests/ci/test_continuous_integration.py` relative import collection error after the fallback fix.
- The focused pytest command still exits with pytest code 5 because these files are helper/runner/template modules and collect 0 pytest items under the current repository pytest config. This is recorded as a collection-shape limitation, not as a passing unit-test suite.
