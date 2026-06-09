# Frontend View Redundant Page Review Checklist: `views/trading`

Date: 2026-05-10

Scope:
- `web/frontend/src/views/trading/Execution.vue`
- `web/frontend/src/views/trading/History.vue`
- `web/frontend/src/views/trading/Orders.vue`
- `web/frontend/src/views/trading/Positions.vue`

Purpose:
- Apply the frontend view governance redundant-page checklist to the legacy `views/trading/` focus group.
- Preserve the distinction between dead route entries, intentional compatibility wrappers, and honest static shells.
- Prevent archive approval before guard/test retirement and successor proof are complete.

## Current Truth Inputs

Runtime truth:
- `web/frontend/src/router/index.ts` does not dynamically import `views/trading/*.vue` as active route entries.
- Current canonical trade surfaces live under `web/frontend/src/views/trade/*` and selected ArtDeco trading tab owners.

Historical governance evidence:
- `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-20-manifest.yaml`
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/trading-legacy-canonical-wrapper-truth-audit.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-21-manifest.yaml`
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/trading-orders-execution-legacy-static-shell-truth-audit.md`

Guard and reference evidence:
- `web/frontend/tests/unit/config/trading-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/trading-style-normalization.spec.ts`
- `docs/FUNCTION_TREE.md` still records legacy trading workbench concepts.

## Page-Level Classification

| Page | Current implementation | Route status | Guard status | Reusable assets | Successor / owner | Lifecycle status | Archive decision |
|---|---|---:|---:|---|---|---|---|
| `views/trading/Execution.vue` | Honest static shell with links to verified trade surfaces | `dead` | `mainline-guarded` | No dynamic business asset; shell copy records deprecation boundary | No one-to-one owner; handoff to `/trade/terminal`, `/trade/signals`, `/trade/positions` | `candidate-review` | Not archive-approved |
| `views/trading/History.vue` | Thin compatibility wrapper around canonical trade history page | `redirect` | `mainline-guarded` | Wrapper compatibility only | `@/views/trade/History.vue` | `compat-retained` | Not archive-approved |
| `views/trading/Orders.vue` | Honest static shell with links to verified trade surfaces | `dead` | `mainline-guarded` | No dynamic business asset; shell copy records deprecation boundary | No one-to-one owner; handoff to `/trade/terminal`, `/trade/history`, `/trade/reconciliation` | `candidate-review` | Not archive-approved |
| `views/trading/Positions.vue` | Thin compatibility wrapper around ArtDeco trading positions owner | `redirect` | `mainline-guarded` | Wrapper compatibility only | `@/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue` | `compat-retained` | Not archive-approved |

## Redundant-Page Checklist

### `Execution.vue`

- Not menu referenced: pass.
- Not router dynamic import referenced: pass.
- Not active runtime owner: pass.
- Hidden reference check: incomplete; current guard specs still reference the `views/trading` directory.
- Function-tree status: legacy static shell with no one-to-one canonical execution owner.
- Reusable asset review: no reusable composable, data table, selector, metrics card, or verified business logic found.
- Successor proof: partial only; the page intentionally links to multiple canonical surfaces because no direct canonical owner exists.
- Archive eligibility: blocked by guard/test retention and lack of direct successor.

Decision: keep as `candidate-review`; do not mark as `archive-candidate`.

### `History.vue`

- Not menu referenced: pass.
- Not router dynamic import referenced: pass.
- Not standalone runtime owner: pass.
- Hidden reference check: incomplete; current guard specs still reference the `views/trading` directory.
- Function-tree status: compatibility wrapper.
- Reusable asset review: wrapper has no independent business logic to extract.
- Successor proof: direct successor exists at `@/views/trade/History.vue`.
- Archive eligibility: blocked until compatibility-retention requirements and guard/test migration are explicitly retired.

Decision: keep as `compat-retained`; do not mark as `archive-candidate`.

### `Orders.vue`

- Not menu referenced: pass.
- Not router dynamic import referenced: pass.
- Not active runtime owner: pass.
- Hidden reference check: incomplete; current guard specs still reference the `views/trading` directory.
- Function-tree status: legacy static shell with no one-to-one canonical orders owner.
- Reusable asset review: no reusable composable, data table, selector, metrics card, or verified business logic found.
- Successor proof: partial only; the page intentionally links to multiple canonical surfaces because no direct canonical owner exists.
- Archive eligibility: blocked by guard/test retention and lack of direct successor.

Decision: keep as `candidate-review`; do not mark as `archive-candidate`.

### `Positions.vue`

- Not menu referenced: pass.
- Not router dynamic import referenced: pass.
- Not standalone runtime owner: pass.
- Hidden reference check: incomplete; current guard specs still reference the `views/trading` directory.
- Function-tree status: compatibility wrapper.
- Reusable asset review: wrapper has no independent business logic to extract.
- Successor proof: direct wrapper target exists at `@/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue`.
- Archive eligibility: blocked until compatibility-retention requirements and guard/test migration are explicitly retired.

Decision: keep as `compat-retained`; do not mark as `archive-candidate`.

## Batch Conclusion

The `views/trading/` focus group contains two compatibility wrappers and two honest static shells. None of the four files qualifies for archive approval in this batch.

The correct next action is not file movement. The next action is to decide whether the project still needs `views/trading/` as a compatibility namespace. If it does not, retire or migrate `trading-mainline-gate.spec.ts`, `trading-style-normalization.spec.ts`, and relevant function-tree references first, then rerun this checklist before marking any file as `archive-candidate`.
