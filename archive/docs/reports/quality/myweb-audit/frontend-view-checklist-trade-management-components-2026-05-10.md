# Frontend View Checklist - Trade Management Static Shell Components - 2026-05-10

## Scope

This is a read-only redundant-page checklist batch for:

- `web/frontend/src/views/trade-management/components/PortfolioOverview.vue`
- `web/frontend/src/views/trade-management/components/PositionsTab.vue`
- `web/frontend/src/views/trade-management/components/StatisticsTab.vue`
- `web/frontend/src/views/trade-management/components/TradeDialog.vue`
- `web/frontend/src/views/trade-management/components/TradeHistoryTab.vue`

No files were moved, archived, or deleted.

## Shared Metadata

| Field | Value |
|---|---|
| Current directory | `web/frontend/src/views/trade-management/components/` |
| Previous historical classification | Orphan trade-management child components repaired into honest static shells |
| Previous classification source | `docs/reports/quality/myweb-audit/audit-20260426-02/pages/trade-management-orphan-components-static-shell-truth-audit.md` |
| Previous classification upheld or changed? | Upheld |
| Route status | `dead` for route, but `redirect`/compatibility at barrel-export level |
| Guard status | `mainline-guarded` |
| Proposed lifecycle status | `candidate-review` |
| Reviewer | Codex |
| Review date | 2026-05-10 |

## Page Summary

| Page | Current content | Canonical handoff | Lifecycle decision |
|---|---|---|---|
| `PortfolioOverview.vue` | Honest static shell, no portfolio fixtures or fake PnL | `/trade/portfolio` | `candidate-review` |
| `PositionsTab.vue` | Honest static shell, no fallback positions or quick-sell state | `/trade/positions` | `candidate-review` |
| `StatisticsTab.vue` | Honest static shell, no synthetic charts/statistics | `/trade/history` | `candidate-review` |
| `TradeDialog.vue` | Honest static shell, no local order form or submit API | `/trade/terminal` | `candidate-review` |
| `TradeHistoryTab.vue` | Honest static shell, no local history request/pagination | `/trade/history` | `candidate-review` |

## Truth-Source Checks

| Check | Result | Evidence |
|---|---|---|
| Dynamically imported by `router/index.ts` | No | Not in current routed view import set |
| Reachable through compatibility route or alias | No route; yes compatibility export | `components/index.ts` re-exports all five components |
| Represented by `MenuConfig.ts` | No | Current trade menu uses canonical `/trade/*` routes |
| Intentional hidden route, blank page, detail page, or special shell | No active route; yes guarded static shell | Files intentionally degrade to `legacy-static-shell` with `/trade/*` handoffs |
| Referenced by layout tabs, page registries, generated page config | No active route/layout registry reference found | Guard map found only a barrel export in runtime source |
| Referenced by docs/runtime string links/examples expected to work | Yes, historical docs/audit references | Multiple historical docs and audit artifacts reference these files |

## Functional Coverage Checks

| Check | Result | Evidence |
|---|---|---|
| Workflow not covered by canonical route page | No current evidence | Static shell copy points users to canonical `/trade/*` surfaces |
| Visible business-domain capability | No | Functional capability is now owned by canonical `/trade/portfolio`, `/trade/positions`, `/trade/history`, and `/trade/terminal` |
| Selector behavior, tab orchestration, or cross-slice state | No | Files contain static template and scoped SCSS only |
| Domain calculation rules | No | Prior local trading semantics were removed by secondary-batch-49 |
| Compatibility behavior for tests/docs/historical links | Yes | Existing specs assert static shell degradation and mainline changed-scope coverage |

## Reusable Asset Checks

| Asset class | Present? | Absorption target / rationale |
|---|---|---|
| Reusable UI component | No | Repeated static shell markup only |
| Shared composable or API normalization | No | No script imports |
| Request provenance, freshness, runtime status | No | Static shell only |
| Metric cards, KPI grid, stats strip, summary logic | No | Explicitly removed |
| Table columns, filters, selectors, query schema | No | Explicitly removed |
| Domain calculation rule | No | Explicitly removed |

## Guard And Test Checks

Discovery commands used:

```bash
rg -n "src/views/trade-management|@/views/trade-management|views/trade-management|trade-management/components|PortfolioOverview.vue|PositionsTab.vue|StatisticsTab.vue|TradeDialog.vue|TradeHistoryTab.vue" web/frontend/src web/frontend/tests docs --glob '!**/.claude/**'
sed -n '1,220p' web/frontend/tests/unit/config/trade-management-mainline-gate.spec.ts
sed -n '1,220p' web/frontend/tests/unit/config/trade-management-components-normalization.spec.ts
sed -n '1,220p' web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts
sed -n '1,220p' web/frontend/src/views/trade-management/components/index.ts
```

| Check | Result | Evidence |
|---|---|---|
| Referenced by `*-mainline-gate.spec.ts` | Yes | `trade-management-mainline-gate.spec.ts` requires root `src/views/trade-management` changed-scope coverage |
| Imported or read by other `*.spec.ts` | Yes | `trade-management-components-normalization.spec.ts` reads all five files |
| Test asserts style/class/route/runtime behavior | Yes | Tests assert `legacy-static-shell`, canonical handoff, no trade API, no fallback rows, no fake chart/history/order semantics |
| Relevant guard migrated to canonical successor | No | Guards still point at `src/views/trade-management` and component paths |
| Guard retirement rationale recorded | No | Not yet recorded; required before archive |

## Successor Decision

| Field | Value |
|---|---|
| Canonical successor page | `/trade/portfolio`, `/trade/positions`, `/trade/history`, `/trade/terminal` depending on component |
| Successor covers all useful functionality? | Yes for current verified trade truth; no independent component semantics should remain |
| Missing functionality to absorb | None identified from these static shells |
| No-successor-needed rationale | Not applicable because canonical `/trade/*` successors are recorded |

## Redundant Eligibility Gate

| Required condition | Result | Evidence |
|---|---|---|
| Not part of active routed-page baseline | Pass | Not in router dynamic import set |
| Not represented by visible menu | Pass | Menu uses canonical `/trade/*` entries |
| Not an intentional hidden route or special shell | Fail | They are intentional guarded legacy static shells |
| Provides no unique business-domain function coverage | Pass | Static handoff shells only |
| All useful assets absorbed or explicitly rejected | Pass | Prior local semantics removed; no reusable assets remain |
| No active static import reference | Fail / unresolved | `components/index.ts` still re-exports all five components |
| No active dynamic import reference | Pass | No router dynamic imports found |
| No layout tab or page registry reference | Pass | No active layout/tab registry ref found |
| No page-config reference | Pass | No active page-config ref found |
| No documentation or example link expected to work | Fail / unresolved | Historical docs and audits still reference these files |
| No runtime string-link or feature-flag reference | Pass | None found beyond barrel export |
| No test guard or spec reference, or migration/retirement recorded | Fail | Mainline and normalization specs still guard these files |
| Successor or `no-successor-needed` rationale recorded | Pass | Canonical `/trade/*` successors recorded |

## Final Decision

| Field | Value |
|---|---|
| Lifecycle decision | Keep as `candidate-review` |
| Execution action | Needs barrel export review plus guard/test retirement or migration before any archive proposal |
| Archive target | None approved |
| Archive batch ID / approval reference | None |

## Conclusion

These five trade-management components are not useful as product components anymore, but they are still guarded compatibility/static-shell assets. They are not `archive-candidate` until:

1. `web/frontend/src/views/trade-management/components/index.ts` is reviewed and either migrated or retired.
2. `trade-management-mainline-gate.spec.ts` is migrated or retired.
3. `trade-management-components-normalization.spec.ts` is migrated or retired.
4. `monitoring-system-strategy-style-normalization.spec.ts` no longer references `TradeHistoryTab.vue` or has a recorded retention reason.
5. Historical docs are either updated to canonical `/trade/*` pages or marked historical-only.
6. The redundant eligibility gate is re-run and all rows pass.

