# Batch Audit Report: system-batch-05

## Scope
- Module: system
- Pages:
  - `/system/health`
  - `/system/api`
  - `/system/data`
  - `/system/config`
- Batch rationale: close the routed system top-strip count-kpi leaks and the system health probe-envelope mismatch, then feed both discoveries back into the audit skill

## Agent Summary

### route-inventory
- `/system/health`, `/system/api`, `/system/data`, and `/system/config` continue to resolve directly to canonical `web/frontend/src/views/system/*.vue` entries.

### functional-audit
- No new routed interaction-path defect required a separate action-flow repair wave in this batch.

### data-state-audit
- Three medium-severity issue clusters remained:
  - system health-family pages were discarding successful plain `/api/health` payloads because the wrapper expected `UnifiedResponse.success/data`
  - system health-family and system-data KPI strips were inheriting shared stat-card delta chrome and pseudo precision on plain count or label surfaces
  - system-config could collapse a valid summary fallback to `UNAVAILABLE` when detailed health metrics were absent

### visual-artdeco-audit
- No batch-dominant visual defect required a separate repair wave after the route-local KPI truth fixes landed.

### responsive-a11y-audit
- No new desktop-breakpoint or a11y defect required a repair wave in this batch.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 3
- Low: 0

## Pattern Findings
- Repeated issue pattern:
  - routed probe pages can return successful plain-object payloads and must not be downgraded to unavailable merely because a generic wrapper expects a `UnifiedResponse` envelope
  - routed count and label KPI strips must suppress shared stat-card delta chrome when the current payload only proves plain counts or labels
- Occurrence basis:
  - `/system/health` and `/system/api` both hit live `200` `/api/health` responses while still rendering `UNKNOWN / N/A / N/A / 3` before repair
  - `/system/health`, `/system/api`, and `/system/data` all rendered flat-change chips or pseudo precision on plain KPI cards before repair
  - `/system/config` already had a summary normalizer but the wrapper-envelope mismatch prevented the fallback from ever receiving a successful plain health payload
- Shared component or token involved:
  - rejected for current batch: `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue` (`HIGH` blast radius)
  - rejected for current batch: `web/frontend/src/api/index.ts` (`MEDIUM` blast radius)
  - accepted page-family owner: `web/frontend/src/views/system/healthProbeContract.ts`
- Suggested follow-up scope:
  - future audits should verify whether any other routed health or readiness pages depend on plain probe contracts
  - count-kpi truth should continue to be applied page-locally until a dedicated shared `ArtDecoStatCard` batch is approved

## Main Skill Decisions
- duplicates merged:
  - paired `/system/health` and `/system/api` probe-envelope plus KPI findings were consolidated into one health-family issue because they shared one page-family adapter plus the same route-local stat-card pattern
- priority order applied:
  - probe-envelope truth > count-kpi delta truth > generic stat-card styling
- primary owners selected:
  - `web/frontend/src/views/system/healthProbeContract.ts`
  - `web/frontend/src/views/system/DataSource.vue`
- shared-impact review items:
  - `web/frontend/src/api/index.ts` reviewed but not changed due `MEDIUM` blast radius
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue` reviewed but not changed due `HIGH` blast radius
- fixes applied:
  - `system-health-family-issue-01`
  - `system-data-issue-01`
  - `system-config-issue-01`
- deferred items: none

## Fix Summary
- Added a page-family `healthProbeContract` adapter so system health probes can normalize successful plain `/api/health` payloads before wrapper-level success checks.
- Updated `/system/health` and `/system/api` to use the adapter and to render honest plain KPI strips with `show-change=false`.
- Updated `/system/data` to render honest plain KPI strips with `show-change=false`.
- Updated `/system/config` so the detailed-health fallback can still consume a successful plain health summary path.
- Tightened system page tests so the `useArtDecoApi` mock no longer masks wrapper-envelope mismatches by silently accepting plain payloads that runtime code would reject.
- Extended `myweb-audit` with `v1.33` probe-envelope truth while reusing `v1.32` count-kpi delta truth.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-05-repair-approval.yaml`
- Approved issue ids:
  - `system-health-family-issue-01`
  - `system-data-issue-01`
  - `system-config-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch:
  - shared `ArtDecoStatCard.vue` default cleanup
  - shared `api/index.ts` transport normalization

## Unresolved Items
- No approved repair remains unimplemented in `system-batch-05`.

## Reasons Not Fixed
- The shared `ArtDecoStatCard.vue` default remains unchanged because GitNexus reported `HIGH` upstream blast radius, so this batch stayed page-local.
- The shared `api/index.ts` entry remains unchanged because GitNexus reported `MEDIUM` blast radius and the discovered probe-envelope defect was isolated to the routed system health family for this run.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/system/__tests__/API.spec.ts src/views/system/__tests__/Health.spec.ts src/views/system/__tests__/DataSource.spec.ts src/views/system/__tests__/Settings.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` -> passed `14/14`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `11` tests
  - `git diff --check -- ...system batch paths...` -> passed
- Targeted routed-page verification confirmed:
  - `/system/health` now shows `HEALTHY / N/A / 1.0.0 / 3` with `0` `.artdeco-stat-change` nodes
  - `/system/api` now shows `HEALTHY / N/A / 1.0.0 / 3` with `0` `.artdeco-stat-change` nodes
  - `/system/data` now shows `19 / 19 / ON / <REQ_ID>` with `0` `.artdeco-stat-change` nodes
  - none of the three routed strips contain `+0%`, `3.00`, `2.00`, `1.00`, or `0.00`
  - actual PM2 requests reached `http://localhost:3020/api/health`, `http://localhost:3020/api/health/ready`, and `http://localhost:3020/api/v1/data-sources/config/` with `200`
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` runner still cannot execute Chromium on this machine because the local Playwright chromium executable is missing, so the batch relied on system `google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` is recorded as mixed-staged observation only for this run
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Continue system-domain audits with the strengthened `v1.33` probe-envelope truth and `v1.32` count-kpi truth rules, prioritizing any remaining routed health, readiness, runtime, or count-strip surfaces that still rely on wrapper assumptions or shared stat-card defaults.
