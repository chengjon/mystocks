# Stocks Portfolio Static Shell Truth Audit

## Scope
- File: `web/frontend/src/views/stocks/Portfolio.vue`
- Synthetic route key: `/secondary/stocks-portfolio-static-shell`
- Family: `local-action-and-execution-truth`

## Problem
- The page was not active route truth and had no importing owner.
- It still rendered local mock portfolio metrics, hardcoded position rows, random refresh mutation, add-position toast semantics, and a performance chart placeholder.
- Keeping this page live-looking would create a parallel portfolio truth next to canonical `/trade/portfolio`.

## Repair
- Converted the page to an honest static shell.
- Preserved the file for compatibility and linked users to canonical `/trade/portfolio`.
- Did not add a new portfolio API, store, snapshot, request badge, freshness strip, or shell-owned execution state.

## Verification
- RED:
  - `cd web/frontend && npx vitest run tests/unit/config/stocks-portfolio-static-shell.spec.ts` failed because the old page lacked `legacy-static-shell`.
- GREEN:
  - `cd web/frontend && npx vitest run tests/unit/config/stocks-portfolio-static-shell.spec.ts` passed (`1/1`).
- Source scan:
  - `rg "ElMessage|Math\\.random|000001|平安银行|portfolioMetrics|positions = ref|ADD POSITION|Portfolio refreshed|performancePeriod|PORTFOLIO MANAGEMENT" web/frontend/src/views/stocks/Portfolio.vue` produced no matches.

## Outcome
- The retired portfolio child page no longer claims local portfolio metrics, position rows, random refresh, add-position, or chart execution truth.
