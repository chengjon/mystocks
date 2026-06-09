# Frontend View Governance A4 Next Root Test Sandbox Selection

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: select the next A4 root demo/test/sandbox mutation or decision batch after OpenStock root duplicate archive.

This selection does not move files, edit runtime code, or retire tests.

## Selected Next Batch

```text
A4-root-test-sandbox-minimal-preflight
```

Proposed initial candidates:

- `web/frontend/src/views/MinimalTest.vue`
- `web/frontend/src/views/Test.vue`

## Why This Batch

After `OpenStockDemo.vue` root duplicate archive, the remaining root demo/test/sandbox pages split into two risk groups:

- Low-coupling test sandbox shells: `MinimalTest.vue`, `Test.vue`.
- Guarded or potentially reusable demo assets: `ArtDecoTest.vue`, `DataVisualizationShowcase.vue`, `KLineDemo.vue`, `MarketDataDemo.vue`, `SkeletonUsage.vue`, `SmartDataSourceTest.vue`, `StockAnalysisDemo.vue`.

The low-coupling group is the smallest safe next batch because current search did not find active router/menu/config/package ownership for `MinimalTest.vue` or `Test.vue`, while the other pages still have direct package targets, direct tests, direct style guards, workflow guards, or plausible market/data absorption value.

## Current Evidence

| Page | Router/menu/config/package status | Direct guard/test status | Initial lifecycle | Next action |
| --- | --- | --- | --- | --- |
| `MinimalTest.vue` | No active owner found in router/menu/config/package targeted search | Historical guard-map/inventory references only; no direct unit/e2e guard found in the focused scan | `archive-candidate/test-sandbox` | Final hidden-reference preflight |
| `Test.vue` | No active owner found in router/menu/config/package targeted search | Historical guard-map/inventory references only; no direct unit/e2e guard found in the focused scan | `archive-candidate/test-sandbox` | Final hidden-reference preflight |
| `ArtDecoTest.vue` | `package.json` direct `lint:artdeco:changed` target-file entry | Guard-map/package target coupling | `candidate-review/demo-sandbox` | Exclude until guard retirement plan exists |
| `DataVisualizationShowcase.vue` | `package.json` direct target-file entry | `root-demo-style-entrypoints.spec.ts` and `console-log-cleanup-batch-24.spec.ts` | `candidate-review/demo-sandbox` | Exclude until guard migration/retirement plan exists |
| `KLineDemo.vue` | No active router/menu owner found | Historical guard-map/inventory references; K-line feature overlap remains | `absorb-assets` | Exclude until market/technical successor decision exists |
| `MarketDataDemo.vue` | No active router/menu owner found | Historical guard-map/inventory references; market/data API-demo value remains | `absorb-assets` | Exclude until market/data successor decision exists |
| `SkeletonUsage.vue` | `package.json` direct target-file entry | Tokenization and workflow guards | `retain-as-demo` | Exclude until skeleton docs/guard ownership is replaced |
| `SmartDataSourceTest.vue` | `package.json` direct target-file entry | `root-demo-style-entrypoints.spec.ts` | `absorb-assets` | Exclude until data-source diagnostic successor decision exists |
| `StockAnalysisDemo.vue` | `package.json` direct target-file entry | Direct `src/views/__tests__/StockAnalysisDemo.spec.ts`, style normalization, and root-demo style guard | `retain-as-demo` / static shell | Exclude until static-shell guard retirement is explicitly approved |

## Required Preflight For Next Batch

Before moving either selected file:

1. Run GitNexus impact for `MinimalTest.vue` and `Test.vue`.
2. Run exact active-reference search for both names across `web/frontend/src`, `web/frontend/tests`, `web/frontend/package.json`, and current governance docs.
3. Confirm no router/menu/config/package owner.
4. Confirm no direct spec reads or imports the files.
5. Record `no-successor-needed` or successor rationale for each file.

## Candidate Execution Profile

If preflight stays clear:

- Move only `MinimalTest.vue` and `Test.vue` to `archive/web/frontend/src/views/root-sandbox/test-sandbox/`.
- Add archive README for the two test sandbox shells.
- Do not touch `ArtDecoTest.vue`, `KLineDemo.vue`, `MarketDataDemo.vue`, `SkeletonUsage.vue`, `DataVisualizationShowcase.vue`, `SmartDataSourceTest.vue`, or `StockAnalysisDemo.vue`.
- Do not modify router/menu/package/test files unless the preflight finds a direct owner that must be retired in the same batch.

## Next Task

```text
3.41 Prepare A4-root-test-sandbox-minimal-preflight without moving files.
```
