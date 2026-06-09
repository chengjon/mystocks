# Frontend View Checklist: Demo Examples Batch

Date: 2026-05-10

Scope:
- `web/frontend/src/views/examples/*`
- `web/frontend/src/views/examples/composables/*`
- `web/frontend/src/views/freqtrade-demo/*`
- `web/frontend/src/views/tdxpy-demo/*`

This checklist is part of `update-frontend-view-governance`. It records lifecycle evidence only. It does not approve file moves, archive moves, or deletion.

## Summary

| Group | Files Reviewed | Route/Menu Status | Runtime/Code References | Guard Status | Lifecycle Result |
| --- | ---: | --- | --- | --- | --- |
| `views/examples` | 3 Vue + 1 composable | Not in current router or menu | README/docs/example references; `pageConfigExtended.example.ts` references migrated composable | `examples-mainline-gate` plus 3 style-source specs | `candidate-review/demo-example-asset` |
| `views/freqtrade-demo` | 6 Vue tabs | Not in current router or menu | Imported by root `views/FreqtradeDemo.vue` | `freqtrade-demo-mainline-gate` | `candidate-review/demo-tab-asset` |
| `views/tdxpy-demo` | 5 Vue tabs | Not in current router or menu | Imported by root `views/TdxpyDemo.vue` | `tdxpy-demo-mainline-gate` | `candidate-review/demo-tab-asset` |

No file in this batch is `archive-approved`.

## Evidence

### Menu And Router

- `web/frontend/src/router/index.ts` has no active dynamic import for `views/examples`, `views/freqtrade-demo`, or `views/tdxpy-demo`.
- `web/frontend/src/layouts/MenuConfig.ts` has no active menu owner for these demo/example directories.
- Historical docs still mention old `/freqtrade-demo` and `/tdxpy-demo` routes, but the current router truth does not register those paths.

### Internal References

- `views/freqtrade-demo/*.vue` are direct child tabs of `web/frontend/src/views/FreqtradeDemo.vue`.
- `views/tdxpy-demo/*.vue` are direct child tabs of `web/frontend/src/views/TdxpyDemo.vue`.
- `views/examples/PageConfigExample.vue` and `views/examples/WebSocketConfigExample.vue` are example pages documented by `views/examples/README.md`.
- `views/examples/TradingDashboard.migrated.vue` and `views/examples/composables/useTradingDashboard.migrated.ts` are explicit migration examples, not canonical `/trade/terminal` implementation.
- `web/frontend/src/config/pageConfigExtended.example.ts` references `@/views/examples/composables/useTradingDashboard.migrated` as example guidance.

### Guard And Test References

- `web/frontend/tests/unit/config/examples-mainline-gate.spec.ts` requires `--target-dir src/views/examples --changed-from-git`.
- `web/frontend/tests/unit/config/examples-page-config-style-source.spec.ts` guards `PageConfigExample.vue`.
- `web/frontend/tests/unit/config/examples-trading-dashboard-style-source.spec.ts` guards `TradingDashboard.migrated.vue`.
- `web/frontend/tests/unit/config/examples-websocket-style-source.spec.ts` guards `WebSocketConfigExample.vue`.
- `web/frontend/tests/unit/config/freqtrade-demo-mainline-gate.spec.ts` requires `--target-dir src/views/freqtrade-demo --changed-from-git`.
- `web/frontend/tests/unit/config/tdxpy-demo-mainline-gate.spec.ts` requires `--target-dir src/views/tdxpy-demo --changed-from-git`.
- `web/frontend/package.json` includes all three directories in `lint:artdeco:changed`.

## Per-File Classification

| File | Selector | Stats/Metric Cards | Shared Composable | Current Result | Successor / Absorption Hint |
| --- | --- | --- | --- | --- | --- |
| `views/examples/PageConfigExample.vue` | No | No | No | `candidate-review/demo-example-asset` | Keep as page-config usage example until example-doc relocation is approved |
| `views/examples/WebSocketConfigExample.vue` | Yes | No | No | `candidate-review/demo-example-asset` | Absorb useful WebSocket config guidance into formal docs/shared connection guidance before archive |
| `views/examples/TradingDashboard.migrated.vue` | Yes | No | Yes | `candidate-review/demo-migration-asset` | Do not merge into `/trade/terminal`; use only as migration reference |
| `views/examples/composables/useTradingDashboard.migrated.ts` | Yes | No | Local example composable | `candidate-review/demo-support-asset` | Keep paired with migrated example until example asset relocation is approved |
| `views/freqtrade-demo/FreqOverviewTab.vue` | Yes | No | No | `candidate-review/demo-tab-asset` | Only removable with root `FreqtradeDemo.vue` decision |
| `views/freqtrade-demo/FreqStrategyTab.vue` | Yes | No | No | `candidate-review/demo-tab-asset` | Only removable with root `FreqtradeDemo.vue` decision |
| `views/freqtrade-demo/FreqBacktestTab.vue` | Yes | No | No | `candidate-review/demo-tab-asset` | Only removable with root `FreqtradeDemo.vue` decision |
| `views/freqtrade-demo/FreqConfigTab.vue` | Yes | No | No | `candidate-review/demo-tab-asset` | Only removable with root `FreqtradeDemo.vue` decision |
| `views/freqtrade-demo/FreqWebuiTab.vue` | Yes | No | No | `candidate-review/demo-tab-asset` | Only removable with root `FreqtradeDemo.vue` decision |
| `views/freqtrade-demo/FreqStatusTab.vue` | Yes | No | No | `candidate-review/demo-tab-asset` | Only removable with root `FreqtradeDemo.vue` decision |
| `views/tdxpy-demo/TdxOverviewTab.vue` | Yes | No | No | `candidate-review/demo-tab-asset` | Only removable with root `TdxpyDemo.vue` decision |
| `views/tdxpy-demo/TdxInstallTab.vue` | Yes | No | No | `candidate-review/demo-tab-asset` | Only removable with root `TdxpyDemo.vue` decision |
| `views/tdxpy-demo/TdxApiTab.vue` | Yes | No | No | `candidate-review/demo-tab-asset` | Only removable with root `TdxpyDemo.vue` decision |
| `views/tdxpy-demo/TdxExportTab.vue` | Yes | No | No | `candidate-review/demo-tab-asset` | Only removable with root `TdxpyDemo.vue` decision |
| `views/tdxpy-demo/TdxStatusTab.vue` | Yes | No | No | `candidate-review/demo-tab-asset` | Only removable with root `TdxpyDemo.vue` decision |

## Archive Eligibility

Current eligibility: not approved.

Blocking conditions:
- Demo tab files still have root demo wrappers as direct importers.
- Directory-level mainline gates still require these paths in `lint:artdeco:changed`.
- Example pages have explicit style-source tests and documentation references.
- Existing restructure spec and historical reports mention a future deprecated/demo relocation model, but that relocation has not been executed in the current repo truth.

Required before any archive move:
- Decide whether root `FreqtradeDemo.vue` and `TdxpyDemo.vue` are retained, absorbed, or archived.
- Retire or migrate the directory-level mainline gates in the same approved mutation batch.
- Move example docs/references together with example assets, or replace them with canonical documentation.
- Record a successor or `no-successor-needed` rationale for every moved file.

## Governance Conclusion

This batch confirms that `examples`, `freqtrade-demo`, and `tdxpy-demo` are outside the current canonical menu/router tree, but they are not safe deletion or archive targets yet. They remain demo/example assets under `candidate-review` until a dedicated demo relocation or archive mutation batch updates wrappers, guards, and documentation together.
