# System Data Count KPI Truth Audit

## Scope
- `/system/data`

## Routed Defect Closed
- The routed data-source top strip rendered plain counts and labels through the shared stat-card default path, which produced fabricated flat-change chips and pseudo precision on a primary live config surface.

## Repair
- Updated `web/frontend/src/views/system/DataSource.vue` so the routed KPI strip renders string values and explicitly sets `show-change=false` for all four cards.
- Added routed unit regression and routed `phase4` E2E assertions for the `.stats-strip` surface.

## Verification Evidence
- Regression:
  - `npx vitest run src/views/system/__tests__/DataSource.spec.ts` passed
- Live browser verification with Playwright-library + system `google-chrome`:
  - `/system/data` now shows `19 / 19 / ON / <REQ_ID>` on the top strip
  - the routed strip has `0` `.artdeco-stat-change` nodes
  - the routed strip no longer contains `+0%`, `3.00`, `2.00`, `1.00`, or `0.00`
  - actual PM2 requests reached `http://localhost:3020/api/v1/data-sources/config/` with `200`

## Rule Feedback
- This page reused the existing `v1.32` count-kpi delta truth rule rather than introducing a new audit rule.
