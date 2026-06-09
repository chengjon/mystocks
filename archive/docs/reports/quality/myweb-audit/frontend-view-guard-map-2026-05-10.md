# Frontend View Guard Map - 2026-05-10

## Scope

Read-only guard/reference map for `update-frontend-view-governance` Step 0. No frontend files were moved, archived, or deleted.

## Summary

- generated_at: `2026-05-10T02:22:50.997Z`
- scanned_files: `1833`
- mainline_gate_specs: `22`
- total_references: `4452`
- by_source_type: `spec=348 / mainline-gate=121 / runtime-src=157 / docs=3826`
- by_kind: `route-detail-link=195 / alias-view-import=247 / src-view-string=3947 / target-dir=31 / target-file=32`
- The current router includes a `detail` route group (`/detail/graphics/:symbol` and `/detail/news/:symbol`), so `route-detail-link` matches must be interpreted per source, not assumed stale by default.

## Mainline Gate Specs

- `web/frontend/tests/unit/config/advanced-analysis-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/announcement-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/data-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/demo-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/demo-styles-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/errors-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/examples-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/freqtrade-demo-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/lighthouse-mainline-gates.spec.ts`
- `web/frontend/tests/unit/config/openstock-components-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/pyprofiling-components-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/pyprofiling-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/risk-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/settings-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/stock-analysis-components-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/strategy-styles-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/tdxpy-demo-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/technical-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/testing-mainline-gates.spec.ts`
- `web/frontend/tests/unit/config/trade-management-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/trading-decision-mainline-gate.spec.ts`
- `web/frontend/tests/unit/config/trading-mainline-gate.spec.ts`

## Zero-Router-Reference Focus Dirs

| Directory | Hit count | Guard/reference files |
|---|---:|---|
| `stocks/` | 49 | `docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-51-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/batches/watchlist-batch-01-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/batches/watchlist-batch-03-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/batches/watchlist-batch-04-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/pages/stocks-orphan-static-shells-truth-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/pages/stocks-portfolio-static-shell-truth-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/pages/watchlist-screener-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/pages/watchlist-screener-request-and-envelope-truth-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/pages/watchlist-screener-summary-truth-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/secondary-line-progress-summary.md`<br>`docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.json`<br>`docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.md`<br>`web/frontend/src/composables/market/useDataAnalysis.ts`<br>`web/frontend/src/views/watchlist/Screener.vue`<br>`web/frontend/tests/unit/config/console-log-cleanup-batch-30.spec.ts`<br>`web/frontend/tests/unit/config/stocks-orphan-static-shells.spec.ts`<br>`web/frontend/tests/unit/config/stocks-portfolio-static-shell.spec.ts` |
| `trading/` | 91 | `docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-20-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-21-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-25-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-26-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-46-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/pages/trading-decision-active-panel-canonical-wrapper-truth-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/pages/trading-decision-header-static-shell-truth-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/pages/trading-decision-orders-static-shell-truth-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/pages/trading-legacy-canonical-wrapper-truth-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/pages/trading-orders-execution-legacy-static-shell-truth-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/secondary-line-progress-summary.md`<br>`docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.json`<br>`docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.md`<br>`web/frontend/tests/unit/config/console-log-cleanup-batch-36.spec.ts`<br>`web/frontend/tests/unit/config/console-log-cleanup-batch-37.spec.ts`<br>`web/frontend/tests/unit/config/trading-decision-mainline-gate.spec.ts`<br>`web/frontend/tests/unit/config/trading-mainline-gate.spec.ts`<br>`web/frontend/tests/unit/config/trading-style-normalization.spec.ts` |
| `trading-decision/` | 49 | `docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-25-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-26-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-46-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/pages/trading-decision-active-panel-canonical-wrapper-truth-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/pages/trading-decision-header-static-shell-truth-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/pages/trading-decision-orders-static-shell-truth-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/secondary-line-progress-summary.md`<br>`docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.json`<br>`docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.md`<br>`web/frontend/tests/unit/config/console-log-cleanup-batch-36.spec.ts`<br>`web/frontend/tests/unit/config/console-log-cleanup-batch-37.spec.ts`<br>`web/frontend/tests/unit/config/trading-decision-mainline-gate.spec.ts` |
| `trade-management/` | 26 | `docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-49-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/pages/trade-management-orphan-components-static-shell-truth-audit.md`<br>`docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.json`<br>`docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.md`<br>`web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts`<br>`web/frontend/tests/unit/config/trade-management-components-normalization.spec.ts`<br>`web/frontend/tests/unit/config/trade-management-mainline-gate.spec.ts` |
| `technical/` | 14 | `docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-18-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/pages/technical-analysis-module-legacy-static-shell-truth-audit.md`<br>`docs/reports/quality/myweb-audit/audit-20260426-02/secondary-line-progress-summary.md`<br>`docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.json`<br>`docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.md`<br>`web/frontend/tests/unit/config/console-log-cleanup-batch-23.spec.ts`<br>`web/frontend/tests/unit/config/technical-web3-style-support.spec.ts` |
| `settings/` | 18 | `docs/reports/quality/myweb-audit/audit-20260426-02/pages/settings-test-static-shells-truth-audit.md`<br>`docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.json`<br>`docs/reports/quality/myweb-audit/frontend-view-governance-inventory-2026-05-10.md`<br>`web/frontend/tests/unit/config/settings-mainline-gate.spec.ts`<br>`web/frontend/tests/unit/config/settings-style-normalization.spec.ts` |

## Top References

| Reference | Count |
|---|---:|
| `trade/__tests__/Portfolio.spec` | 64 |
| `artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec` | 63 |
| `artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec` | 63 |
| `artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec` | 57 |
| `artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec` | 56 |
| `risk/__tests__/News.spec` | 53 |
| `trade/Portfolio` | 52 |
| `trade/__tests__/Signals.spec` | 51 |
| `trade/__tests__/History.spec` | 50 |
| `/detail/news/:symbol` | 49 |
| `data/Advanced` | 48 |
| `artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec` | 48 |
| `system/__tests__/Settings.spec` | 48 |
| `risk/__tests__/Overview.spec` | 47 |
| `system/__tests__/API.spec` | 45 |
| `risk/__tests__/StopLoss.spec` | 44 |
| `watchlist/__tests__/Signals.spec` | 44 |
| `artdeco-pages/ArtDecoDashboard` | 43 |
| `composables/__tests__/useTradingDashboard.spec` | 43 |
| `artdeco-pages/composables/useArtDecoDashboard` | 42 |
| `risk/__tests__/Alerts.spec` | 42 |
| `system/__tests__/Health.spec` | 41 |
| `system/__tests__/DataSource.spec` | 40 |
| `/detail/graphics/600519` | 39 |
| `artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec` | 39 |
| `risk/Center` | 38 |
| `data/FundFlow` | 37 |
| `artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis` | 37 |
| `artdeco-pages/strategy-tabs/backtestAnalysisViewModel` | 37 |
| `trade/Center` | 36 |
| `trade/History` | 36 |
| `data/Industry` | 35 |
| `artdeco-pages/strategy-tabs/StrategySignalsTab` | 34 |
| `trade/Signals` | 34 |
| `/detail/graphics/:symbol` | 34 |
| `/detail/news/600519` | 33 |
| `artdeco-pages/stock-management-tabs/WatchlistManager` | 33 |
| `market/LHB` | 32 |
| `risk/__tests__/Center.spec` | 32 |
| `trade/__tests__/Reconciliation.spec` | 32 |
| `data/Concepts` | 31 |
| `market/Realtime` | 31 |
| `risk/Overview` | 30 |
| `announcement/__tests__/AnnouncementMonitor.spec` | 30 |
| `TradingDashboard` | 29 |
| `risk/StopLoss` | 29 |
| `strategy/Backtest` | 29 |
| `artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization` | 29 |
| `composables/useTradingDashboard` | 29 |
| `watchlist/__tests__/Manage.spec` | 27 |

## Notes

- This map is discovery evidence only. A match blocks archive until reviewed, migrated, or explicitly retired.
- Search patterns include `@/views/*`, `src/views/*`, `--target-dir`, `--target-file`, and `/detail/*` string links.
- In the JSON `records` array, `sourceFile` names the file where the reference was found, alongside `sourceType`, `kind`, `reference`, and `raw`.
- Use the JSON artifact for full per-reference rows.
