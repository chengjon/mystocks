# B4.012-M3a-B API / Backend Contract Tests Fresh Review

Date: 2026-06-19
Repository: `/opt/claude/mystocks_spec`
Baseline HEAD: `a8a276ce22069ba633d2b4dfbbdcc2396e0bc99e`
Mode: no-source family reactivation review

## Scope

This review refreshes the B4.012-M3a-B API/backend contract tests parent after B4.013 closeout and B4.012-M3a parent reactivation.

The immediate target is only:

- `b4-012-m3a-b-api-backend-contract-tests-split`

This package does not authorize test edits, source edits, runtime edits, OpenSpec edits, deletion, untracked preservation, or broad test acceptance.

## Current Gate Truth

- `b4-012-m3a-tests-residual-domain-audit` is `decision-prepared`.
- `b4-012-m3a-b-api-backend-contract-tests-split` is still `blocked` only because it was paused by the B4.013 runtime-first reset.
- Existing child implementation/authorization nodes under B are already closed:
  - `b4-012-m3a-b1-api-file-tests-authorization`
  - `b4-012-m3a-b2-api-root-file-tests-authorization`
  - `b4-012-m3a-b3-backend-regression-contract-authorization`
  - `b4-012-m3a-b4-tracked-contract-engine-tests-authorization`

## Fresh Dirty Surface

Current API/backend-related dirty surface is smaller than the original M3a audit:

| Group | Count | Notes |
| --- | ---: | --- |
| `tests/api/**` | 1 | `tests/api/file_tests/run_file_tests.py` remains tracked dirty and belongs to file-test runner/provenance handling, not broad API behavior acceptance. |
| `tests/backend/**` | 0 | No current dirty files in this path subset. |
| `web/backend/tests/**` | 9 | Backend test dirty files remain and require focused child-family handling. |
| API file tests | 1 | Already represented historically by B1/B2; current runner dirtiness should not be accepted implicitly. |
| Contract/auth/security-adjacent | 4 | Includes CSRF, performance/security, rate limit, and validation model tests. |
| Untracked | 1 | Untracked backend runtime regression test must not be staged without separate provenance authorization. |

## Boundary Decisions

The B family parent can return from `blocked` to `decision-prepared` because:

- B4.013 no longer blocks residual cleanup.
- The tests residual domain parent is now current.
- B1-B4 child nodes are already closed and should not be reopened by this package.

This reactivation does not accept remaining dirty test behavior. It only reopens the family-level decision point so the remaining API/backend contract test surface can be handled by a new child authorization package if needed.

## Risk Notes

- Backend contract tests can either expose route regressions or mask them if assertions are weakened.
- Security-adjacent tests must not be mixed with ordinary file-test runner cleanup.
- Untracked backend regression tests need provenance review before preserve/delete/ignore decisions.
- If any source behavior drift is found, source changes require a separate source-authorized package; this no-source package does not grant that authority.

## Recommended Next Queue

1. If runner dirtiness remains relevant, create a narrow `B4.012-M3a-B5 API/backend file-test runner residual` child package.
2. If security-adjacent backend tests remain dirty, create a separate `B4.012-M3a-B6 backend security-adjacent contract tests` child package.
3. Keep untracked backend regression tests out of staging until the untracked provenance family is explicitly authorized.

## Verification Plan

Before commit:

- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus staged verification and staged change detection
- OPENDOG verification

After commit:

- GitNexus analyze
- staged index empty
- `b4-012-m3a-b-api-backend-contract-tests-split` is `decision-prepared`
- closed B1-B4 child nodes remain closed
