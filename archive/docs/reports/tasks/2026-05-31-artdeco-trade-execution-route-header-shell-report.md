# ArtDeco Trade Execution Route Header Shell Report

Date: 2026-05-31

Function Tree node: `artdeco-web-design-governance/route-header-shell-trade-execution`

## Scope

Migrated `/trade/execution` from a local `ArtDecoHeader` header block to the shared `ArtDecoRouteHeader` route header shell.

Touched implementation surface:

- `web/frontend/src/views/trade/Execution.vue`
- `web/frontend/tests/e2e/trade-execution-tracking.spec.ts`

Governance/report surface:

- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/cards/route-header-shell-trade-execution.yaml`
- `docs/reports/tasks/2026-05-31-artdeco-trade-execution-route-header-shell-report.md`

## Compatibility Boundary

Preserved:

- `/trade/execution` route path and router ownership
- `trade-execution-header`, `trade-execution-refresh`, stats/filter/trigger/work-area test hooks
- refresh behavior through `loadTracking`
- page status text and warning/info status mapping
- external trigger observation copy
- trade execution, bridge evidence, broker acknowledgement, and reconciliation semantics

Not changed:

- `web/frontend/src/router/index.ts`
- backend API routes, schemas, or OpenAPI contracts
- frontend API clients or request URLs
- stores, polling, retry, stale snapshot, filters, table columns, trigger workflow, detail drawer, or reconciliation navigation
- shared trade business components

## GitNexus Evidence

Pre-edit impact analysis:

- target: `web/frontend/src/views/trade/Execution.vue`
- direction: upstream
- risk: LOW
- direct affected symbols: 1
- affected processes: 0

## TDD Evidence

RED command:

```bash
npx playwright test tests/e2e/trade-execution-tracking.spec.ts -g "exposes route-level ArtDeco hooks for execution tracking" --project=chromium
```

Expected failure:

- `trade-execution-header` existed
- expected `/artdeco-route-header/`
- received `execution-hero artdeco-card-shell`

GREEN command:

```bash
npx playwright test tests/e2e/trade-execution-tracking.spec.ts -g "exposes route-level ArtDeco hooks for execution tracking" --project=chromium
```

Result:

- Chromium
- 1 test passed

## Additional E2E Evidence

Command:

```bash
npx playwright test tests/e2e/trade-execution-tracking.spec.ts --project=chromium
```

Result:

- Chromium
- 1 passed
- 1 failed

Failure observed:

- test: `observes external triggers without promoting bridge evidence to broker truth`
- failure point: `getByRole("complementary", { name: "执行证据详情" })`
- failure reason: detail drawer did not appear after clicking `execution-detail-track-101`
- scope assessment: outside this route header shell migration; the failing surface is the detail fetch/drawer path, which this node explicitly did not modify

The focused route header shell gate passed. The broader detail drawer failure is recorded as existing/non-scope follow-up evidence and was not repaired in this node.

## Static And Governance Gates

Passed:

- `npx eslint src/views/trade/Execution.vue tests/e2e/trade-execution-tracking.spec.ts --quiet`
- `node scripts/check-artdeco-tokens.js --target-file src/views/trade/Execution.vue`
- `npx impeccable --json src/views/trade/Execution.vue` returned `[]`
- `npm run type-check -- --pretty false`
- `openspec validate --all --strict`: 63 passed, 0 failed
- `ft-governance validate --steward`
- `ft-governance gate --verbose`

OpenSpec note:

- spec validation passed
- PostHog telemetry flush printed a network error after validation; this did not change the 63 passed / 0 failed validation result

PM2:

- `mystocks-backend`: online, expected URL `http://localhost:8020`
- `mystocks-frontend`: online, expected URL `http://localhost:3020`

## Dirty Worktree Note

The repository contains unrelated dirty files. This node must stage only the implementation, E2E assertion, governance node/card/active-gate files, and this report.

Known unrelated file to keep unstaged:

- `.governance/programs/artdeco-web-design-governance/tree.md`

## Next Closeout Step

After the implementation commit lands:

1. transition the Function Tree node to `implementation-landed`
2. run `closeout`
3. transition to `closed`
4. append `/trade/execution` to the route header shell migration ledger
5. commit the closeout/ledger update separately
