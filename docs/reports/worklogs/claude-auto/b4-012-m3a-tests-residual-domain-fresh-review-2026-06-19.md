# B4.012-M3a Tests Residual Domain Fresh Review

Date: 2026-06-19
Repository: `/opt/claude/mystocks_spec`
Baseline HEAD: `7f384fc57e51546dcfe73cdccaa053eee0c562ea`
Mode: no-source family reactivation review

## Scope

This review refreshes the B4.012 tests residual domain parent after B4.013 runtime mainline closeout and the B4.012-M3 parent reactivation.

The immediate target is only:

- `b4-012-m3a-tests-residual-domain-audit`

This package does not authorize source edits, test edits, test deletion, untracked test preservation, OpenSpec edits, runtime changes, or broad test execution acceptance.

## Current Gate Truth

- No active B4.013 gates remain.
- `b4-012-m3-residual-dirty-atlas-rebaseline` is now `decision-prepared`.
- `b4-012-m3a-tests-residual-domain-audit` is still `blocked` only because it was paused by the B4.013 runtime-first reset.
- Child family nodes remain blocked and must not be unlocked by this package.

## Evidence Reviewed

- `docs/reports/worklogs/claude-auto/b4-012-m3a-tests-residual-domain-no-source-audit-2026-06-14.md`
  - Inventoried the dirty `tests/**` domain.
  - Classified the domain by family and risk.
  - Explicitly prohibited test edits, test deletion, test preservation, untracked test staging, source edits, runtime edits, and OpenSpec edits.
- `docs/reports/worklogs/claude-auto/b4-012-m3-residual-dirty-atlas-reactivation-no-source-review-2026-06-19.md`
  - Removed the B4.013 runtime-first blocker only for the parent dirty atlas entry.
  - Preserved child-family blocking until each family receives a fresh review or explicit authorization.

## Refreshed Family Matrix

The prior family grouping remains valid, but the post-B4.013 ordering changes slightly to keep mainline impact first:

| Priority | Family | Existing node | Fresh decision |
| --- | --- | --- | --- |
| 1 | Tests infrastructure/helpers | not yet split as a child in current active gates | Must be reviewed before accepting large test behavior diffs because helpers, fixtures, and runners can change global pytest behavior. |
| 2 | API/backend contract tests | `b4-012-m3a-b-api-backend-contract-tests-split` | Highest business-protection test family; protects API compatibility and backend route contracts. |
| 3 | Adapter/data-source tests | `b4-012-m3a-c-adapter-data-source-tests-split` | Must preserve the OpenStock boundary: MyStocks tests can validate consumer integration and adapters, but must not rebuild provider/data-source functionality in MyStocks. |
| 4 | E2E/frontend tests | `b4-012-m3a-d-e2e-frontend-tests-split` | Must be refreshed against current PM2/browser-smoke truth before any assertion or fixture changes. |
| 5 | Performance/runtime/security tests | `b4-012-m3a-e-performance-runtime-security-tests-split` | High gate semantics; keep isolated from ordinary unit or contract test cleanup. |
| 6 | Untracked test provenance | `b4-012-m3a-u-untracked-tests-provenance-review` | Metadata/provenance only until explicit preserve/delete/ignore authorization exists. |

`b4-012-m3a-d1-e2e-browser-smoke-authorization` remains downstream of the E2E/frontend family and should stay blocked until the E2E no-source review is current.

## Boundary Decisions

The parent tests residual domain can return from `blocked` to `decision-prepared` because the B4.013 runtime-first blocker is gone.

This is only a decision reactivation:

- no test file edits
- no test file deletion
- no untracked test staging
- no source/runtime/OpenSpec edits
- no broad test result acceptance from the existing dirty state
- no child-family authorization

## Next Queue

Recommended next package:

1. `B4.012-M3a-A tests infrastructure/helper boundary no-source review`
   - Review `tests/conftest.py`, base/helper files, fixtures, runners, and file-level harnesses.
   - Decide whether a child node/card is needed if the current FUNCTION_TREE does not already model this family.

Then proceed to child families in order:

1. `B4.012-M3a-B` API/backend contract tests.
2. `B4.012-M3a-C` adapter/data-source tests, with OpenStock boundary enforcement.
3. `B4.012-M3a-D` E2E/frontend tests.
4. `B4.012-M3a-E` performance/runtime/security tests.
5. `B4.012-M3a-U` untracked provenance review.

## Verification Plan

Before commit:

- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus staged verification and staged change detection
- OPENDOG verification

After commit:

- GitNexus analyze
- staged index empty
- `b4-012-m3a-tests-residual-domain-audit` is `decision-prepared`
- child family nodes remain blocked
