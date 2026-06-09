# Frontend View Inventory Correction: `views/ai/BatchAnalysis.vue`

Date: 2026-05-10

Scope:
- `web/frontend/src/views/ai/BatchAnalysis.vue`
- `web/frontend/src/views/ai/composables/useBatchAnalysisWorkbench.ts`

Purpose:
- Correct the stale high-priority inventory classification for `views/ai/BatchAnalysis.vue`.
- Prevent an active canonical route from entering redundant-page archive review.

## Original Inventory Signal

`docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.md` listed:

| Page | Classification | Priority | Hit features |
|---|---|---:|---|
| `web/frontend/src/views/ai/BatchAnalysis.vue` | `候选待审` | `H` | `selector`, `fallback-literal`, `shared-composable` |

This classification is stale for cleanup purposes because the page is currently an active AI-domain route.

## Current Runtime Truth

Router evidence:
- `web/frontend/src/router/index.ts` registers `path: 'batch'`, `name: 'ai-batch'`, and `component: () => import('@/views/ai/BatchAnalysis.vue')`.

Navigation evidence:
- `web/frontend/src/config/menu.config.js` exposes `id: 'ai-batch'`, `title: '批量分析'`, and `path: '/ai/batch'`.

Function-tree evidence:
- `docs/FUNCTION_TREE.md` records `views/ai/BatchAnalysis.vue` as the canonical frontend entry for batch backtest, batch screening, and batch monitoring evidence.

Test evidence:
- `web/frontend/tests/unit/config/ai-route-canonical-paths.spec.ts` asserts the canonical route and navigation path.
- `web/frontend/src/views/ai/__tests__/BatchAnalysis.spec.ts` verifies page rendering, submit wiring, task selection, empty state, and safety copy.
- `web/frontend/tests/e2e/ai-batch-analysis.spec.ts` covers `/ai/batch` route behavior.

## Classification Correction

| Page | Previous inventory status | Corrected status | Route status | Guard status | Archive decision |
|---|---|---|---|---|---|
| `views/ai/BatchAnalysis.vue` | `候选待审` / `H` | `canonical-active` | `active` | `route-and-e2e-guarded` | Not eligible for archive review |

## Asset Notes

- `useBatchAnalysisWorkbench.ts` is an active view-local composable for `BatchAnalysis.vue`, not a redundant shared helper.
- The page intentionally owns selector-like operation selection and batch task state because `/ai/batch` is the canonical batch-analysis workbench.
- The safety copy is product semantics, not fallback noise: it clarifies that batch analysis outputs are analytical evidence, not automated trading or scheduler mutation.

## Decision

Do not include `views/ai/BatchAnalysis.vue` in redundant-page checklist or archive-candidate batches.

If future governance wants to move this implementation, it must be handled as a route migration with a declared successor, not as cleanup of an unrouted or redundant page.
