# ArtDeco Market Realtime Route Header Shell Migration Report

> **Authority note**: This report records implementation evidence for one Function Tree node. Repository-wide governance remains defined by `architecture/STANDARDS.md`, OpenSpec governance remains defined by `openspec/AGENTS.md`, and route-header-shell execution rules remain documented in `docs/guides/web/ARTDECO_ROUTE_HEADER_SHELL_MODIFICATION_RULES.md`.

## Summary

- Date: 2026-05-31
- Function Tree program: `artdeco-web-design-governance`
- Function Tree node: `route-header-shell-market-realtime`
- Function Tree reference: `docs/FUNCTION_TREE.md#domain-01-node-03`
- Route surface: `/market/realtime`
- Canonical page file: `web/frontend/src/views/market/Realtime.vue`
- Reusable shell: `web/frontend/src/components/artdeco/route-shell/ArtDecoRouteHeader.vue`
- E2E file: `web/frontend/tests/e2e/market-data.spec.ts`

This node migrates the `/market/realtime` page header band from a local `section.route-header-shell` plus inline `ArtDecoHeader` composition to `ArtDecoRouteHeader`.

## Scope Boundary

Implemented:

- Replaced the local realtime route header shell with `ArtDecoRouteHeader`.
- Preserved the existing title, subtitle, status text, refresh button hook, refresh loading state, refresh disabled state, `market-realtime-header`, `market-realtime-refresh`, and `market-realtime-status-strip` hooks.
- Extended `ArtDecoRouteHeader` with a default slot so route-local runtime strips can remain inside the same route header shell.
- Preserved the market realtime `.hero-meta` contract used by unit tests:
  - `SAMPLE: ...`
  - `TRACE_ID: ...`
  - `PRESET: ...`
- Preserved the `.content-shell-meta` contract used by unit tests:
  - `MOOD: ...`
  - `UP: ...`
  - `DOWN: ...`
- Updated the route header shell rules guide to document the default-slot pattern for pages that already carry route-local runtime strips inside the header shell.

Explicit non-goals respected:

- No router configuration or route path changes.
- No backend API contract changes.
- No frontend API client changes.
- No market quote request, retry, cache, stale snapshot, or preset orchestration changes.
- No table, chart, stats strip, control row, workbench area, A-share color semantic, or market data semantic changes.
- No unrelated page polish.

## TDD Evidence

RED:

- Command: `npx playwright test tests/e2e/market-data.spec.ts -g "should display core realtime widgets" --project=chromium`
- Result: failed as expected.
- Failure: `market-realtime-header` had class `route-header-shell artdeco-card-shell` and did not match `/artdeco-route-header/`.

GREEN:

- Command: `npx playwright test tests/e2e/market-data.spec.ts -g "should display core realtime widgets" --project=chromium`
- Result: 1 passed.

Focused route regression:

- Command: `npx playwright test tests/e2e/market-data.spec.ts -g "Market Realtime Page" --project=chromium`
- Result: 3 passed.

Unit regression:

- Command: `npm run test -- src/views/market/__tests__/Realtime.spec.ts`
- Initial result after header migration: 5 failures because the unit contract expected `.hero-meta`.
- Fix: restored `.hero-meta` via the `ArtDecoRouteHeader` `#meta` slot and restored `.content-shell-meta` inside the route header shell.
- Final result: 1 file passed, 6 tests passed.

## Verification Evidence

- `npx eslint src/views/market/Realtime.vue src/components/artdeco/route-shell/ArtDecoRouteHeader.vue tests/e2e/market-data.spec.ts --quiet`: passed.
- `node scripts/check-artdeco-tokens.js --target-file src/views/market/Realtime.vue`: passed.
- `node scripts/check-artdeco-tokens.js --target-file src/components/artdeco/route-shell/ArtDecoRouteHeader.vue`: passed.
- `npx impeccable --json src/views/market/Realtime.vue`: passed with `[]`.
- `npx impeccable --json src/components/artdeco/route-shell/ArtDecoRouteHeader.vue`: passed with `[]`.
- `npm run type-check -- --pretty false`: passed with exit code 0.
- `openspec validate --all --strict`: 63 passed, 0 failed.
- `node /root/.codex/skills/myskills/skills/function-tree/scripts/ft-governance.cjs validate --steward`: passed.
- PM2 status: `mystocks-backend` and `mystocks-frontend` online.

## GitNexus Evidence

Pre-edit impact checks:

- `impact(target="Realtime.vue", file_path="web/frontend/src/views/market/Realtime.vue")`: risk `LOW`, direct impact `2`, affected processes `0`.
- `impact(target="ArtDecoRouteHeader.vue", file_path="web/frontend/src/components/artdeco/route-shell/ArtDecoRouteHeader.vue")`: risk `LOW`, direct impact `3`, affected processes `0`.

Staged `detect_changes` must run before commit and should be recorded in the final closeout.

## Dirty Worktree Note

The repository still contains unrelated dirty files outside this node. This node owns only:

- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/cards/route-header-shell-market-realtime.yaml`
- `web/frontend/src/components/artdeco/route-shell/ArtDecoRouteHeader.vue`
- `web/frontend/src/views/market/Realtime.vue`
- `web/frontend/tests/e2e/market-data.spec.ts`
- `docs/guides/web/ARTDECO_ROUTE_HEADER_SHELL_MODIFICATION_RULES.md`
- `docs/reports/tasks/2026-05-31-artdeco-market-realtime-route-header-shell-report.md`

## Outcome

`/market/realtime` now uses the shared route header shell while preserving its route-local runtime status strip, snapshot freshness metadata, sample/preset metadata, and market data behavior.

The route-header-shell rollout now covers:

- `/trade/positions`
- `/trade/portfolio`
- `/risk/alerts`
- `/market/realtime`
