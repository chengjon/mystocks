# ArtDeco Trade Signals Route Header Shell Report

Date: 2026-05-31

Function Tree node: `artdeco-web-design-governance/route-header-shell-trade-signals`

Implementation commit: `81e9db3be feat(web): migrate trade signals route header shell`

## Scope

Migrated `/trade/signals` from a local `ArtDecoHeader` header block to the shared `ArtDecoRouteHeader` route header shell.

Touched implementation surface:

- `web/frontend/src/views/trade/Signals.vue`
- `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts`

Governance/report surface:

- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/cards/route-header-shell-trade-signals.yaml`
- `docs/guides/web/ARTDECO_ROUTE_HEADER_SHELL_MODIFICATION_RULES.md`
- `docs/reports/tasks/2026-05-31-artdeco-trade-signals-route-header-shell-report.md`

## Compatibility Boundary

Preserved:

- `/trade/signals` route path and router ownership
- `trade-signals-page`, `trade-signals-header`, `trade-signals-refresh`, `trade-signals-review-lens`, `trade-signals-trust-strip`, `trade-signals-runtime-message`, and `trade-signals-list` test hooks
- hero metadata order: `COUNT`, `DATA`, `REQ_ID`, `TIME`
- refresh behavior through `loadSignals`
- page status text and warning/info status mapping
- signal list, confidence/review lens, trust strip, execution history, pending provenance, first-load failure, stale refresh failure, mock-data, and sample copy semantics

Not changed:

- `web/frontend/src/router/index.ts`
- backend API routes, schemas, OpenAPI contracts, or Pydantic models
- frontend API clients, request URLs, stores, or transport wrappers
- `/api/v1/trade/signals` contract
- signal filter behavior, batch execution handler, CSV export handler, signal row mapping, or runtime state ownership
- shared signal business components

## GitNexus Evidence

Pre-edit impact analysis:

- target: `web/frontend/src/views/trade/Signals.vue`
- direction: upstream
- risk: LOW
- direct affected symbols: 2
- affected processes: 0

Staged scope gate:

- changed files: 6
- risk level: low
- changed symbols: 0
- affected processes: 0

GitNexus index note:

- Local `gitnexus analyze` was run, not `npx gitnexus analyze`.
- Analyze result: repository indexed successfully in 353.4s, `234,263 nodes`, `321,578 edges`, `2738 clusters`, `300 flows`.
- MCP metadata still reported stale `indexed_commit` after analyze; this is treated as the known MCP metadata residual for this line, not as a reason to loop analysis.

## TDD Evidence

RED command:

```bash
npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Signals renders mocked signal execution workspace" --project=chromium
```

Expected failure:

- `trade-signals-header` existed
- expected `/artdeco-route-header/`
- received `hero-shell artdeco-card-shell`

GREEN command:

```bash
npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Signals renders mocked signal execution workspace" --project=chromium
```

Result:

- Chromium
- 1 test passed

Additional same-route E2E command:

```bash
npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Signals" --project=chromium
```

Result:

- Chromium
- 4 tests passed

## Static And Governance Gates

Passed:

- `npx eslint src/views/trade/Signals.vue --max-warnings=0`
- `node scripts/check-artdeco-tokens.js --target-file src/views/trade/Signals.vue`
- `npx impeccable --json src/views/trade/Signals.vue` returned `[]`
- `npm run type-check`: exit code 0, 0 total errors, 0 structural syntax errors, 0 changed-file errors
- `openspec validate --all --strict`: 63 passed, 0 failed
- `ft-governance scope-check --files ...`
- `ft-governance validate --steward`
- `ft-governance gate --verbose`
- `git diff --cached --check`

ESLint note:

- `npx eslint src/views/trade/Signals.vue tests/e2e/phase3-mainline-matrix.spec.ts` exited 0.
- The E2E file emitted the repository's configured ignore warning, so the page file was also checked independently with `--max-warnings=0`.

PM2:

- `mystocks-backend`: online, expected URL `http://localhost:8020`
- `mystocks-frontend`: online, expected URL `http://localhost:3020`

## Dirty Worktree Note

The repository contains unrelated dirty files. This node staged only the implementation, E2E assertion, governance node/card/active-gate files, and this report/ledger update.

Known unrelated file to keep unstaged:

- `.governance/programs/artdeco-web-design-governance/tree.md`

## Closeout Result

The `/trade/signals` route now uses the same shared route-level ArtDeco header shell as the completed trade and risk route migrations while preserving route ownership, API/client contracts, signal runtime state, and page-local business semantics.
