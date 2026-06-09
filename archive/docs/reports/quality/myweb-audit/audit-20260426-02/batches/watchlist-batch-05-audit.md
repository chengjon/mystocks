# Batch Audit Report: watchlist-batch-05

## Scope
- Module: watchlist
- Pages:
  - /watchlist/manage
- Batch rationale: close the canonical `/watchlist/manage` first-load failure and slice-local summary truth defects so resolved `success:false` watchlist payloads cannot be swallowed into fake empty-success rendering and verified watchlist counts cannot promote unresolved stock-summary siblings into faux zero truth, while codifying the new `myweb-audit v1.51` guidance.

## Agent Summary

### route-inventory
- `/watchlist/manage` remains the canonical routed watchlist-management entry at `web/frontend/src/views/watchlist/Manage.vue`, with the routed surface owner in `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave in this batch.

### data-state-audit
- One high-severity routed truth cluster remained: the route conflated first-load failure truth, local completion truth, and slice-local summary provenance, so it could either collapse into fake empty-success rendering or emit faux zero stock-summary counts before the stock slice was verified.

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
- Repeated issue pattern: store-backed routed pages can stay browser-red even when unit mocks look green if shared collection extractors erase resolved `success:false` truth or if route-local completion flags do not survive thrown first-load failures.
- Occurrence basis:
  - `/watchlist/manage` previously treated a resolved `success:false` watchlist payload as a fake empty-success shell
  - the same route previously rendered `2 / 0 / 0 / 0` or natural `18 / 0 / 0 / 0` while the stock-detail slice was still unresolved under a visible loading panel
- Shared component or token involved:
  - none for the visible summary rendering repair
- Shared mapper involved:
  - `web/frontend/src/views/artdeco-pages/stock-management-tabs/stockManagementRouteData.ts`
- Suggested follow-up scope: continue applying `v1.51 + v1.42 + v1.41` to remaining store-backed routed pages that combine shared extractors, local completion flags, and multi-slice KPI strips.

## Main Skill Decisions
- duplicates merged: `2` raw findings into `1` routed summary-truth cluster
- priority order applied: preserve failure truth > preserve visible error shell > preserve per-slice summary provenance
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`
- shared-impact review items:
  - `web/frontend/src/views/artdeco-pages/stock-management-tabs/stockManagementRouteData.ts`
- fixes applied:
  - `watchlist-manage-issue-05`
- deferred items: none

## Fix Summary
- Tightened the shared watchlist extractors so resolved `success:false` envelopes throw instead of collapsing into empty watchlist or stock arrays.
- Updated the route-local refresh lifecycle so first-load failures still advance the canonical route into a visible error shell.
- Split the top summary strip into watchlist-backed versus stock-backed truth, allowing verified watchlist counts to render while unresolved stock-summary siblings remain on `--`.
- Strengthened both the component regression and the Phase 2 route matrix with explicit first-load failure and hanging-stock-slice proofs.
- Promoted `myweb-audit` to `v1.51` for slice-local summary truth and first-load completion truth.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/watchlist-batch-05-repair-approval.yaml`
- Approved issue ids:
  - `watchlist-manage-issue-05`
- Deferred issue ids: none
- Shared-impact items approved for current batch:
  - `web/frontend/src/views/artdeco-pages/stock-management-tabs/stockManagementRouteData.ts`
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `watchlist-batch-05`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/watchlist/__tests__/Manage.spec.ts src/views/watchlist/__tests__/Signals.spec.ts src/views/watchlist/__tests__/Screener.spec.ts` -> passed `9/9`
  - `node --test src/views/artdeco-pages/stock-management-tabs/__node_tests__/stockManagementRouteData.test.ts` -> passed `8/8`
  - `npx playwright test tests/e2e/phase2-mainline-matrix.spec.ts --list` -> listed `24` structurally valid tests including the new `/watchlist/manage` first-load failure and hanging-stock-slice assertions
  - `timeout 180s npm run type-check` -> passed
  - `git diff --check -- web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue web/frontend/src/views/artdeco-pages/stock-management-tabs/stockManagementRouteData.ts web/frontend/src/views/watchlist/__tests__/Manage.spec.ts web/frontend/src/views/artdeco-pages/stock-management-tabs/__node_tests__/stockManagementRouteData.test.ts web/frontend/tests/e2e/phase2-mainline-matrix.spec.ts .claude/skills/myweb-audit/SKILL.md .claude/skills/myweb-audit/references/CHANGELOG.md .claude/skills/myweb-audit/references/audit-checklist.md .claude/agents/myweb-audit-data-state-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/findings/watchlist-batch-05-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/watchlist-batch-05-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/watchlist-batch-05-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/watchlist-batch-05-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/watchlist-manage-slice-summary-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/watchlist-batch-05-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - targeted system-Chrome browser verification confirmed:
    - a controlled first-load `success:false` watchlist payload now renders top-strip `-- / -- / -- / --` together with `自选列表加载失败`
    - the same first-load failure route no longer falls through to `暂无自选组合`
    - a controlled hanging stock-slice path now renders `18 / -- / -- / --` with the visible loading panel, proving verified watchlist counts no longer promote unresolved stock-summary siblings into faux zero truth
    - the natural PM2 success path still reaches `/watchlist/manage` and currently renders live summary counts `18 / 0 / 0 / 0` once the stock slice verifies
  - `pm2 list` -> confirmed `mystocks-backend` and `mystocks-frontend` remained online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/watchlist-batch-05-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/watchlist-batch-05-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/watchlist-batch-05-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/watchlist-batch-05-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/watchlist-batch-05-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict
  - latest staged observation returned `risk_level: low`, `changed_files: 126`, `changed_count: 317`, and `affected_count: 0`

## Next Batch Plan
- Continue the watchlist and adjacent store-backed route families on any remaining shells that still let resolved failure envelopes disappear inside shared extractors or let one verified slice promote unresolved sibling summary cards into faux zero truth.
