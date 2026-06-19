# B4.012-M3a-C Adapter / Data-Source Tests Fresh Review

Date: 2026-06-19
Repository: `/opt/claude/mystocks_spec`
Baseline HEAD: `188deee6916c617a997f60d5410d5331bc2202df`
Mode: no-source family reactivation review

## Scope

This review refreshes the B4.012-M3a-C adapter/data-source tests parent after B4.013 closeout and B4.012-M3a parent reactivation.

The immediate target is only:

- `b4-012-m3a-c-adapter-data-source-tests-split`

This package does not authorize test edits, source edits, runtime edits, OpenSpec edits, OpenStock edits, deletion, untracked preservation, or broad test acceptance.

## Current Gate Truth

- `b4-012-m3a-tests-residual-domain-audit` is `decision-prepared`.
- `b4-012-m3a-c-adapter-data-source-tests-split` is still `blocked` only because it was paused by the B4.013 runtime-first reset.
- Existing child implementation/authorization nodes under C are already closed:
  - `b4-012-m3a-c1-fast-adapter-tests-authorization`
  - `b4-012-m3a-c2-datasource-registry-tests-authorization`
  - `b4-012-m3a-c3-query-builder-contract-authorization`
  - `b4-012-m3a-c4-akshare-adapter-tests-authorization`
  - `b4-012-m3a-c5-other-adapter-compatibility-tests-authorization`
  - `b4-012-m3a-c6-datasource-manager-tests-authorization`

## Fresh Dirty Surface

Current adapter/data-source-related dirty surface remains mixed and must not be accepted as one batch:

| Group | Count | Notes |
| --- | ---: | --- |
| Total matching paths | 23 | Includes test, script-test, backend-test, and source-path matches. |
| Tracked | 22 | Tracked dirty paths require explicit family authorization before staging. |
| Untracked | 1 | `tests/unit/data_source/` must remain provenance-only until separately authorized. |
| `tests/unit/data_source/**` | 1 | Untracked data-source unit-test directory; not automatically preserved. |
| `web/backend/tests/**` | 2 | Backend data-source factory tests; must remain tests-only unless a separate backend source review is authorized. |
| `scripts/tests/**` | 6 | Script-level adapter/data-source tests; do not mix with application contract tests. |
| Source paths | 4 | Source-path dirty files are explicitly out of scope for this test-family reactivation. |
| OpenStock-boundary-sensitive | 13 | Names imply adapter/data-source/provider sensitivity and require boundary discipline. |

## OpenStock Boundary

The boundary remains fixed:

- OpenStock owns provider runtime, provider adapters, provider execution, provider fallback, provider-specific normalization, and new provider category work.
- MyStocks owns consumer integration, compatibility tests, adapter contract assertions for local compatibility, and response/read-model adaptation.
- This C family must not reintroduce provider/data-source development into MyStocks.
- Any future test package under this family must distinguish consumer/compatibility verification from provider acquisition behavior.

## Boundary Decisions

The C family parent can return from `blocked` to `decision-prepared` because:

- B4.013 no longer blocks residual cleanup.
- The tests residual domain parent is now current.
- C1-C6 child packages are already closed and should not be reopened by this package.

This reactivation does not accept remaining dirty test behavior. It only reopens the family-level decision point so remaining adapter/data-source test or provenance work can be handled by a new child authorization package if needed.

## Risk Notes

- Adapter/data-source tests can accidentally encode provider responsibilities back into MyStocks.
- Source-path dirty files such as `src/adapters/**`, `src/core/data_source/**`, and database manager internals are outside this package and require separate source authorization if ever touched.
- Untracked `tests/unit/data_source/` must not be staged without provenance authorization.
- Existing closed C1-C6 nodes remain historical evidence and must not be treated as open permission for new edits.

## Recommended Next Queue

1. If remaining untracked data-source tests are still relevant, handle them through `B4.012-M3a-U untracked provenance review`, not through this parent reactivation.
2. If remaining script-level adapter tests need cleanup, prepare a narrow child authorization package that is tests-only and excludes source/provider changes.
3. If any adapter/data-source behavior gap requires implementation, stop and request a separate source-authorized package with explicit OpenStock boundary review.

## Verification Plan

Before commit:

- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus staged verification and staged change detection
- OPENDOG verification

After commit:

- GitNexus analyze
- staged index empty
- `b4-012-m3a-c-adapter-data-source-tests-split` is `decision-prepared`
- closed C1-C6 child nodes remain closed
