# Route Header Migration Line Handoff - 2026-06-05

## Purpose

This document closes the current ArtDeco Route Header Shell migration line and hands off remaining work for the upcoming dirty worktree governance pass.

The line focused on replacing direct `ArtDecoHeader` usage in canonical route pages with `ArtDecoRouteHeader`, preserving page status, route meta, refresh actions, and E2E-visible selectors.

## Completed Commits

### SCSS Governance Line Closed Before This Route Header Line

The SCSS large-file governance line was declared complete by the user. Recent relevant commits in the current history include:

- `0eaa4d510 refactor(web): split ArtDeco button variant styles`
- `2c861530b refactor(web): split ArtDeco chart and table styles`
- `d55418ad4 refactor(web): split performance table styles`
- `879deabdb refactor(web): split heatmap card styles`
- `ddf4ecc4b refactor(web): split ArtDeco sidebar styles`

### Route Header Shell Migrations Completed

1. `af23918df refactor(web): migrate market technical route header`
   - Route: `/market/technical`
   - Files:
     - `web/frontend/src/views/market/Technical.vue`
     - `web/frontend/tests/e2e/market-data.spec.ts`
   - Preserved:
     - `market-technical-header`
     - `market-technical-refresh`
     - `REQ / SYMBOL / POINTS`
     - refresh action behavior

2. `d920e6bfa refactor(web): migrate data industry route header`
   - Route: `/data/industry`
   - Files:
     - `web/frontend/src/views/data/Industry.vue`
     - `web/frontend/tests/e2e/market-data.spec.ts`
   - Preserved:
     - `DATA / REQ_ID / TIME`
     - page status text/type
     - refresh action behavior
   - Added:
     - `data-industry-header`
     - `data-industry-refresh`

3. `bf6fcc437 refactor(web): migrate data concept route header`
   - Route: `/data/concept`
   - Files:
     - `web/frontend/src/views/data/Concepts.vue`
     - `web/frontend/tests/e2e/market-data.spec.ts`
   - Preserved:
     - `REQ / SECTORS / LEADER`
     - page status text/type
     - refresh action behavior
   - Added:
     - `data-concept-header`
     - `data-concept-refresh`

## Verification Evidence

The final completed route slice, `/data/concept`, passed:

- `git diff --cached --check -- web/frontend/src/views/data/Concepts.vue web/frontend/tests/e2e/market-data.spec.ts`
- `npm run test -- src/views/data/__tests__/Concepts.spec.ts` - `3/3 passed`
- `npm run test -- tests/unit/views/data-concept-refresh-fallback.spec.ts` - `1/1 passed`
- `npm run test -- tests/unit/config/data-route-canonical-paths.spec.ts` - `4/4 passed`
- `npm run test -- tests/unit/config/pageConfig.test.ts` - `13/13 passed`
- `node scripts/check-artdeco-tokens.js --target-file src/views/data/Concepts.vue --target-file tests/e2e/market-data.spec.ts`
- `npm run type-check` - `vue-tsc --noEmit passed`
- `npx playwright test tests/e2e/market-data.spec.ts --project=chromium -g "should open data concept page"` - `1/1 passed`
- `scripts/run_e2e_pm2.sh` - exit code `0`, Chromium `14/14 passed`

Earlier route slices also passed their focused unit/config/static/E2E checks and PM2 smoke before commit.

## GitNexus Status

GitNexus was used before edits and before commits where possible.

Observed limitations:

- `Industry.vue` pre-edit `impact` initially returned `UNKNOWN` because LadybugDB was temporarily unavailable.
- `Concepts.vue` pre-edit `impact` returned `not_found` for both `DataConceptsPage` and `Concepts`; no HIGH or CRITICAL risk was reported.
- `detect_changes(scope=staged)` succeeded before the route commits and returned `risk_level=low`, with no affected processes.
- The GitNexus index remained stale during this line.
- Per user instruction, `npx gitnexus analyze` was not used. If re-indexing becomes necessary, use local `gitnexus analyze`, not `npx gitnexus analyze`.

## Current Dirty State

At handoff time, selected status showed these unstaged files:

- `web/frontend/src/views/data/Concepts.vue`
- `web/frontend/src/views/data/Industry.vue`
- `web/frontend/src/views/market/LHB.vue`

The staged area was empty after `bf6fcc437`.

Important isolation notes:

- `Concepts.vue` and `Industry.vue` had pre-existing unstaged changes. Route Header migration hunks were committed by staging only the migration delta from `HEAD`; the remaining dirty changes were intentionally left unstaged.
- `market/LHB.vue` was explicitly not processed. The user said it must wait for later Vue slimming.
- The earlier external backend files are no longer shown in the selected staged/dirty status at this handoff point:
  - `tests/api/file_tests/test_data_source_config_api.py`
  - `web/backend/app/api/_data_source_config_responses.py`
  - `web/backend/app/api/data_source_config.py`
  Do not assume why they disappeared without checking current git history and status.

## Remaining Route Header Migration Candidates

Next route by canonical router order:

1. `/data/fund-flow`
   - File: `web/frontend/src/views/data/FundFlow.vue`
   - Status: still uses `ArtDecoHeader`
   - Recommended next Route Header slice if continuing this line.

Explicitly deferred:

- `/market/lhb`
  - File: `web/frontend/src/views/market/LHB.vue`
  - Reason: user said it must wait for later Vue slimming.

Other active route candidates still using `ArtDecoHeader` or needing verification:

- `/dashboard` - `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- `/trade/history` - `web/frontend/src/views/trade/History.vue`
- `/risk/overview` - `web/frontend/src/views/risk/Overview.vue`
- `/risk/stop-loss` - `web/frontend/src/views/risk/StopLoss.vue`
- `/risk/news` - `web/frontend/src/views/risk/News.vue`
- `/system/health` - `web/frontend/src/views/system/Health.vue`
- `/system/api` - `web/frontend/src/views/system/API.vue`
- `/system/resources` - `web/frontend/src/views/system/Resources.vue`
- `/system/data` - `web/frontend/src/views/system/DataSource.vue`

Some ArtDeco page/template paths also still contain `ArtDecoHeader`, but verify active routing through `web/frontend/src/router/index.ts` before editing. Do not treat `artdeco-pages/` as canonical by default unless the router points there.

## Dirty Worktree Governance Recommendations

For the upcoming dirty directory governance pass:

1. Start with path-specific status, not full assumptions.
   - Use `git status --short -- <paths>` for targeted files.
   - Keep unrelated dirty files out of route migration commits.

2. Classify dirty files before touching them.
   - `Concepts.vue` and `Industry.vue` still contain leftover unstaged changes after route-header hunks were committed.
   - `LHB.vue` is intentionally deferred.
   - Do not revert these files unless the user explicitly authorizes it.

3. For dirty Vue files, prefer partial staging from `HEAD`.
   - During this line, route-header commits were isolated by staging only the generated migration delta from `HEAD`, leaving unrelated dirty worktree changes unstaged.
   - Re-check `git diff --cached --name-status` before every commit.

4. Keep verification evidence fresh.
   - For each route/header slice:
     - focused component test
     - relevant route config test
     - `pageConfig.test.ts`
     - ArtDeco token check
     - `npm run type-check`
     - focused Chromium E2E
     - `scripts/run_e2e_pm2.sh` for route/layout changes

5. PM2/backend caveat.
   - Frontend `http://localhost:3020` was reachable after final PM2 restart.
   - Backend PM2 was online, but `http://localhost:8020/health` still failed to connect.
   - This backend health issue was not part of the frontend Route Header line.

## Suggested Next Step

If continuing Route Header migration after dirty governance, start with `/data/fund-flow`:

- Pre-check: `web/frontend/src/views/data/FundFlow.vue`
- Add route shell test ids similar to:
  - `data-fund-flow-header`
  - `data-fund-flow-refresh`
- Add focused E2E assertion in `web/frontend/tests/e2e/market-data.spec.ts`
- Avoid `market/LHB.vue` until the later Vue slimming task is explicitly started.

