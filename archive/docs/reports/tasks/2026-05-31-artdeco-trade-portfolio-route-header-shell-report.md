# ArtDeco Trade Portfolio Route Header Shell Migration Report

Date: 2026-05-31

Function Tree node: `artdeco-web-design-governance/route-header-shell-trade-portfolio`

Function Tree position: `docs/FUNCTION_TREE.md#domain-05-node-01` (`05-投资组合与交易 / 5.1 持仓管理`)

## Scope

This slice migrates only the `/trade/portfolio` route header shell to the shared ArtDeco route shell component.

Changed implementation files:

- `web/frontend/src/views/trade/Portfolio.vue`
- `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts`

Governance files:

- `.governance/active-gates.md`
- `.governance/active-gates.json`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `docs/reports/tasks/2026-05-31-artdeco-trade-portfolio-route-header-shell-report.md`

## Boundary Confirmation

This slice did not change:

- router configuration or route paths
- backend API handlers
- OpenAPI contracts
- frontend API clients
- portfolio fetch orchestration
- attribution loading behavior
- stale snapshot logic
- route-local copy outside the header shell
- runtime status strips, review segments, table panels, or route business state

## TDD Evidence

RED:

- Command: `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Portfolio renders mocked portfolio overview" --project=chromium`
- Result: failed because `trade-portfolio-header` had class `hero-shell artdeco-card-shell` and did not have `artdeco-route-header`.

GREEN:

- Command: `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Portfolio renders mocked portfolio overview" --project=chromium`
- Result: 1 passed.

## Implementation

`web/frontend/src/views/trade/Portfolio.vue` now imports `ArtDecoRouteHeader` from `@/components/artdeco/route-shell/ArtDecoRouteHeader.vue`.

The previous inline header shell was replaced with:

- title: `组合资产工作台`
- subtitle: `统一查看资产规模、持仓分布、绩效归因和再平衡建议`
- eyebrow: `portfolio assets desk`
- `test-id="trade-portfolio-header"`
- `#meta` slot preserving:
  - `REQ: {{ displayRequestId }}`
  - `POSITIONS: {{ displayPositionCount }}`
  - `REBALANCE: {{ displayRebalanceStatValue }}`
- `#actions` slot preserving:
  - refresh button
  - `data-testid="trade-portfolio-refresh"`
  - `@click="fetchPortfolio"`

The E2E route check now verifies that `trade-portfolio-header` uses the shared `artdeco-route-header` shell class while keeping the existing route hooks visible.

## Verification Evidence

Completed:

- GitNexus pre-edit impact for `web/frontend/src/views/trade/Portfolio.vue`: MEDIUM risk, 5 direct dependents, 8 total impacted, 0 affected processes.
- Function Tree `scope-check`: planned files were within active authorization.
- RED E2E: expected failure before migration.
- GREEN E2E single test: 1 passed.
- Focused E2E: `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Portfolio" --project=chromium`: 5 passed.
- Unit test: `npm run test -- src/views/trade/__tests__/Portfolio.spec.ts`: 8 passed.
- ESLint: `npx eslint src/views/trade/Portfolio.vue tests/e2e/phase3-mainline-matrix.spec.ts --quiet`: passed.
- ArtDeco token check: `node scripts/check-artdeco-tokens.js --target-file src/views/trade/Portfolio.vue`: passed.
- Impeccable: `npx impeccable --json src/views/trade/Portfolio.vue`: `[]`.
- Type check: `npm run type-check -- --pretty false`: passed.
- OpenSpec: `openspec validate --all --strict`: 63 passed, 0 failed.
- Function Tree governance: `ft-governance validate --steward`: passed after refreshing evidence to current HEAD.
- PM2: `mystocks-backend` and `mystocks-frontend` online.
- `git diff --cached --check`: passed.
- GitNexus index refresh: `npx gitnexus analyze`, repository indexed successfully; 234,200 nodes, 321,503 edges, 300 flows.
- GitNexus staged scope gate: low risk, 6 changed files, 0 affected processes.

Note: GitNexus MCP metadata continued to report `stale=true` after the successful CLI index refresh. The staged scope result still returned low risk and no affected processes.

## Result

`/trade/portfolio` is now the second route using `ArtDecoRouteHeader`, after `/trade/positions`.

The route-level evidence supports continuing cautiously to one cross-domain header-shell migration candidate, likely `risk/Alerts.vue`, but runtime strips, review segments, and data panels should remain separate proposals.
