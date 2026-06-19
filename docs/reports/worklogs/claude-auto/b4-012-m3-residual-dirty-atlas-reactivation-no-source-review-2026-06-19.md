# B4.012-M3 Residual Dirty Atlas Reactivation No-Source Review

Date: 2026-06-19
Repository: `/opt/claude/mystocks_spec`
Baseline HEAD: `7a48081e9b4b993ae3dd4f4e7d456a2be3ab352f`
Mode: no-source reactivation review

## Scope

This review restarts the B4.012 residual dirty/test cleanup line after the B4.013 runtime mainline closeout.

The immediate target is only the parent governance gate:

- `b4-012-m3-residual-dirty-atlas-rebaseline`

This package does not authorize source, test, OpenSpec, runtime, deletion, or archive edits.

## Current Active Gate Truth

B4.013 has no remaining active gates. The remaining active gates are B4.012 residual cleanup nodes that were blocked during the B4.013 runtime-first reset:

| Node | Current status | Current next gate | Role |
| --- | --- | --- | --- |
| `b4-012-m3-residual-dirty-atlas-rebaseline` | `blocked` | unblock to `decision-prepared` | parent dirty-atlas rebaseline entry |
| `b4-012-m3a-tests-residual-domain-audit` | `blocked` | unblock to `decision-prepared` | tests residual domain parent |
| `b4-012-m3a-b-api-backend-contract-tests-split` | `blocked` | unblock to `decision-prepared` | API/backend contract test family |
| `b4-012-m3a-c-adapter-data-source-tests-split` | `blocked` | unblock to `decision-prepared` | adapter/data-source test family |
| `b4-012-m3a-d-e2e-frontend-tests-split` | `blocked` | unblock to `decision-prepared` | E2E/frontend test family |
| `b4-012-m3a-e-performance-runtime-security-tests-split` | `blocked` | unblock to `decision-prepared` | performance/runtime/security test family |
| `b4-012-m3a-u-untracked-tests-provenance-review` | `blocked` | unblock to `decision-prepared` | untracked test provenance review |
| `b4-012-m3a-d1-e2e-browser-smoke-authorization` | `blocked` | unblock to `authorization-prepared` | downstream E2E browser smoke authorization |

## Reactivation Decision

The B4.013 runtime-first blocker has been removed for the parent B4.012-M3 dirty-atlas entry because:

- B4.013 runtime mainline bring-up is closed.
- B4.013 OpenStock / FUND_FLOW evidence-family active gates are archived.
- The remaining B4.012 work is not a runtime-mainline source implementation package.

The parent node can return from `blocked` to `decision-prepared` so the cleanup line can be reprioritized and split by family.

This does not unblock the child implementation or authorization nodes yet. Each child family must be refreshed separately before any source/test/deletion work is requested.

## Queue Priority

Next work should follow the mainline-alignment method and dirty worktree cleanup guide:

1. Keep B4.012-M3 as a no-source parent rebaseline entry.
2. Refresh `b4-012-m3a-tests-residual-domain-audit` as a no-source family inventory.
3. Rank the child families by mainline impact and risk:
   - API/backend contract tests first if they protect runtime API compatibility.
   - Adapter/data-source tests next, while preserving the OpenStock boundary: MyStocks consumes and adapts data; it must not reintroduce provider development.
   - E2E/frontend tests only after current PM2/browser smoke truth is rechecked.
   - Performance/runtime/security tests after runtime and contract families are stable.
   - Untracked provenance review remains metadata-only until separately authorized.
4. Treat `b4-012-m3a-d1-e2e-browser-smoke-authorization` as a downstream authorization node; do not unblock it until the E2E/frontend no-source review is current.

## Boundaries

Strictly out of scope for this package:

- Source or test edits.
- File deletion or retirement.
- OpenSpec edits.
- OpenStock repository edits.
- Frontend runtime or backend runtime changes.
- Any untracked external card/worklog currently outside this package.

## Verification Plan

Before commit:

- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus staged verification and staged change detection
- OPENDOG verification

After commit:

- GitNexus analyze
- staged index empty
- parent node is `decision-prepared`
- B4.013 remains absent from active gates
