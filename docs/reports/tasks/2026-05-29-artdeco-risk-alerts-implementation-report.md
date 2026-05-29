# ArtDeco Risk Alerts Implementation Report

Date: 2026-05-29
Target: `web/frontend/src/views/risk/Alerts.vue`
Approved brief: `docs/reports/tasks/2026-05-29-artdeco-risk-alerts-shape-brief.md`

## Scope

Implemented the approved `risk/Alerts.vue` shape brief as a page-level craft slice. The page now treats alert triage as the primary route job and keeps rule management as a secondary configuration area.

Changed files:

- `web/frontend/src/views/risk/Alerts.vue`
- `web/frontend/src/views/risk/__tests__/Alerts.spec.ts`

Supporting planning artifacts already produced:

- `docs/reports/tasks/2026-05-29-artdeco-impeccable-next-route-batch-plan.md`
- `docs/reports/tasks/2026-05-29-artdeco-risk-alerts-critique.md`
- `docs/reports/tasks/2026-05-29-artdeco-risk-alerts-shape-brief.md`

## Implemented Design Changes

- Replaced internal English scaffolding in the main route surface with Chinese operational copy.
- Added alert triage controls with `全部`, `高优先级`, `预警`, `普通`, and `仅未读`.
- Added computed filtering for unread, high-priority, warning, and normal alerts.
- Sorted the alert queue so unread high-priority alerts lead the table.
- Added a runtime status strip with visible row count and request ID.
- Converted the duplicated metric-card area into a compact summary strip so the alert table reaches the first desktop viewport sooner.
- Wrapped rule management in a visually secondary `规则配置` section below the alert table.
- Preserved route, API contracts, monitoring API calls, existing rule mutation behavior, and existing route-level provenance behavior.

## Verification

TDD:

- RED observed before implementation: `npm run test -- src/views/risk/__tests__/Alerts.spec.ts` failed because `[data-test="risk-alerts-triage-controls"]` did not exist.
- GREEN after implementation: same command passed.

Final checks:

- `npm run test -- src/views/risk/__tests__/Alerts.spec.ts`
  - 1 file passed
  - 8 tests passed
- `npx eslint src/views/risk/Alerts.vue`
  - 0 errors
  - 0 warnings
- `node scripts/check-artdeco-tokens.js --target-file src/views/risk/Alerts.vue`
  - ArtDeco Token Validation Passed
- `npm run type-check -- --pretty false`
  - exit code 0
  - type error lines 0
  - target file errors 0
- `E2E_FRONTEND_PORT=3022 FRONTEND_BASE_URL=http://127.0.0.1:3022 npx playwright test --config playwright.config.js --project=chromium tests/e2e/phase4-mainline-matrix.spec.ts -g "Risk-Alerts"`
  - Chromium
  - 4 tests passed

Browser inspection:

- Desktop 1280x720 screenshot: `/tmp/risk-alerts-1280x720-compact2.png`
- Desktop 1600x1000 screenshot: `/tmp/risk-alerts-1600x1000-compact2.png`
- The 1280x720 pass confirmed the alert table enters the first viewport after compacting the metric strip.
- The 1600x1000 pass confirmed the alert table is the dominant work area and the rule configuration section remains below it.

PM2 status:

- `mystocks-backend`: online at `http://localhost:8020`
- `mystocks-frontend`: online at `http://localhost:3020`

## Remaining Boundaries

- No backend, router, shared component, or global token migration was performed.
- No shared `ArtDecoTriageBar` or `ArtDecoStatusStrip` extraction was performed; extraction should wait until at least one more route proves the same pattern.
- Mobile and tablet redesign were intentionally out of scope because this project treats desktop Web as the supported target.
