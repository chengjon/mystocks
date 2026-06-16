# B4.013-M1-C Mainline Route Runtime Blockers No-Source Audit

Date: 2026-06-16
Branch: `wip/root-dirty-20260403`
Head at audit start: `4bbb3ded1 B4.013-M1-B: align market kline period contract`
Governance node: `b4-013-m1c-mainline-route-runtime-blockers-audit`
Mode: no-source audit
Source edits authorized: false

## Scope

This audit applies the B4.013 runtime-first method to the remaining primary navigation entrypoints after M1-B:

- `/`
- `/dashboard`
- `/market` and `/market/realtime` as a regression spot-check
- `/data`
- `/watchlist`
- `/strategy`
- `/trade`
- `/risk`
- `/system`

Execution surface:

- PM2-backed frontend: `http://127.0.0.1:3020`
- PM2-backed backend: `http://127.0.0.1:8020`
- Browser: Playwright Chromium
- Auth: seeded local account `admin/admin123`

Explicit exclusions:

- No source, test, runtime, route, API, OpenSpec, ST-HOLD, marketKlineData, B4.012, or external dirty-file edits
- No pageConfig or route migration
- No visual polish fix
- No deletion, archive, or residual dirty cleanup

## Batch Manifest

```yaml
audit_run_id: b4-013-m1c-20260616
batch_id: mainline-route-runtime-batch-01
module: cross-domain-mainline
scope:
  requested_by: user
  pages:
    - route: /
      page_key: root-dashboard-redirect
      route_class: compatibility-redirect
      canonical_entry: web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue
    - route: /dashboard
      page_key: dashboard
      route_class: canonical-page
      canonical_entry: web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue
    - route: /market
      page_key: market-default-redirect
      route_class: compatibility-redirect
      canonical_entry: web/frontend/src/views/market/Realtime.vue
    - route: /market/realtime
      page_key: market-realtime
      route_class: canonical-page
      canonical_entry: web/frontend/src/views/market/Realtime.vue
    - route: /data
      page_key: data-default-redirect
      route_class: compatibility-redirect
      canonical_entry: web/frontend/src/views/data/Industry.vue
    - route: /watchlist
      page_key: watchlist-default-redirect
      route_class: compatibility-redirect
      canonical_entry: web/frontend/src/views/watchlist/Manage.vue
    - route: /strategy
      page_key: strategy-default-redirect
      route_class: compatibility-redirect
      canonical_entry: web/frontend/src/views/strategy/List.vue
    - route: /trade
      page_key: trade-default-redirect
      route_class: compatibility-redirect
      canonical_entry: web/frontend/src/views/TradingDashboard.vue
    - route: /risk
      page_key: risk-default-redirect
      route_class: compatibility-redirect
      canonical_entry: web/frontend/src/views/risk/Overview.vue
    - route: /system
      page_key: system-default-redirect
      route_class: compatibility-redirect
      canonical_entry: web/frontend/src/views/system/Settings.vue
  compatibility_redirects:
    - /
    - /market
    - /data
    - /watchlist
    - /strategy
    - /trade
    - /risk
    - /system
batch_rationale: Runtime-first verification of primary navigation defaults after the market K-line contract fix.
audit_roles:
  - route-inventory
  - functional-audit
  - data-state-audit
  - visual-artdeco-audit
  - responsive-a11y-audit
environment:
  frontend_url: http://127.0.0.1:3020
  backend_url: http://127.0.0.1:8020
  browser_tool: playwright
  execution_surface: live-audit
  frontend_runtime_mode: reuse-existing-pm2
  fallback_log:
    - Initial 9-route script exceeded the context-mode tool ceiling and was split into smaller route batches.
    - Some redirect routes timed out on `page.goto(..., waitUntil: domcontentloaded)` while later DOM reads or fresh-page reruns proved route content; these timeouts are recorded as automation/navigation timing noise, not standalone route truth.
verification_plan:
  verification_strategy: chromium-only-route-smoke
  browser_project: chromium
  breakpoints: [1440]
  required_states: [default]
  notes:
    - This is a no-source blocker audit, not a full myweb-audit repair batch.
repair_approval:
  status: not_requested
  approved_findings: []
  deferred_findings: []
state_tracking:
  completed_pages:
    - root-dashboard-redirect
    - dashboard
    - market-default-redirect
    - market-realtime
    - data-default-redirect
    - watchlist-default-redirect
    - strategy-default-redirect
    - trade-default-redirect
    - risk-default-redirect
    - system-default-redirect
  pending_pages: []
  fixed_files: []
  shared_impact:
    candidates:
      - dashboard runtime aggregate data/provenance state
      - ArtDecoIcon registry fallback warnings
    confirmed: []
  validation_status:
    syntax: not-run-no-source
    typecheck: not-run-no-source
    pm2: observed-online
    e2e: chromium-route-smoke-run
    gitnexus_staged_detect: pending-no-source-report-package
  staged_scope:
    mode: not-started
    files: []
    verdict_origin: none
status: decision-prepared
```

## Route Truth And Runtime Matrix

| Route | Runtime target | Evidence | Result |
| --- | --- | --- | --- |
| `/` | `/dashboard` | fresh page rerun rendered `交易室 - MyStocks`, text length 544 | Visible; redirects to dashboard |
| `/dashboard` | `/dashboard` | extended fresh run rendered `交易室 - MyStocks`, text length 715 | Visible, but aggregate dashboard state remains `DATA: PENDING`, `REQ: N/A` |
| `/market` | `/market/realtime` | parent redirect had navigation timing noise; fresh leaf rerun rendered `实时行情 - MyStocks`, text length 1516 | Visible after verification-ladder rerun |
| `/market/realtime` | `/market/realtime` | `/api/v1/market/quotes?...` returned 200; `实时行情工作台` visible | M1-B regression spot-check green |
| `/data` | `/data/industry` | rendered `板块动向 - MyStocks`, text length 1568 | Visible |
| `/watchlist` | `/watchlist/manage` | rendered `组合管理 - MyStocks`, text length 373; `/api/v1/monitoring/watchlists` 200 and `/api/v1/monitoring/watchlists/18/stocks` 200 | Visible, but prop warnings remain |
| `/strategy` | `/strategy/repo` | rendered `策略仓库 - MyStocks`, text length 1371 | Visible |
| `/trade` | `/trade/terminal` | rendered `交易操作 - MyStocks`, text length 1380 | Visible |
| `/risk` | `/risk/overview` | rendered `风险概览 - MyStocks`, text length 1355 | Visible |
| `/system` | `/system/config` | rendered `系统配置 - MyStocks`, text length 3075 | Visible |

## Static Owner Notes

Route truth:

- `/dashboard` is still backed by `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.
- `/market/realtime` is backed by `web/frontend/src/views/market/Realtime.vue`.
- `/data` redirects to `/data/industry`, backed by `web/frontend/src/views/data/Industry.vue`.
- `/watchlist` redirects to `/watchlist/manage`, backed by `web/frontend/src/views/watchlist/Manage.vue`.
- `/strategy` redirects to `/strategy/repo`, backed by `web/frontend/src/views/strategy/List.vue`.
- `/trade` redirects to `/trade/terminal`, backed by `web/frontend/src/views/TradingDashboard.vue`.
- `/risk` redirects to `/risk/overview`, backed by `web/frontend/src/views/risk/Overview.vue`.
- `/system` redirects to `/system/config`, backed by `web/frontend/src/views/system/Settings.vue`.

Dashboard data/provenance owners:

- `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
- `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.fetchers.ts`
- `web/frontend/src/api/services/dashboardService.ts`
- `web/frontend/src/api/services/dashboardServiceData.ts`

## Findings

### M1C-001 Dashboard Remains Visible But Aggregate Data Truth Stays Pending

- Severity: High
- Source roles: data-state-audit, functional-audit
- Affected route: `/dashboard`
- Evidence:
  - Extended fresh run rendered dashboard content.
  - Visible shell still showed `DASHBOARD DATA: PENDING`, `REQ: N/A`, and `SYNC: PENDING` after the route was usable.
  - Captured requests showed dashboard page/component modules and `/api/v1/market/lhb?limit=10` 200, but primary dashboard aggregate request/provenance did not reach verified `REAL/READY` truth in the observed window.
- Expected:
  - The primary dashboard route should either verify core dashboard slices and expose real request provenance, or clearly classify which primary slices are unavailable/degraded.
- Actual:
  - The route is visible but leaves the aggregate route status in pending truth while still presenting multiple dashboard surfaces.
- Primary repair target:
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
  - `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.fetchers.ts`
  - `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- Can fix frontend: likely yes, pending a focused dashboard source audit.
- Dedupe key: `/dashboard:data-state:useArtDecoDashboard`
- Recommended next package:
  - `B4.013-M1-D dashboard aggregate runtime data/provenance standardization`

### M1C-002 Watchlist Manage Renders But Emits Required Prop Warnings

- Severity: Medium
- Source roles: functional-audit, data-state-audit
- Affected route: `/watchlist/manage`
- Evidence:
  - Page rendered `组合管理 - MyStocks`.
  - `/api/v1/monitoring/watchlists` returned 200.
  - `/api/v1/monitoring/watchlists/18/stocks` returned 200.
  - Console warnings reported missing required props on `WatchlistManager`: `watchlists`, `activeWatchlistId`, and `currentStocks`.
- Expected:
  - Watchlist manager composition should pass the props it declares as required, or the component contract should make route-owned defaults explicit.
- Actual:
  - Runtime renders, but prop contract is inconsistent and could hide state drift or future strict-mode failures.
- Primary repair target:
  - `web/frontend/src/views/watchlist/Manage.vue`
  - nearest shared owner to confirm: `WatchlistManager`
- Can fix frontend: likely yes.
- Dedupe key: `/watchlist/manage:data-state:WatchlistManager`
- Recommended disposition:
  - P1/P2 follow-up after dashboard state truth, unless watchlist becomes the next user-critical flow.

### M1C-003 Repeated ArtDecoIcon Fallback Warnings Across Mainline Routes

- Severity: Low
- Source roles: visual-artdeco-audit, functional-audit
- Affected routes:
  - `/dashboard`
  - `/market/realtime`
  - `/data/industry`
  - `/strategy/repo`
  - `/trade/terminal`
  - `/risk/overview`
  - `/system/config`
- Evidence:
  - Console warnings include missing `Monitor`, `BarChart2`, and `plus` icons with fallback to `Alert`.
- Expected:
  - Mainline route icons should resolve through the ArtDeco icon registry or use supported names.
- Actual:
  - Visual fallback is non-blocking but noisy and can mask actual console regressions.
- Primary repair target:
  - ArtDeco icon registry or route/component icon usage sites.
- Can fix frontend: yes, but shared-impact.
- Dedupe key: `mainline:visual:ArtDecoIcon`
- Recommended disposition:
  - Shared UI cleanup batch after runtime blockers.

### M1C-004 Playwright Navigation Event Timeouts On Some Redirect/Heavy Routes

- Severity: Medium as test reliability; not classified as a route-rendering blocker
- Source roles: route-inventory, functional-audit
- Affected observations:
  - The initial all-route script exceeded the tool ceiling.
  - Some `page.goto(..., waitUntil: domcontentloaded)` calls timed out even when later DOM reads or fresh-page reruns proved visible content.
  - `/market/realtime` returned route content under a fresh-page rerun even though `page.goto` still reported a timeout.
- Expected:
  - Smoke tests should wait for route-owned visible content, not only for navigation lifecycle events.
- Actual:
  - Navigation lifecycle waits can produce false negatives for this PM2/Vite runtime.
- Primary repair target:
  - E2E/smoke harness wait policy, not route source.
- Can fix frontend: no direct page source fix recommended from this audit.
- Dedupe key: `mainline:route:playwright-navigation-wait-policy`
- Recommended disposition:
  - Record as E2E harness hardening candidate; do not block mainline source work on this alone.

## Decision

No confirmed P0 blank-page route blocker remains across the primary navigation default entrypoints after M1-B.

The next business-mainline issue is dashboard data/provenance truth:

- `/dashboard` is visible and navigable.
- It does not yet prove core dashboard data readiness.
- It remains in `PENDING / REQ: N/A` aggregate truth after an extended route observation.

This should be handled before returning to B4.012 residual cleanup, visual polish, or broad test rework.

## Recommended Next Step

Start:

`B4.013-M1-D dashboard aggregate runtime data/provenance standardization`

Recommended first phase:

- no-source focused dashboard data-flow audit if source authorization is not granted immediately

Recommended source-authorization candidates after focused audit:

- `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
- `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.fetchers.ts`
- focused dashboard tests, if an existing focused test owner is found
- closeout worklog and FUNCTION_TREE governance files

Non-goals for M1-D:

- No market K-line changes
- No watchlist prop cleanup unless separately authorized
- No global icon registry cleanup unless separately authorized
- No B4.012 residual cleanup
- No ST-HOLD, OpenSpec, backend API redesign, or external dirty-file changes
