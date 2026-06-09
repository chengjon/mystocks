# ArtDeco Route Header Shell Extraction Report

Date: 2026-05-31

OpenSpec change: `extract-artdeco-route-shell-components`

## Scope

This implementation introduces the first approved shared ArtDeco route shell surface and migrates only the `/trade/positions` route header.

Changed implementation files:

- `web/frontend/src/components/artdeco/route-shell/ArtDecoRouteHeader.vue`
- `web/frontend/src/components/artdeco/route-shell/index.ts`
- `web/frontend/src/components/artdeco/route-shell/__tests__/ArtDecoRouteHeader.spec.ts`
- `web/frontend/src/views/trade/Center.vue`

Documentation / governance files:

- `openspec/changes/extract-artdeco-route-shell-components/tasks.md`
- `docs/reports/tasks/2026-05-31-artdeco-route-header-extraction-report.md`

## Component Contract

`ArtDecoRouteHeader` owns only the route header shell structure:

- default shell classes: `artdeco-route-header`, `hero-shell`, `artdeco-card-shell`
- route test hook passthrough: `testId` -> `data-testid`, `legacyTest` -> `data-test`
- decorative route copy: `eyebrow`
- route metadata slot: `#meta`
- route action slot: `#actions`
- status presentation delegated to existing `ArtDecoHeader`

It does not own:

- route metadata registration
- router configuration
- backend or API client contracts
- route-level fetch orchestration
- stale snapshot rules
- domain row semantics
- page-specific fallback copy

## Migrated Route Slice

Route: `/trade/positions`

File: `web/frontend/src/views/trade/Center.vue`

The previous inline header shell was replaced with `ArtDecoRouteHeader`. The migration preserved:

- `data-test="trade-positions-header"`
- `data-testid="trade-positions-header"`
- refresh action hook: `data-testid="trade-positions-refresh"`
- title: `持仓工作台`
- subtitle: `统一查看持仓结构、盈亏表现和仓位分布，形成交易域的头寸入口`
- eyebrow: `持仓审阅`
- request id, process time, and row count metadata
- existing refresh click behavior through `loadPositions`

## TDD Evidence

RED:

- Command: `npx vitest run src/components/artdeco/route-shell/__tests__/ArtDecoRouteHeader.spec.ts`
- Result: failed because `../ArtDecoRouteHeader.vue` did not exist.

GREEN:

- Command: `npx vitest run src/components/artdeco/route-shell/__tests__/ArtDecoRouteHeader.spec.ts`
- Result: 1 test passed.

## Verification Evidence

Completed:

- `npx vitest run src/components/artdeco/route-shell/__tests__/ArtDecoRouteHeader.spec.ts`: 1 passed.
- `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g Trade-Positions --project=chromium`: 5 passed.
- `npx eslint src/components/artdeco/route-shell/ArtDecoRouteHeader.vue src/components/artdeco/route-shell/__tests__/ArtDecoRouteHeader.spec.ts src/components/artdeco/route-shell/index.ts src/views/trade/Center.vue --quiet`: passed.
- `node scripts/check-artdeco-tokens.js --target-file src/components/artdeco/route-shell/ArtDecoRouteHeader.vue --target-file src/views/trade/Center.vue`: passed.
- `npx impeccable --json src/views/trade/Center.vue`: `[]`.
- `npx impeccable --json src/components/artdeco/route-shell/ArtDecoRouteHeader.vue`: `[]`.
- `npm run type-check -- --pretty false`: passed.
- `openspec validate extract-artdeco-route-shell-components --strict`: passed.
- `pm2 list`: `mystocks-backend` online at `http://localhost:8020`; `mystocks-frontend` online at `http://localhost:3020`.
- `git diff --cached --check`: passed.
- `npx gitnexus analyze`: repository indexed successfully; 234,189 nodes, 321,490 edges, 300 flows.
- `gitnexus.detect_changes(scope=staged)`: low risk, 6 changed files, 0 affected processes.

Note: GitNexus MCP metadata continued to report `stale=true` after the successful CLI index refresh. The staged scope result still returned low risk and no affected processes.

## Stop Rule

This change intentionally stops after the first verified route slice. Broader rollout to `/trade/portfolio`, `/risk/alerts`, or other route headers requires separate approval after this implementation is reviewed.
