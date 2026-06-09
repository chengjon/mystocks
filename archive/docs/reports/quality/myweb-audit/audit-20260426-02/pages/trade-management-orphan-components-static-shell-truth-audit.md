# Trade Management Orphan Components Static Shell Truth Audit

## Scope
- Files:
  - `web/frontend/src/views/trade-management/components/PortfolioOverview.vue`
  - `web/frontend/src/views/trade-management/components/PositionsTab.vue`
  - `web/frontend/src/views/trade-management/components/StatisticsTab.vue`
  - `web/frontend/src/views/trade-management/components/TradeHistoryTab.vue`
  - `web/frontend/src/views/trade-management/components/TradeDialog.vue`
- Synthetic route key: `/secondary/trade-management-orphan-components`
- Family: `local-action-and-execution-truth / static-shell degradation`

## Problem
- These components were no longer imported by the active `ArtDecoTradingManagement.vue` orchestration shell.
- They still preserved independent live trading semantics: sample portfolio values, direct `tradeApi` fetches, fallback position rows, local chart synthesis, history pagination, and order submission.

## Repair
- Converted the five orphan components to honest static shells.
- Preserved the files and barrel exports for compatibility, but removed independent live state and execution behavior.
- Added source-level regression coverage that rejects `tradeApi`, fallback rows, chart synthesis, order submission, and fake history totals.

## Verification
- RED:
  - `cd web/frontend && npx vitest run tests/unit/config/trade-management-components-normalization.spec.ts` failed because the old components lacked `legacy-static-shell`.
- GREEN:
  - `cd web/frontend && npx vitest run tests/unit/config/trade-management-components-normalization.spec.ts` passed (`1/1`).
- Source scan:
  - `rg "tradeApi\\.|from '@/api/trade'|PING AN BANK|NO POSITION|ORDER SUBMITTED|TRADE FAILED|FAILED TO LOAD TRADE HISTORY|echarts\\.init|console\\.error" <batch files>` produced no matches.

## Outcome
- The retired trade-management component tree no longer claims independent trading truth.
- Users are handed off to canonical `/trade/portfolio`, `/trade/positions`, `/trade/history`, and `/trade/terminal`.
