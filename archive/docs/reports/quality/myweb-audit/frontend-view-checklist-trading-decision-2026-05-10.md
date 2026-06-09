# Frontend View Redundant Page Review Checklist: `views/trading-decision`

Date: 2026-05-10

Scope:
- `web/frontend/src/views/trading-decision/DecisionHeader.vue`
- `web/frontend/src/views/trading-decision/DecisionOrders.vue`
- `web/frontend/src/views/trading-decision/DecisionPortfolio.vue`
- `web/frontend/src/views/trading-decision/DecisionPositions.vue`

Purpose:
- Apply the frontend view governance redundant-page checklist to the legacy `views/trading-decision/` focus group.
- Separate compatibility wrappers from honest static shells.
- Prevent archive approval while mainline guards, cleanup specs, and historical compatibility evidence still exist.

## Current Truth Inputs

Runtime truth:
- `web/frontend/src/router/index.ts` does not dynamically import `views/trading-decision/*.vue` as active route entries.
- Canonical trade truth is provided by `web/frontend/src/views/trade/*` and approved ArtDeco trading surfaces.

Historical governance evidence:
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/trading-decision-active-panel-canonical-wrapper-truth-audit.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/trading-decision-orders-static-shell-truth-audit.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/trading-decision-header-static-shell-truth-audit.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/secondary-line-progress-summary.md`

Guard and reference evidence:
- `web/frontend/tests/unit/config/trading-decision-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/console-log-cleanup-batch-36.spec.ts`
- `web/frontend/tests/unit/config/console-log-cleanup-batch-37.spec.ts`
- `docs/FUNCTION_TREE.md` still records `旧交易决策组件`.

## Page-Level Classification

| Page | Current implementation | Route status | Guard status | Reusable assets | Successor / owner | Lifecycle status | Archive decision |
|---|---|---:|---:|---|---|---|---|
| `views/trading-decision/DecisionHeader.vue` | Honest static header shell with canonical handoff links | `dead` | `mainline-guarded` | No dynamic business asset; shell records deprecation boundary | No one-to-one owner; handoff to `/trade/terminal`, `/trade/positions`, `/trade/portfolio` | `candidate-review` | Not archive-approved |
| `views/trading-decision/DecisionOrders.vue` | Honest static orders shell with canonical handoff links | `dead` | `mainline-guarded` | No dynamic business asset; shell records deprecation boundary | No one-to-one owner; handoff to `/trade/terminal`, `/trade/history`, `/trade/reconciliation` | `candidate-review` | Not archive-approved |
| `views/trading-decision/DecisionPortfolio.vue` | Thin wrapper around canonical trade portfolio page | `redirect` | `mainline-guarded` | Wrapper compatibility only | `@/views/trade/Portfolio.vue` | `compat-retained` | Not archive-approved |
| `views/trading-decision/DecisionPositions.vue` | Thin wrapper around canonical trade center positions page with empty positions prop | `redirect` | `mainline-guarded` | Wrapper compatibility only | `@/views/trade/Center.vue` | `compat-retained` | Not archive-approved |

## Redundant-Page Checklist

### `DecisionHeader.vue`

- Not menu referenced: pass.
- Not router dynamic import referenced: pass.
- Not active runtime owner: pass.
- Hidden reference check: incomplete; current mainline and historical docs still reference the `views/trading-decision` directory.
- Function-tree status: legacy decision header shell with no one-to-one canonical owner.
- Reusable asset review: no reusable composable, selector, metrics card, table schema, or verified trading rule found.
- Successor proof: partial only; shell intentionally links to multiple canonical surfaces.
- Archive eligibility: blocked by guard/test retention and lack of direct successor.

Decision: keep as `candidate-review`; do not mark as `archive-candidate`.

### `DecisionOrders.vue`

- Not menu referenced: pass.
- Not router dynamic import referenced: pass.
- Not active runtime owner: pass.
- Hidden reference check: incomplete; `console-log-cleanup-batch-37.spec.ts` still reads this file directly.
- Function-tree status: legacy decision orders shell with no one-to-one canonical order owner.
- Reusable asset review: no reusable composable, selector, metrics card, table schema, or verified trading rule found.
- Successor proof: partial only; shell intentionally links to multiple canonical surfaces.
- Archive eligibility: blocked by direct test reference, guard retention, and lack of direct successor.

Decision: keep as `candidate-review`; do not mark as `archive-candidate`.

### `DecisionPortfolio.vue`

- Not menu referenced: pass.
- Not router dynamic import referenced: pass.
- Not standalone runtime owner: pass.
- Hidden reference check: incomplete; current mainline and historical docs still reference the `views/trading-decision` directory.
- Function-tree status: compatibility wrapper.
- Reusable asset review: wrapper has no independent business logic to extract.
- Successor proof: direct successor exists at `@/views/trade/Portfolio.vue`.
- Archive eligibility: blocked until compatibility-retention requirements and guard/test migration are explicitly retired.

Decision: keep as `compat-retained`; do not mark as `archive-candidate`.

### `DecisionPositions.vue`

- Not menu referenced: pass.
- Not router dynamic import referenced: pass.
- Not standalone runtime owner: pass.
- Hidden reference check: incomplete; `console-log-cleanup-batch-36.spec.ts` still reads this file directly.
- Function-tree status: compatibility wrapper.
- Reusable asset review: wrapper has no independent business logic to extract.
- Successor proof: direct wrapper target exists at `@/views/trade/Center.vue`.
- Archive eligibility: blocked until compatibility-retention requirements and direct cleanup specs are explicitly retired or migrated.

Decision: keep as `compat-retained`; do not mark as `archive-candidate`.

## Batch Conclusion

The `views/trading-decision/` focus group contains two compatibility wrappers and two honest static shells. None of the four files qualifies for archive approval in this batch.

The next safe action is to decide whether the legacy decision namespace still has an intentional compatibility role. If it does not, first retire or migrate `trading-decision-mainline-gate.spec.ts`, `console-log-cleanup-batch-36.spec.ts`, `console-log-cleanup-batch-37.spec.ts`, and function-tree references, then rerun this checklist before marking any file as `archive-candidate`.
