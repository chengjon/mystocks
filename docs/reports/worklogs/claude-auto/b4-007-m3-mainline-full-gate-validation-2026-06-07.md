# B4.007-M3 Mainline Full Gate Validation

Date: 2026-06-07
Recorded at: 2026-06-07 20:24:03 CST
Branch: `wip/root-dirty-20260403`
Validation HEAD: `b39fc7b85`
FUNCTION_TREE node: `artdeco-web-design-governance/b4-frontend-mainline-route-truth`
Mode: validation-only; no source edits

## Scope

M3 validates the B4.007 mainline route continuity package after M2 landed.

Validated surfaces:

- Router truth: `web/frontend/src/router/index.ts`
- Navigation truth: `web/frontend/src/config/menu.config.js`
- Page configuration truth: `web/frontend/src/config/pageConfig.ts`
- Mainline view components under dashboard, data, market, watchlist, strategy, trade, risk, system, and ai route families
- Store/API/composable dependencies imported by active route components
- PM2-served runtime at `http://localhost:3020` with backend at `http://localhost:8020`

Explicit non-goals preserved:

- No source edits in M3.
- No edits to the 11 frozen F3 archive Backlog files.
- No edits to ST-HOLD.
- No edits to `marketKlineData`.
- No archive-only deletion or retirement work.
- No backend/API contract changes.

## Mainline Matrix Closure

AST-based validation was run against router, menu config, pageConfig, and active component imports.

| Check | Result |
|---|---:|
| Router paths | 56 |
| Mainline route rows | 55 |
| Mainline component routes | 39 |
| Menu paths | 25 |
| Active pageConfig paths | 35 |
| pageConfig API endpoints | 33 |
| Menu paths missing from router | 0 |
| pageConfig paths missing from router | 0 |
| Router component files missing | 0 |

Domain matrix:

| Domain | Router paths | Menu paths | pageConfig paths | pageConfig APIs | Component routes | Store imports | API imports | Composable imports |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| dashboard | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 1 |
| data | 5 | 1 | 4 | 4 | 4 | 0 | 3 | 4 |
| market | 4 | 3 | 3 | 3 | 3 | 0 | 3 | 3 |
| watchlist | 4 | 3 | 3 | 3 | 3 | 0 | 0 | 0 |
| strategy | 8 | 4 | 7 | 7 | 7 | 1 | 1 | 2 |
| trade | 8 | 1 | 6 | 5 | 7 | 1 | 5 | 5 |
| risk | 7 | 6 | 5 | 5 | 6 | 0 | 3 | 4 |
| system | 6 | 3 | 5 | 5 | 5 | 1 | 4 | 5 |
| ai | 4 | 3 | 1 | 1 | 3 | 0 | 0 | 3 |

Matrix conclusion:

- Router -> menu closure: passed.
- Router -> pageConfig closure: passed.
- Router -> page component file closure: passed.
- Active route components retain expected store/API/composable dependencies where applicable.
- No new mainline route discontinuity was found.

## Verification

Commands run:

- `npm run type-check`
  - Result: passed.
  - Exit: `0`.
  - Summary: `vue-tsc --noEmit`.

- `npm run test:unit:stable`
  - Result: passed.
  - Exit: `0`.
  - Summary: 33 test files passed, 415 tests passed.
  - Note: expected negative-path log lines were emitted by mocked auth/market adapter tests; Vitest exit remained `0`.

- `PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://localhost:3020 npm run test:e2e:business-smoke`
  - Result: passed.
  - Exit: `0`.
  - Browser/project: chromium.
  - Summary: 55 tests passed in 2.1m.

PM2:

- `mystocks-backend`: online at `http://localhost:8020`.
- `mystocks-frontend`: online at `http://localhost:3020`.

GitNexus:

- `detect_changes(scope=staged)`: no staged changes.
- Indexed commit: `b39fc7b858797a155da9c96a1630842ca587d777`.
- Current commit: `b39fc7b858797a155da9c96a1630842ca587d777`.
- Stale: false.
- Risk: none for staged diff.

OPENDOG:

- `run-verification --kind build --command "npm --prefix web/frontend run type-check"`: passed, exit `0`.
- `run-verification --kind test --command "npm --prefix web/frontend run test:unit:stable"`: passed, exit `0`.
- `run-verification --kind test --command "cd web/frontend && PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://localhost:3020 npm run test:e2e:business-smoke"`: passed, exit `0`, 55 passed.
- Final `verification`: failing runs `0`, cleanup blockers `0`, refactor blockers `0`, freshness `fresh`.

## Generated Drift Disposition

The following generated-class drifts remain separate from M3 validation and must not be mixed into the M3 closeout package:

1. `.governance/programs/artdeco-web-design-governance/tree.md`
   - Drift type: governance generated planning tree expansion.
   - Diff shape: 1 hunk, 41 added planning-node lines, 0 deletions.
   - M3 disposition: not a runtime/source gate input; keep isolated for a later governance-tree sync package.

2. `web/frontend/src/components.d.ts`
   - Drift type: generated component declaration update.
   - Diff shape: 2 hunks, 1 added declaration, 1 removed declaration.
   - Notable delta: adds `ArtDecoRouteHeader`; removes `ElRadio`.
   - M3 disposition: not required for M3 gate pass; keep isolated for a later generated-types package.

## Result

B4.007-M3 mainline validation passed at `b39fc7b85`.

FUNCTION_TREE closeout was completed after this report was recorded:

- `approved-for-implementation -> implementation-ready`
- `implementation-ready -> implementation-landed`
- `implementation-landed -> closeout-prepared`
- `closeout-prepared -> closed`
- `ft-governance validate`: passed.
- Active gates after closeout: `0`.

B4.007 mainline route governance is closed. F3 Backlog remains frozen until the approved family-batch archive workflow starts.
