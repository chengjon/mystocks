# ArtDeco Technical Analysis Static Shell Truth Audit

## Scope
- File: `web/frontend/src/views/artdeco-pages/ArtDecoTechnicalAnalysis.vue`
- Synthetic route key: `/secondary/artdeco-technical-analysis-static-shell`
- Family: `local-action-and-execution-truth`

## Problem
- The page had no active route or importing owner.
- It still rendered local GPU/load badges, dashboardService-driven indicator calls, random trend data, delayed mock backtest stats, and synthetic equity series.
- Keeping this page live-looking would create parallel technical-analysis and backtest truth next to canonical `/market/technical`, `/data/indicator`, and `/strategy/backtest`.

## Repair
- Converted the page to an honest static shell.
- Preserved the file for compatibility and linked users to canonical technical, indicator, and backtest routes.
- Did not add a new API, store, snapshot, request badge, freshness strip, or shell-owned execution state.

## Verification
- RED:
  - `cd web/frontend && npx vitest run tests/unit/config/artdeco-technical-analysis-static-shell.spec.ts` failed because the old page lacked `legacy-static-shell`.
- GREEN:
  - `cd web/frontend && npx vitest run tests/unit/config/artdeco-technical-analysis-static-shell.spec.ts` passed (`1/1`).
- Source scan:
  - `rg "GPU 核心活跃|计算负载 12%|Math\\.random|setTimeout|handleRunBacktest|dashboardService|000001\\.SH|回测验证" web/frontend/src/views/artdeco-pages/ArtDecoTechnicalAnalysis.vue` produced no matches.

## Outcome
- The retired ArtDeco technical analysis page no longer claims local GPU state, random trend/equity, or mock backtest execution truth.
