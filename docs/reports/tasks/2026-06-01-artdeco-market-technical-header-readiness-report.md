# ArtDeco Market Technical Header Readiness Report

Date: 2026-06-01

Function Tree node: `artdeco-web-design-governance/market-technical-header-readiness`

Implementation commit: `13321ab73 test(web): harden market technical header readiness`

## Scope

Prepared `/market/technical` for a future ArtDeco route header shell migration by adding stable route-level test hooks and focused E2E coverage.

Touched implementation surface:

- `web/frontend/src/views/market/Technical.vue`
- `web/frontend/tests/e2e/market-data.spec.ts`

Governance/report surface:

- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/cards/market-technical-header-readiness.yaml`
- `docs/reports/tasks/2026-06-01-artdeco-market-technical-header-readiness-report.md`

## Result

Added stable test hooks:

- `market-technical-page`
- `market-technical-header`
- `market-technical-refresh`

Added focused E2E assertions to `market-data.spec.ts` for the `/market/technical` navigation test.

This is a readiness/test-hardening node only. It does not migrate `Technical.vue` to `ArtDecoRouteHeader`.

## Compatibility Boundary

Preserved:

- `/market/technical` route path and router ownership
- `market-technical` route name and route metadata
- K-line API request construction
- `dataApi.getKline`
- `fetchKLine`
- chart rendering
- stats strip
- content shell
- K-line summary table
- error, empty, loading, and retry behavior

Not changed:

- `web/frontend/src/router/index.ts`
- backend API routes, OpenAPI/Pydantic schemas, or frontend API clients
- `marketKlineData.ts`
- `ProKLineChart`
- financial rise/fall color semantics
- shared ArtDeco components
- route header shell implementation

## GitNexus Evidence

Pre-edit file impact for `web/frontend/src/views/market/Technical.vue`:

- target UID: `File:web/frontend/src/views/market/Technical.vue`
- risk: LOW
- direct affected symbols: 1
- affected processes: 0

Staged scope gate:

- changed files: 6
- risk level: low
- affected processes: 0

GitNexus index note:

- Local `gitnexus analyze` was run, not `npx gitnexus analyze`.
- Analyze result before implementation commit: repository indexed successfully in 175.4s, `230,303 nodes`, `315,809 edges`, `2730 clusters`, `300 flows`.
- MCP metadata still reported stale `indexed_commit` after analyze; this is the same known MCP metadata residual observed in this route-header workline.

## TDD Evidence

RED command:

```bash
npx playwright test tests/e2e/market-data.spec.ts -g "should open market technical page" --project=chromium
```

Expected failure:

- `market-technical-page` was not found before adding the readiness hooks

GREEN command:

```bash
npx playwright test tests/e2e/market-data.spec.ts -g "should open market technical page" --project=chromium
```

Result:

- Chromium
- 1 test passed

## Static And Governance Gates

Passed:

- `npx eslint src/views/market/Technical.vue tests/e2e/market-data.spec.ts --no-warn-ignored`
- `node scripts/check-artdeco-tokens.js --target-file src/views/market/Technical.vue`
- `npm run type-check -- --pretty false`: exit code 0, 0 structural syntax errors, 0 type errors
- `ft-governance validate --steward`: passed
- `git diff --cached --check`: passed

## Dirty Worktree Note

The repository contains unrelated dirty files. This node staged only the readiness hooks, E2E assertions, and Function Tree governance files.

`web/frontend/src/views/market/Technical.vue` had pre-existing unstaged changes beyond this node's hook additions. Those unrelated hunks were intentionally left unstaged.

Other unrelated dirty files remain outside this node, including:

- `.governance/programs/artdeco-web-design-governance/tree.md`
- `docs/reports/quality/myweb-audit/market-technical-myweb-audit-2026-05-11-repair.md`

## Next Recommended Step

Create a separate `route-header-shell-market-technical` implementation node after this readiness node is closed.

The future migration should add a RED assertion that `market-technical-header` has `artdeco-route-header`, then migrate only the route header shell to `ArtDecoRouteHeader` while preserving K-line API, chart, stats, table, error, empty, and loading semantics.
