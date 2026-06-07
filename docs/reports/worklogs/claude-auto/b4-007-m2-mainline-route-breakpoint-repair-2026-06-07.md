# B4.007-M2 Mainline Route Breakpoint Repair

Date: 2026-06-07
Branch: `wip/root-dirty-20260403`
Base HEAD: `b2a559c1741aae5619ab5083ab6ad43a18ab168b`
FUNCTION_TREE node: `artdeco-web-design-governance/b4-frontend-mainline-route-truth`
Mode: source-authorized implementation

## Scope

This package repairs the mainline route/menu/runtime breakpoints found by B4.007-M1.

Allowed source/test surface used:

- `web/frontend/src/config/menu.config.js`
- `web/frontend/src/main-standard.ts`
- `web/frontend/tests/e2e/critical/menu-navigation-fixed.spec.ts`
- `web/frontend/tests/e2e/market-data.spec.ts`

Governance/report artifacts:

- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/cards/b4-frontend-mainline-route-truth.yaml`
- `docs/reports/worklogs/claude-auto/b4-007-m1-mainline-route-continuity-audit-2026-06-07.md`
- `docs/reports/worklogs/claude-auto/b4-007-m2-mainline-route-breakpoint-repair-2026-06-07.md`

Explicit non-goals preserved:

- No edits to the 11 frozen F3 Backlog root legacy view files.
- No edits to ST-HOLD.
- No edits to `marketKlineData`.
- No archive-only retirement or deletion work.
- No backend/API contract changes.

## Fix Summary

1. Navigation route truth:
   - Updated `src/config/menu.config.js` paths to canonical active router paths.
   - Removed legacy menu entries with no active route equivalent from this menu source.
   - Static menu-to-router check now reports `missingCount: 0`.

2. QUANTIX H1 E2E failure:
   - Confirmed `ArtDecoHeader` renders the dashboard H1 as `量化驾驶舱`.
   - Kept page structure unchanged.
   - Updated E2E assertion to the canonical H1 and retained `QUANTIX · 实时洞察 · 策略执行` subtitle evidence.

3. vue-i18n runtime error:
   - Added `app.use(i18n)` in `src/main-standard.ts`.
   - This fixes the `ArtDecoSkipLink.vue` runtime path that previously threw `Need to install with app.use function`.
   - Kept the startup hardening scoped to the same entrypoint by typing `window.$vue` and preventing first-control service-worker reload churn.

4. Market duplicated text strict locator:
   - Kept page structure unchanged.
   - Scoped the E2E assertion to `market-realtime-header`, avoiding the duplicate `PRESET: 核心蓝筹样本` text in the control row.

## Impact Evidence

GitNexus impact checks:

- `routes` in `web/frontend/src/router/index.ts`: LOW, 0 direct upstream symbols/processes.
- `menuConfig` in `web/frontend/src/config/menu.config.js`: LOW, 0 direct upstream symbols/processes.
- `useI18n` in `web/frontend/src/composables/useI18n.ts`: LOW, 4 upstream symbols, 0 processes.
- `main-standard.ts`: LOW, 0 direct upstream symbols/processes.
- `ArtDecoDashboard.vue`: LOW, 3 upstream symbols, 0 processes.
- `Realtime.vue`: LOW, 3 upstream symbols, 0 processes.

FUNCTION_TREE:

- Authorization moved to `approved-for-implementation`.
- Active allowed paths were corrected from the nonexistent `web/frontend/src/main.ts` to the actual `web/frontend/src/main-standard.ts`.
- `ft-governance validate` passed after the correction.
- `.governance/programs/artdeco-web-design-governance/tree.md` contains unrelated generated planning drift and is intentionally excluded from this M2 batch.

## Verification

Commands run:

- `node --check web/frontend/src/config/menu.config.js`: passed.
- Static menu/router path check: `missingCount: 0`.
- `npm run type-check`: passed.
- `npm run test -- src/router/__tests__/home-route.spec.ts src/router/__tests__/utils.spec.ts src/stores/__tests__/auth-guard-route-meta.spec.ts tests/unit/config/ai-route-canonical-paths.spec.ts tests/unit/components/SidebarMenu.spec.ts`: 5 files, 18 tests passed.
- `PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://localhost:3020 npx playwright test --config playwright.config.js --project=chromium tests/e2e/critical/menu-navigation-fixed.spec.ts tests/e2e/kline-chart.spec.ts tests/e2e/market-data.spec.ts`: 30 passed.
- `PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://localhost:3020 npm run test:e2e:business-smoke`: chromium 55 passed.
- `gitnexus detect_changes --scope staged`: 10 staged files, 4 changed indexed symbols, affected count 0, risk low, index fresh for staged diff.
- `opendog verification --id mystocks`: failing runs 0, cleanup blockers 0, refactor blockers 0; latest recorded build/test runs passed.

PM2:

- `mystocks-backend`: online at `http://localhost:8020`.
- `mystocks-frontend`: online at `http://localhost:3020`.

## Result

The five M1 E2E failures are fixed in the PM2-backed chromium business smoke suite.

M2 should proceed next to post-commit GitNexus refresh and then M3 full mainline gate validation. F3 Backlog remains frozen.
