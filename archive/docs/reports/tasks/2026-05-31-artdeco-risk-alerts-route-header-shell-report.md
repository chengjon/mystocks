# ArtDeco Risk Alerts Route Header Shell Migration Report

> **Authority note**: This report records the implementation evidence for one Function Tree node. Repository-wide governance remains defined by `architecture/STANDARDS.md`, `openspec/AGENTS.md`, and the active Function Tree governance files.

## Summary

- Date: 2026-05-31
- Function Tree program: `artdeco-web-design-governance`
- Function Tree node: `route-header-shell-risk-alerts`
- Function Tree reference: `docs/FUNCTION_TREE.md#domain-06-node-03`
- Related risk-domain reference: `docs/FUNCTION_TREE.md#domain-04-node-03`
- Route surface: `/risk/alerts`
- Canonical page file: `web/frontend/src/views/risk/Alerts.vue`
- Reusable shell: `web/frontend/src/components/artdeco/route-shell/ArtDecoRouteHeader.vue`

This node migrates the `/risk/alerts` page header band from a local `section.hero-shell` plus inline `ArtDecoHeader` composition to the shared `ArtDecoRouteHeader` shell proven by the earlier `/trade/positions` and `/trade/portfolio` slices.

## Scope Boundary

Implemented:

- Replaced the page-level risk alerts header shell with `ArtDecoRouteHeader`.
- Preserved the existing title, subtitle, eyebrow, status text, status type, request-id metadata, unread metadata, focus metadata, refresh button hook, refresh loading state, and `risk-alerts-header` / `risk-alerts-refresh` test hooks.
- Added an E2E assertion that `risk-alerts-header` uses the shared `artdeco-route-header` class.

Explicit non-goals respected:

- No router configuration or route path changes.
- No backend API contract changes.
- No frontend API client changes.
- No shared component extraction beyond using the already-landed `ArtDecoRouteHeader`.
- No changes to alert fetch orchestration, runtime status strips, table panels, filter state, alert records, alert rules, unread semantics, or risk severity semantics.

## TDD Evidence

RED:

- Command: `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts -g "Risk-Alerts renders mocked alerts and rules tables" --project=chromium`
- Result: failed as expected.
- Failure: `risk-alerts-header` had class `hero-shell artdeco-card-shell` and did not match `/artdeco-route-header/`.

GREEN:

- Command: `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts -g "Risk-Alerts renders mocked alerts and rules tables" --project=chromium`
- Result: 1 passed.

Focused route regression:

- Command: `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts -g "Risk-Alerts" --project=chromium`
- Result: 4 passed.

Unit regression:

- Command: `npm run test -- src/views/risk/__tests__/Alerts.spec.ts`
- Result: 1 file passed, 8 tests passed.

## Verification Evidence

- `npx eslint src/views/risk/Alerts.vue tests/e2e/phase4-mainline-matrix.spec.ts --quiet`: passed.
- `node scripts/check-artdeco-tokens.js --target-file src/views/risk/Alerts.vue`: passed.
- `npx impeccable --json src/views/risk/Alerts.vue`: passed with `[]`.
- `npm run type-check -- --pretty false`: passed with exit code 0.
- `openspec validate --all --strict`: 63 passed, 0 failed.
- `node /root/.codex/skills/myskills/skills/function-tree/scripts/ft-governance.cjs validate --steward`: passed.
- PM2 status: `mystocks-backend` and `mystocks-frontend` online.

## GitNexus Evidence

Pre-edit impact check:

- `impact(target="Alerts.vue", file_path="web/frontend/src/views/risk/Alerts.vue")`: GitNexus could not resolve the Vue SFC target and returned `UNKNOWN`.
- Follow-up `context(name="Alerts", file_path="web/frontend/src/views/risk/Alerts.vue")`: symbol not found.
- Follow-up `query("risk alerts Vue route page Alerts.vue")`: returned related risk and E2E symbols but no front-end SFC process.
- Follow-up `route_map("/risk/alerts")`: only matched `/api/risk/alerts`, not the front-end route.

Interpretation:

- GitNexus does not currently expose this Vue SFC as an indexed symbol, so the page-level impact result is unknown rather than high-risk.
- The implementation is therefore constrained through Function Tree scope, focused E2E, route hook preservation, and staged `detect_changes` before commit.

## Dirty Worktree Note

`web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts` already had unrelated worktree changes before this node's E2E assertion was added. This node owns only the `risk-alerts-header` class assertion in that file. The implementation commit must stage that single assertion hunk only and must not include pre-existing unrelated changes from the file.

## Outcome

`/risk/alerts` is now the third migrated route in the ArtDeco route-header-shell rollout, following:

- `/trade/positions`
- `/trade/portfolio`
- `/risk/alerts`

The route now uses the shared route header grammar while preserving existing risk-alert data flow and visual/runtime test hooks.
