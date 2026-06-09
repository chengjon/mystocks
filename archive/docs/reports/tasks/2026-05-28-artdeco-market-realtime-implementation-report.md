# Implementation Report: `market/Realtime.vue` ArtDeco Pilot

Date: 2026-05-28

OpenSpec change: `add-artdeco-impeccable-design-gate`

Approval wording: `批准实施 market/Realtime.vue shape brief`

## 1. Implemented Scope

Target file:

- `web/frontend/src/views/market/Realtime.vue`

Implemented within the approved shape scope:

- compact route header band while preserving the existing `实时行情工作台` heading contract
- single control row with preset selection and metadata
- table-first primary work area with a separate breadth distribution panel
- explicit runtime state model for loading, refreshing, live, cache, stale, degraded, empty, and error
- freshness timer and snapshot age labeling
- cache, stale, degraded, empty, and error state banners
- touched-scope style cleanup without changing global tokens

Compatibility retained:

- `.toolbar` class remains on the new control row for existing E2E selectors
- `PRESET: 核心蓝筹样本` metadata remains visible for existing E2E selectors
- no route, API, or wrapper import contract was changed

## 2. Out of Scope

Not performed:

- backend API contract changes
- route restructuring
- mobile redesign
- new charting library
- broad token migration
- global component extraction
- `$impeccable extract`, because a second consumer has not yet proven reuse

## 3. Verification

| Check | Command | Result |
|---|---|---|
| OpenSpec strict validation | `openspec validate add-artdeco-impeccable-design-gate --strict` | Pass |
| Diff whitespace check | `git diff --check -- web/frontend/src/views/market/Realtime.vue openspec/changes/add-artdeco-impeccable-design-gate/tasks.md` | Pass |
| ArtDeco token check | `node scripts/check-artdeco-tokens.js --target-file src/views/market/Realtime.vue` | Pass |
| ESLint targeted check | `npx eslint src/views/market/Realtime.vue` | Pass |
| Type check | `npm run type-check -- --pretty false` | Pass, 0 type errors, no `Realtime.vue` errors |
| PM2 service status | `pm2 list` | `mystocks-backend` online at `http://localhost:8020`; `mystocks-frontend` online at `http://localhost:3020` |
| E2E first attempt | `npm run test:e2e:business-smoke -- --reporter=line` | Did not run because Playwright tried to bind occupied PM2 port `3020` |
| E2E targeted external PM2 | `PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://localhost:3020 FRONTEND_PORT=3020 npx playwright test --config playwright.config.js --project=chromium tests/e2e/market-data.spec.ts --reporter=line` | Pass, 18 passed, 0 failed, 0 skipped |
| GitNexus pre-edit impact check | `gitnexus_impact({ target: "web/frontend/src/views/market/Realtime.vue", direction: "upstream" })` | Pass, LOW risk; direct importers limited to ArtDeco wrapper tabs |
| GitNexus index refresh | `gitnexus analyze` | Partial: an extended run regenerated `.gitnexus/meta.json` with 91,600 nodes and 209,974 edges, but the final post-amend refresh hit the 120s tool limit and could not be confirmed against the final commit |
| GitNexus commit-scope detect changes | `gitnexus_detect_changes({ scope: "compare", base_ref: "HEAD~1" })` | Blocked: MCP repo worker timed out twice at 30s. The original staged check cannot be rerun after commit; scoped `git show --name-only HEAD` confirms the committed file set listed in this report |

## 4. Notes

- The first targeted E2E run caught two compatibility regressions: the heading text changed from `实时行情工作台`, and `.toolbar` / `PRESET:` selectors were removed. Both were restored while preserving the approved compact layout.
- The worktree already contained many unrelated `web/frontend/**` dirty files before this implementation. This report only claims the scoped `market/Realtime.vue` pilot and OpenSpec task updates.
- The intended batch is committed as `feat(web): add ArtDeco realtime design gate pilot` and contains the scoped Realtime page, OpenSpec change files, and task-report artifacts. No unstaged changes remain for those committed paths.
- GitNexus graph freshness remains an environment/tooling limitation for this handoff. Re-run `gitnexus analyze` locally before relying on graph-level `detect_changes` for the final commit.
