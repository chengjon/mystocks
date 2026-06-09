# ArtDeco Trade Reconciliation Route Header Shell Report

Date: 2026-05-31

Function Tree node: `artdeco-web-design-governance/route-header-shell-trade-reconciliation`

## Scope

Migrated `/trade/reconciliation` from a local `ArtDecoHeader` header block to the shared `ArtDecoRouteHeader` route header shell.

Touched implementation surface:

- `web/frontend/src/views/trade/Reconciliation.vue`
- `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts`

Governance/report surface:

- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/cards/route-header-shell-trade-reconciliation.yaml`
- `docs/reports/tasks/2026-05-31-artdeco-trade-reconciliation-route-header-shell-report.md`

## Compatibility Boundary

Preserved:

- `/trade/reconciliation` route path and router ownership
- `trade-reconciliation-header`, `trade-reconciliation-refresh`, `reconciliation-export-button`, control row, status strip, and work-area test hooks
- hero metadata order: `ACCOUNT`, `REQ_ID`, `UPDATED`, `IMPORT_BATCH`, `ROWS`
- page status text and status type mapping
- account selection, CSV import, statement rows, result rows, request-id semantics, stale clearing behavior, and execution context navigation

Not changed:

- `web/frontend/src/router/index.ts`
- backend API routes, schemas, or OpenAPI contracts
- frontend API clients or request URLs
- `useTradeReconciliation` composable behavior
- reconciliation status strip semantics
- broker acknowledgement, statement/result diff semantics, or readonly result interpretation
- shared trade business components

## GitNexus Evidence

Pre-edit impact analysis:

- target: `web/frontend/src/views/trade/Reconciliation.vue`
- direction: upstream
- risk: LOW
- direct affected symbols: 0
- affected processes: 0

## TDD Evidence

RED command:

```bash
npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Reconciliation clears stale statement" --project=chromium
```

Expected failure:

- `trade-reconciliation-header` existed
- expected `/artdeco-route-header/`
- received `hero-shell artdeco-card-shell`

GREEN command:

```bash
npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Reconciliation clears stale statement" --project=chromium
```

Result:

- Chromium
- 1 test passed

## Static And Governance Gates

Passed:

- `npx eslint src/views/trade/Reconciliation.vue tests/e2e/phase3-mainline-matrix.spec.ts --quiet`
- `node scripts/check-artdeco-tokens.js --target-file src/views/trade/Reconciliation.vue`
- `npx impeccable --json src/views/trade/Reconciliation.vue` returned `[]`
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
4. append `/trade/reconciliation` to the route header shell migration ledger
5. commit the closeout/ledger update separately
