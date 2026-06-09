# Batch Audit Report: watchlist-batch-06

## Scope
- Module: watchlist
- Pages:
  - /watchlist/manage
- Batch rationale: close the canonical `/watchlist/manage` selector-scoped row-provenance truth defect so a later watchlist-stock refresh failure cannot leave the previous verified rows visible under a newly selected watchlist label, while codifying the new `myweb-audit v1.66` guidance.

## Agent Summary

### route-inventory
- `/watchlist/manage` remains the canonical routed watchlist-management entry at `web/frontend/src/views/watchlist/Manage.vue`, with the routed surface owner in `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`.

### functional-audit
- One high-severity routed interaction-path defect remained: selector-scoped stock rows and active-tab chrome could drift out of sync after a later refresh failure on the newly requested watchlist.

### data-state-audit
- The route already retained the last verified rows, but it retained them under the wrong selector truth. This batch therefore treated selector-to-row provenance as the primary routed defect instead of first-load envelope truth.

### visual-artdeco-audit
- No batch-dominant visual defect required a repair wave.

### responsive-a11y-audit
- No new desktop-breakpoint defect required a repair wave.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: selector-scoped routes that retain verified rows after a later slice refresh fail can still produce false route truth if the active tab, label, or selector context switches ahead of the failed request.
- Occurrence basis:
  - `/watchlist/manage` previously kept the verified `核心组合` rows visible after a failed `成长跟踪` stock refresh
  - the same route previously switched `.watchlist-tab.active` to `成长跟踪` before that later stock slice verified
- Shared component or token involved:
  - none
- Shared mapper involved:
  - none in the approved repair
- Suggested follow-up scope: continue applying `v1.66 + v1.55 + v1.43` to remaining selector-scoped routed pages where a failed later refresh could leave old rows under a new selector label.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed selector-provenance cluster
- priority order applied: preserve selector-to-row truth > preserve stale-snapshot messaging > preserve routed interaction continuity
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`
- shared-impact review items: none
- fixes applied:
  - `watchlist-manage-issue-06`
- deferred items: none

## Fix Summary
- Added selector-scoped rollback so the route no longer leaves the previous verified stock rows under a newly requested watchlist after that later stock refresh fails.
- Promoted the later selector-refresh failure path into explicit stale-refresh copy `自选列表刷新异常` instead of a generic first-load failure shell.
- Strengthened both the component regression and the Phase 2 route matrix with an explicit `success -> watchlist-stock-refresh-fail` proof.
- Promoted `myweb-audit` to `v1.66` for selector-scoped row-provenance truth.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/watchlist-batch-06-repair-approval.yaml`
- Approved issue ids:
  - `watchlist-manage-issue-06`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `watchlist-batch-06`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/watchlist/__tests__/Manage.spec.ts` -> passed `4/4`
  - `npx vitest run src/views/watchlist/__tests__/Manage.spec.ts src/views/watchlist/__tests__/Signals.spec.ts src/views/watchlist/__tests__/Screener.spec.ts` -> passed `10/10`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase2-mainline-matrix.spec.ts --list` -> listed `26` structurally valid tests including the new `/watchlist/manage` selector-refresh failure assertion
  - `git diff --check -- web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue web/frontend/src/views/watchlist/__tests__/Manage.spec.ts web/frontend/tests/e2e/phase2-mainline-matrix.spec.ts .claude/skills/myweb-audit/SKILL.md .claude/skills/myweb-audit/references/CHANGELOG.md .claude/skills/myweb-audit/references/audit-checklist.md .claude/agents/myweb-audit-data-state-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/findings/watchlist-batch-06-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/watchlist-batch-06-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/watchlist-batch-06-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/watchlist-batch-06-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/watchlist-manage-selector-row-provenance-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/watchlist-batch-06-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - targeted system-Chrome browser verification confirmed:
    - the controlled proof starts from a successful default `核心组合` snapshot before the later selector-refresh failure is triggered
    - a controlled later watchlist-stock refresh failure now leaves `.watchlist-tab.active` on `核心组合`
    - the same route keeps `贵州茅台 / 宁德时代` visible and does not leak `比亚迪`
    - the visible state panel now reads `自选列表刷新异常` together with `当前仍显示上次成功同步的自选组合快照。`
  - `pm2 list` -> confirm `mystocks-backend` and `mystocks-frontend` remained online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/watchlist-batch-06-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/watchlist-batch-06-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/watchlist-batch-06-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/watchlist-batch-06-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/watchlist-batch-06-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict
  - the natural PM2 default success path was not re-run separately in this micro-batch; the controlled success-then-failure browser proof and the component regression cover the unchanged happy-path selector binding

## Next Batch Plan
- Continue the watchlist and adjacent selector-scoped route families on any remaining shells that still let later selector refresh failures rebind old verified rows to a new active tab, filter, or other selector label.
