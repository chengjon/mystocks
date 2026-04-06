# Frontend Structure Guide

## Purpose

This guide records the current frontend directory truth for the active MyStocks web shell after the `restructure-frontend-directory` execution batches. It is a repo-truth guide, not the original March proposal snapshot.

## Truth Sources

- Router truth: `web/frontend/src/router/index.ts`
- Home-route truth: `web/frontend/src/router/homeRoute.ts`
- Active route tests: `web/frontend/tests/unit/config/*-route-canonical-paths.spec.ts`
- Route uniqueness guard: `web/frontend/tests/unit/config/router-full-path-uniqueness.spec.ts`
- Execution ledger truth: Mongo-backed work items exported through `scripts/runtime/coordctl.py`
- OpenSpec execution ledger: `openspec/changes/restructure-frontend-directory/tasks.md`

## Active Page Entry Rules

For active routed business pages, the canonical implementation target is usually:

```text
web/frontend/src/views/<domain>/*.vue
```

Current routed business domains are:

- `market`
- `data`
- `watchlist`
- `strategy`
- `trade`
- `risk`
- `system`

Representative canonical entrypoints:

- `web/frontend/src/views/market/Realtime.vue`
- `web/frontend/src/views/data/Industry.vue`
- `web/frontend/src/views/watchlist/Manage.vue`
- `web/frontend/src/views/strategy/List.vue`
- `web/frontend/src/views/trade/Center.vue`
- `web/frontend/src/views/risk/Center.vue`
- `web/frontend/src/views/system/Settings.vue`

## Important Exceptions

The current repo truth still keeps a small number of canonical pages outside the `<domain>` directories. These are intentional and must not be treated as migration mistakes:

- `/dashboard` remains canonically backed by `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- `/dealing-room` is a legacy compatibility redirect only
- `/trade/terminal` remains backed by `web/frontend/src/views/TradingDashboard.vue`
- Some legacy ArtDeco pages remain embedded or compatibility-facing wrappers even after the domain cutovers

## Compatibility Wrapper Policy

The migration batches converged on this rule:

- The canonical routed implementation lives at the active target entrypoint
- The old ArtDeco path is retained only as a thin compatibility wrapper when existing imports or embedded usage still depend on it
- Compatibility wrappers must not become parallel truth sources

Examples:

- `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue` wraps `web/frontend/src/views/system/Settings.vue`
- `web/frontend/src/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue` wraps `web/frontend/src/views/risk/Overview.vue`

## What Is Not Router Truth

The following directories still exist in the repo, but they are not the primary source of active route truth by themselves:

- `web/frontend/src/views/artdeco-pages/`
- `web/frontend/src/views/converted.archive/`
- `web/frontend/src/views/demo/`
- `web/frontend/src/views/examples/`
- `web/frontend/src/views/freqtrade-demo/`
- `web/frontend/src/views/tdxpy-demo/`
- Older support directories such as `trading/`, `technical/`, `stocks/`, and `monitoring/`

Always confirm active navigation through the router instead of assuming a directory is live because it still exists.

## Verification Truth

Current verification truth for this restructure is split across focused suites instead of one monolithic command:

- Safe smoke chain:
  - `npm run test:e2e:stable`
  - `npm run test:e2e:axe`
  - `npm run test:e2e:lighthouse`
- Playwright matrix suites:
  - `web/frontend/tests/e2e/phase1-mainline-matrix.spec.ts`
  - `web/frontend/tests/e2e/phase2-mainline-matrix.spec.ts`
  - `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts`
  - `web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts`
- Focused real-read UI smokes:
  - login and dashboard shell
  - remaining Phase 1 authenticated pages

## Current Boundary

As of `2026-04-06`, phases 0 through 5 of the restructure are materially closed through verified micro-batches and ledger reconciliation. Review, merge, deploy, archive, and final communication work remain external workflow gates and should not be backfilled into local repo truth.
