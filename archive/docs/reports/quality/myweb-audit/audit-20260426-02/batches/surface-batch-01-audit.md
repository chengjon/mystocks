# Batch Audit Report: surface-batch-01

## Scope
- Module: surface
- Pages:
  - /risk/alerts
  - /risk/news
  - /watchlist/manage
- Batch rationale: close the shared stat-card count-kpi truth gap so canonical routes that only expose counts or labels stop leaking fabricated delta chrome or pseudo precision

## Agent Summary

### route-inventory
- `/risk/alerts`, `/risk/news`, and `/watchlist/manage` remain canonical routed entries at `src/views/risk/Alerts.vue`, `src/views/risk/News.vue`, and `src/views/watchlist/Manage.vue`.
- The watchlist route delegates to `WatchlistManager.vue`, but router truth remains the canonical wrapper route.

### functional-audit
- No new interaction blocker required a repair wave beyond restoring honest KPI semantics on the routed stat-card strips.

### data-state-audit
- Three high-severity count-kpi truth defects remained: count-only routed KPI cards inherited shared stat-card delta chrome and exact-decimal precision even though the current payloads only proved plain counts or labels.

## Consolidated Issue Statistics
- Blocking: 0
- High: 3
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: canonical routes that reuse shared stat-card defaults can accidentally imply unsupported movement semantics by rendering count-only KPIs as `+0%`, flat-change dots, arrows, or decimal-formatted pseudo precision.
- Occurrence basis:
  - `/risk/alerts` previously rendered `规则总数`, `启用规则`, `未读告警`, and `高优先级` as count cards with faux delta chrome
  - `/risk/news` previously rendered `公告总数`, `今日公告`, `重要公告`, and `原文链接` as count cards with faux delta chrome
  - `/watchlist/manage` previously rendered overview counts such as `组合数量` and `当前股票数` with faux delta chrome and pseudo precision
- Shared component or token involved:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue`
- Suggested follow-up scope: continue later routed-page audits for remaining count-only KPI strips and decide whether a dedicated shared-surface batch can safely narrow the shared stat-card default without hitting the current HIGH blast radius.

## Main Skill Decisions
- duplicates merged: no; each route kept its own consolidated issue for page-local repair ownership, but the batch records one repeated shared pattern
- priority order applied: routed surface truth > shared default cleanup
- primary owners selected:
  - `web/frontend/src/views/risk/Alerts.vue`
  - `web/frontend/src/views/risk/News.vue`
  - `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`
- shared-impact review items:
  - `risk-alerts-issue-05`
  - `risk-news-issue-05`
  - `watchlist-manage-issue-03`
- fixes applied:
  - `risk-alerts-issue-05`
  - `risk-news-issue-05`
  - `watchlist-manage-issue-03`
- deferred items:
  - shared `ArtDecoStatCard.vue` default change

## Fix Summary
- Updated the three routed KPI strips to pass plain string counts and explicitly disable shared stat-card delta chrome with `:show-change="false"`.
- Added routed regressions for `/risk/alerts`, `/risk/news`, and `/watchlist/manage` that assert there are no `.artdeco-stat-change` nodes, no `+0%`, and no decimal-formatted pseudo precision on count-only KPI strips.
- Strengthened Phase 2 and Phase 4 matrix assertions so the canonical routes keep this count-kpi truth in future browser runs.
- Extended `myweb-audit` with a `v1.32` count-kpi delta truth rule so future audits explicitly check count-only KPI strips for faux delta chrome and pseudo precision.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/surface-batch-01-repair-approval.yaml`
- Approved issue ids:
  - `risk-alerts-issue-05`
  - `risk-news-issue-05`
  - `watchlist-manage-issue-03`
- Deferred issue ids:
  - shared `ArtDecoStatCard.vue` default change
- Shared-impact items approved for current batch:
  - `risk-alerts-issue-05`
  - `risk-news-issue-05`
  - `watchlist-manage-issue-03`
- Shared-impact items deferred to later batch:
  - shared `ArtDecoStatCard.vue` default change

## Unresolved Items
- No approved route-local repair remains unimplemented in `surface-batch-01`.

## Reasons Not Fixed
- The shared `ArtDecoStatCard.vue` default was not changed in this batch because GitNexus impact marked the shared owner `HIGH` with 96 upstream files. The defect pattern is documented and deferred for a later dedicated shared-surface wave.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - real routed verification used a real backend login token from `/api/v1/auth/login`
- Regression checks completed:
  - `npx vitest run src/views/risk/__tests__/Alerts.spec.ts src/views/risk/__tests__/News.spec.ts src/views/watchlist/__tests__/Manage.spec.ts` -> passed `3/3`
  - `npx vitest run src/views/risk/__tests__/Alerts.spec.ts src/views/risk/__tests__/News.spec.ts src/views/watchlist/__tests__/Manage.spec.ts src/views/watchlist/__tests__/Signals.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts` -> passed `9/9`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase2-mainline-matrix.spec.ts tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `24` structurally valid tests
  - targeted routed-page verification confirmed:
    - actual PM2 `/risk/alerts` now shows KPI values `8 / 8 / 0 / 0` with zero `.artdeco-stat-change` nodes
    - actual PM2 `/risk/news` now shows KPI values `0 / 0 / 0 / 0` with zero `.artdeco-stat-change` nodes
    - actual PM2 `/watchlist/manage` now shows overview values `18 / 0 / 0 / 0` with zero `.artdeco-stat-change` nodes
    - all three real routes no longer show `+0%` or decimal-formatted pseudo precision on count-only KPI strips
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser paths
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/surface-batch-01-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/surface-batch-01-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/surface-batch-01-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/surface-batch-01-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/surface-batch-01-manifest.yaml` -> passed
- GitNexus staged-scope note:
  - `gitnexus_detect_changes({ scope: "staged" })` returned `risk_level: low`, `changed_files: 77`, `changed_count: 260`, and `affected_count: 0`, but the staged set remained mixed with earlier batch files so the result is recorded as observation-only rather than isolated `surface-batch-01` scope
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online

## Next Batch Plan
- Continue routed-page audits for remaining count-only KPI strips that still reuse shared stat-card defaults.
- Revisit `ArtDecoStatCard.vue` in a later dedicated shared-surface batch only after the shared blast radius is narrowed or additional route-level audits prove the current defect pattern is broad enough to justify a coordinated shared fix.
