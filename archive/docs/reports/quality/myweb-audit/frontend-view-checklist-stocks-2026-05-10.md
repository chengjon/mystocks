# Frontend View Redundant Page Review Checklist: `views/stocks`

Date: 2026-05-10

Scope:
- `web/frontend/src/views/stocks/Activity.vue`
- `web/frontend/src/views/stocks/Concept.vue`
- `web/frontend/src/views/stocks/Industry.vue`
- `web/frontend/src/views/stocks/Portfolio.vue`
- `web/frontend/src/views/stocks/Screener.vue`
- `web/frontend/src/views/stocks/Watchlist.vue`

Related non-view assets observed in this batch:
- `web/frontend/src/views/stocks/stockScreenerData.ts`
- `web/frontend/src/views/stocks/__node_tests__/stockScreenerData.test.ts`
- `web/frontend/src/views/stocks/styles/{Concept,Portfolio,Watchlist}.scss`

Purpose:
- Apply the frontend view governance redundant-page checklist to the legacy `views/stocks/` focus group.
- Keep the indirect active screener implementation separate from retired static stocks child pages.
- Prevent accidental archive of shared stock-screening logic used by active routes and composables.

## Current Truth Inputs

Runtime truth:
- `web/frontend/src/router/index.ts` does not dynamically import `views/stocks/*.vue`.
- `web/frontend/src/views/watchlist/Screener.vue` imports and wraps `@/views/stocks/Screener.vue`, making `stocks/Screener.vue` an indirect active implementation.
- `web/frontend/src/composables/market/useDataAnalysis.ts` imports stock-universe helpers from `@/views/stocks/stockScreenerData`.

Historical governance evidence:
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/stocks-orphan-static-shells-truth-audit.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/stocks-portfolio-static-shell-truth-audit.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/watchlist-screener-audit.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/secondary-line-progress-summary.md`

Guard and reference evidence:
- `web/frontend/tests/unit/config/stocks-orphan-static-shells.spec.ts`
- `web/frontend/tests/unit/config/stocks-portfolio-static-shell.spec.ts`
- `web/frontend/tests/unit/config/console-log-cleanup-batch-30.spec.ts`
- `web/frontend/src/views/stocks/__node_tests__/stockScreenerData.test.ts`

## Page-Level Classification

| Page | Current implementation | Route status | Guard status | Reusable assets | Successor / owner | Lifecycle status | Archive decision |
|---|---|---:|---:|---|---|---|---|
| `views/stocks/Activity.vue` | Honest static shell | `dead` | `spec-guarded` | No dynamic business asset remains | `/trade/history` handoff | `candidate-review` | Not archive-approved |
| `views/stocks/Concept.vue` | Honest static shell | `dead` | `spec-guarded` | No dynamic business asset remains | `/data/concept` handoff | `candidate-review` | Not archive-approved |
| `views/stocks/Industry.vue` | Honest static shell | `dead` | `spec-guarded` | No dynamic business asset remains | `/data/industry` handoff | `candidate-review` | Not archive-approved |
| `views/stocks/Portfolio.vue` | Honest static shell | `dead` | `spec-guarded` | No dynamic business asset remains | `/trade/portfolio` handoff | `candidate-review` | Not archive-approved |
| `views/stocks/Screener.vue` | Active stock screener implementation wrapped by `/watchlist/screener` | `redirect` / indirect active | `spec-guarded` | Implementation asset, selector/filter state, stats strip, verified request/freshness handling | `views/watchlist/Screener.vue` currently wraps it | `compat-retained` / `absorb-assets` | Not archive-approved |
| `views/stocks/Watchlist.vue` | Honest static shell | `dead` | `spec-guarded` | No dynamic business asset remains | `/watchlist/manage` handoff | `candidate-review` | Not archive-approved |

## Redundant-Page Checklist

### `Activity.vue`

- Not menu referenced: pass.
- Not router dynamic import referenced: pass.
- Not active runtime owner: pass.
- Hidden reference check: incomplete; `stocks-orphan-static-shells.spec.ts` and historical audit docs still reference it.
- Function-tree status: retired stocks child page.
- Reusable asset review: no reusable composable, selector, metrics card, table schema, or verified trading logic remains after static-shell conversion.
- Successor proof: partial; static handoff points to `/trade/history`.
- Archive eligibility: blocked by direct static-shell spec and historical compatibility evidence.

Decision: keep as `candidate-review`; do not mark as `archive-candidate`.

### `Concept.vue`

- Not menu referenced: pass.
- Not router dynamic import referenced: pass.
- Not active runtime owner: pass.
- Hidden reference check: incomplete; `stocks-orphan-static-shells.spec.ts` and historical audit docs still reference it.
- Function-tree status: retired stocks child page.
- Reusable asset review: no reusable concept selector, stock-pool table, metrics card, or verified business logic remains after static-shell conversion.
- Successor proof: partial; static handoff points to `/data/concept`.
- Archive eligibility: blocked by direct static-shell spec and historical compatibility evidence.

Decision: keep as `candidate-review`; do not mark as `archive-candidate`.

### `Industry.vue`

- Not menu referenced: pass.
- Not router dynamic import referenced: pass.
- Not active runtime owner: pass.
- Hidden reference check: incomplete; `stocks-orphan-static-shells.spec.ts` and historical audit docs still reference it.
- Function-tree status: retired stocks child page.
- Reusable asset review: no reusable industry selector, stock-pool table, metrics card, or verified business logic remains after static-shell conversion.
- Successor proof: partial; static handoff points to `/data/industry`.
- Archive eligibility: blocked by direct static-shell spec and historical compatibility evidence.

Decision: keep as `candidate-review`; do not mark as `archive-candidate`.

### `Portfolio.vue`

- Not menu referenced: pass.
- Not router dynamic import referenced: pass.
- Not active runtime owner: pass.
- Hidden reference check: incomplete; `stocks-portfolio-static-shell.spec.ts`, `console-log-cleanup-batch-30.spec.ts`, and historical audit docs still reference it.
- Function-tree status: retired stocks child page.
- Reusable asset review: no reusable portfolio metrics, positions table, chart logic, action handler, or verified portfolio state remains after static-shell conversion.
- Successor proof: partial; static handoff points to `/trade/portfolio`.
- Archive eligibility: blocked by direct specs and historical compatibility evidence.

Decision: keep as `candidate-review`; do not mark as `archive-candidate`.

### `Screener.vue`

- Not menu referenced directly: pass, but active menu route `/watchlist/screener` wraps it through `views/watchlist/Screener.vue`.
- Not router dynamic import referenced directly: pass, but indirect active import exists.
- Not active runtime owner: fail; it is the active implementation behind `/watchlist/screener`.
- Hidden reference check: fail; `views/watchlist/Screener.vue`, historical watchlist audit docs, and stock-screener node tests reference the implementation or its helper module.
- Function-tree status: active compatibility implementation.
- Reusable asset review: contains reusable stock-universe screening assets, including filter state, request-id/freshness handling, stats display, row extraction, filter equality, and endpoint resolution.
- Successor proof: absent; the current successor would need to absorb this implementation into `views/watchlist/Screener.vue` or a shared layer first.
- Archive eligibility: blocked by active indirect runtime use and unabsorbed business assets.

Decision: keep as `compat-retained` and `absorb-assets`; do not mark as `archive-candidate`.

### `Watchlist.vue`

- Not menu referenced: pass.
- Not router dynamic import referenced: pass.
- Not active runtime owner: pass.
- Hidden reference check: incomplete; `stocks-orphan-static-shells.spec.ts` and historical audit docs still reference it.
- Function-tree status: retired stocks child page.
- Reusable asset review: no reusable watchlist table, filter, mutation action, or verified management logic remains after static-shell conversion.
- Successor proof: partial; static handoff points to `/watchlist/manage`.
- Archive eligibility: blocked by direct static-shell spec and historical compatibility evidence.

Decision: keep as `candidate-review`; do not mark as `archive-candidate`.

## Related Asset Notes

- `stockScreenerData.ts` is not redundant. It is imported by both `stocks/Screener.vue` and `composables/market/useDataAnalysis.ts`, and has dedicated node tests.
- If `stocks/Screener.vue` is later moved out of `views/stocks/`, move `stockScreenerData.ts` by responsibility, not by file adjacency alone. Candidate destinations must preserve both the watchlist screener and data-analysis consumers.
- The legacy SCSS files under `views/stocks/styles/` were observed as possible unused style assets during this batch, but they are outside this view checklist's archive decision. They require a separate hidden-reference and function-tree check before any move.

## Batch Conclusion

The `views/stocks/` focus group contains one indirect active implementation and five retired static shells. None of the six view files qualifies for archive approval in this batch.

The next safe action is not file movement. First decide whether `stocks/Screener.vue` should remain a compatibility implementation or be absorbed into the current `watchlist` / shared screening layer. Static shell pages can only become archive candidates after their static-shell specs and historical references are migrated or explicitly retired.
