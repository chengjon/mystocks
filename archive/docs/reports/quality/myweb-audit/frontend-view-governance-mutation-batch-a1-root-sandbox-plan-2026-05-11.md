# Frontend View Governance Mutation Batch A1 Plan: Root Sandbox Triage

Date: 2026-05-11

Scope: proposed first narrow mutation batch for `openspec/changes/update-frontend-view-governance` section `3`.

This is a proposal / batch plan only. It does not move files, delete files, edit Vue runtime code, retire tests, or change routes.

## Batch Selection

Selected candidate from the 2b closeout options: Option A, narrowed to A1 root sandbox triage.

Reason for narrowing:

- The full Option A set contains files with direct test/script guards, such as `SkeletonUsage.vue`, `DataVisualizationShowcase.vue`, and `SmartDataSourceTest.vue`.
- A first mutation batch should avoid files with active guard coupling until the archive workflow is proven on a smaller, lower-risk set.
- This A1 batch targets root demo/test sandbox pages with no current router/menu ownership and no direct source importer found by focused static search.

## Proposed Exact Files

Initial A1 candidate files:

| File | Current lifecycle | Router/menu status | Known guard/reference status | Proposed mutation disposition |
| --- | --- | --- | --- | --- |
| `web/frontend/src/views/MinimalTest.vue` | `candidate-review/test-sandbox` | No current route/menu owner | Inventory/guard-map references only found in current evidence pass | Archive-candidate after final hidden-reference check |
| `web/frontend/src/views/Test.vue` | `candidate-review/test-sandbox` | No current route/menu owner | Inventory/guard-map references only found in current evidence pass | Archive-candidate after final hidden-reference check |
| `web/frontend/src/views/KLineDemo.vue` | `candidate-review/demo-sandbox` | No current route/menu owner | Inventory/guard-map references; K-line concept overlaps canonical market/technical routes | Archive-candidate with successor `views/market/Technical.vue` / detail graphics |
| `web/frontend/src/views/PageTitleDemo.vue` | `candidate-review/demo-sandbox` | No current route/menu owner | Inventory/guard-map references; page-title/shared-composable demo | Archive-candidate after confirming title behavior is covered elsewhere or `no-successor-needed` |
| `web/frontend/src/views/ArtDecoTest.vue` | `candidate-review/demo-sandbox` | No current route/menu owner | `lint:artdeco:changed` currently includes direct target-file guard | Do not archive in A1 unless package-script guard is migrated in same batch |
| `web/frontend/src/views/OpenStockDemo.vue` | `candidate-review/demo-sandbox` | No current route/menu owner | Inventory/guard-map references; distinct from `views/demo/OpenStockDemo.vue` | Hold for A2 unless OpenStock demo ownership is decided together |
| `web/frontend/src/views/MarketDataDemo.vue` | `candidate-review/demo-sandbox` | No current route/menu owner | Selector/API demo/fallback-literal risk; possible data/market absorption value | Hold for A2/A3 absorption review |

Excluded from A1:

- `SkeletonUsage.vue`: directly referenced by `skeleton-usage-tokenization.spec.ts`, workflow gates, and `lint:artdeco:changed`.
- `DataVisualizationShowcase.vue`: directly referenced by root-demo style and console-cleanup guards.
- `SmartDataSourceTest.vue`: directly referenced by root-demo style guard and `lint:artdeco:changed`.
- `StockAnalysisDemo.vue`: already has historical static-shell repair and direct spec; should be handled with static-shell guard retirement.
- `FreqtradeDemo.vue`, `TdxpyDemo.vue`, `PyprofilingDemo.vue`: parent shell files with child/support assets; must be handled as parent-child batches.

## Proposed A1 Mutation Rules

Before any file move:

- Re-run focused static search for every candidate across `web/frontend/src`, `web/frontend/tests`, `web/frontend/package.json`, `docs`, and `openspec`.
- Confirm no router import, menu entry, dynamic import, package script target, test read, or style-source spec still depends on the file.
- Record successor or `no-successor-needed` per file.
- If a candidate is still referenced by a test or package script, remove it from A1 rather than expanding the batch.

Allowed mutation if approved:

- Move only final archive-approved A1 files to the governed frontend view archive location defined by the accepted governance rule.
- Do not edit canonical route owners.
- Do not change `router/index.ts` or `MenuConfig.ts` unless a hidden reference is discovered and explicitly addressed.
- Do not touch demo parent shells or nested demo directories in this batch.

Not allowed in A1:

- No business-route refactor.
- No broad `views/styles` cleanup.
- No guard retirement for files outside the final A1 set.
- No physical deletion.

## Required Validation

Pre-mutation:

```bash
rg -n "MinimalTest|Test\\.vue|KLineDemo|PageTitleDemo|ArtDecoTest|OpenStockDemo|MarketDataDemo" web/frontend/src web/frontend/tests web/frontend/package.json docs openspec
```

If runtime files are moved:

```bash
openspec validate update-frontend-view-governance --strict
cd web/frontend && npm run lint:artdeco
cd web/frontend && npx vitest run tests/unit/config/root-demo-style-entrypoints.spec.ts tests/unit/workflows/ci-workflow-gates.spec.ts
```

If no package/test guard is affected, the Vitest set can be reduced to the specific guards discovered by the pre-mutation search.

Post-mutation:

- Verify `router/index.ts` and `MenuConfig.ts` still have no references to moved files.
- Verify no archive path is imported by menu/router.
- Record actual command results, not assumed pass counts.

## Approval Boundary

This plan selects the first proposed mutation batch but does not itself approve mutation.

Recommended approval wording for execution:

`批准执行 A1 root sandbox triage，仅移动最终通过隐藏引用检查的 root sandbox 文件，不处理 SkeletonUsage/DataVisualizationShowcase/SmartDataSourceTest/StockAnalysisDemo 和 demo parent shells。`

Without that explicit approval, section `3.0` should remain open and no files should be moved.
