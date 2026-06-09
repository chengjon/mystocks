# Batch Audit Report: watchlist-batch-02

## Scope
- Module: watchlist
- Pages:
  - /watchlist/signals
- Batch rationale: close the donor-route semantic truth gap so the canonical watchlist signals route stops leaking strategy-workbench semantics from a shared strategy surface

## Agent Summary

### route-inventory
- `/watchlist/signals` remains the canonical routed entrypoint at `src/views/watchlist/Signals.vue`.
- The route still wraps the shared `StrategySignalsTab.vue` surface, so route-local truth depends on parameterizing a shared owner rather than forking the page.

### functional-audit
- No new interaction blocker required a repair wave beyond restoring route-local copy and task framing semantics.

### data-state-audit
- One high-severity donor-route semantic truth defect remained: the canonical watchlist route rendered strategy-workbench titles, focus labels, and workflow copy even though the page still relied on the broader shared trading-signals feed.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a canonical wrapper route can borrow a shared page surface and accidentally leak donor-route titles, hero copy, or workflow promises into a different route family.
- Occurrence basis:
  - `/watchlist/signals` previously showed `策略信号工作台`, `FOCUS: ALL`, and strategy timeline copy even though the canonical route is watchlist-scoped
  - the same route did not disclose that watchlist-specific signal association or filtering is still pending and that the surface currently reuses the broader trading-signals feed
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
  - `web/frontend/src/views/watchlist/Signals.vue`
- Suggested follow-up scope: extend later wrapper-route audits to verify that shared workbench surfaces do not leak donor-route semantics across watchlist, strategy, trade, or other routed domains.

## Main Skill Decisions
- duplicates merged: yes; title, subtitle, focus-label, and timeline-copy leakage were merged into one donor-route semantic truth issue
- priority order applied: routed surface truth > donor-route copy cleanup
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
- shared-impact review items:
  - `watchlist-signals-issue-02`
- fixes applied:
  - `watchlist-signals-issue-02`
- deferred items: none

## Fix Summary
- Parameterized the shared strategy signals surface so routed pages can select `strategy` or `watchlist` semantics without cloning the component.
- Updated the canonical watchlist signals wrapper so it now passes a watchlist-specific surface variant.
- Degraded the watchlist route subtitle and timeline description to explicit pending-integration copy because the current route still reuses the broader trading-signals feed and does not yet prove real watchlist-linked filtering.
- Extended `myweb-audit` with a `v1.27` donor-route semantic truth rule so future audits catch shared-route copy leakage earlier.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/watchlist-batch-02-repair-approval.yaml`
- Approved issue ids:
  - `watchlist-signals-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch:
  - `watchlist-signals-issue-02`
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved watchlist repair remains unimplemented in `watchlist-batch-02`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - real routed verification checked both `/watchlist/signals` and `/strategy/signals` so the watchlist surface truth and the shared-donor preservation path were both covered
- Regression checks completed:
  - `npx vitest run src/views/watchlist/__tests__/Signals.spec.ts src/views/trade/__tests__/Signals.spec.ts` -> passed `3/3`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase2-mainline-matrix.spec.ts --list` -> listed `13` structurally valid tests including the strengthened watchlist-signals route assertion
  - targeted routed-page verification confirmed:
    - actual PM2 `/watchlist/signals` now shows `自选信号雷达`, `FOCUS: WATCHLIST`, and `当前复用全局交易信号流，自选组合联动与范围过滤待接入。`
    - the same watchlist route no longer shows `策略信号工作台` or the old strategy timeline description
    - actual PM2 `/strategy/signals` still shows `策略信号工作台` and the strategy timeline description after the shared parameterization landed
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/watchlist-batch-02-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/watchlist-batch-02-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/watchlist-batch-02-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/watchlist-batch-02-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/watchlist-batch-02-manifest.yaml` -> passed
- GitNexus staged-scope note:
  - `gitnexus_detect_changes({ scope: "staged" })` returned `risk_level: low`, `changed_files: 80`, `changed_count: 258`, and `affected_count: 0`, but the staged set remained mixed with earlier batch files so the result is recorded as observation-only rather than isolated `watchlist-batch-02` scope
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online

## Next Batch Plan
- If the user continues the watchlist, strategy, or other wrapper-route audit, apply the strengthened donor-route semantic truth rule before trusting any shared page surface that crosses route families.
