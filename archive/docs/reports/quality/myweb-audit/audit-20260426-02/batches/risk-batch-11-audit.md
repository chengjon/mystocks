# Batch Audit Report: risk-batch-11

## Scope
- Module: risk
- Pages:
  - /risk/news
- Batch rationale: reuse existing `v1.43` verified-snapshot provenance rules so the canonical `/risk/news` route no longer lets first-load failures leak request ids, faux announcement/count summary truth, or empty-success copy, and no longer clears verified announcements when a later refresh fails.

## Agent Summary

### route-inventory
- `/risk/news` remains the canonical routed announcement workbench at `web/frontend/src/views/risk/News.vue`.
- The same owner continues to feed the legacy wrapper `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue`, so the current repair stays page-local and consumer-compatible.

### functional-audit
- No new interaction-path defect required a separate repair wave beyond restoring honest stale-refresh behavior on the existing `刷新公告` workflow.

### data-state-audit
- One high-severity routed truth cluster remained: the route trusted the latest `useArtDecoApi` request metadata and null-on-failure arrays instead of preserving a page-local verified announcements snapshot across its announcement slice.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a transport-backed route can correctly render its happy path and still misrepresent first-load failure and refresh-after-success truth if hero request provenance, date/count surfaces, and empty-state copy are bound directly to the latest request attempt instead of the currently visible verified snapshot.
- Occurrence basis:
  - `/risk/news` previously let the failed announcements request overwrite `REQ_ID` and zero-fill sibling count surfaces before any verified snapshot existed
  - the same route previously showed empty-success copy on first-load failure and cleared verified announcements on refresh failure instead of preserving last-known-good routed truth
- Shared component or token involved:
  - none for the approved product repair
- Suggested follow-up scope: continue applying `v1.43 + v1.38` to other canonical routes that expose top-level request meta plus adjacent count surfaces or empty-state copy on the same routed shell.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed news provenance and placeholder-truth issue
- priority order applied: preserve verified request provenance > preserve verified rows on refresh failure > suppress faux zero-count first-load truth > suppress empty-success copy before any verified snapshot exists
- primary owners selected:
  - `web/frontend/src/views/risk/News.vue`
- shared-impact review items:
  - `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue` was reviewed as a direct consumer and did not require a separate repair
- fixes applied:
  - `risk-news-issue-11`
- deferred items: none

## Fix Summary
- Added page-local verified request provenance to the canonical risk-news route.
- Added first-load placeholder gating so hero `TODAY`, content `ANNOUNCEMENTS / LINKED`, and top-strip counts now render `--` until a verified announcements snapshot exists.
- Suppressed empty-success copy before any verified snapshot exists, so first-load failure no longer falls through to `暂无公告数据` or `当前没有可展示的公告记录。`
- Added stale-refresh handling so refresh-after-success failures preserve verified announcements instead of clearing the routed shell to empty arrays.
- Strengthened the routed component regression and the Phase 4 matrix with explicit first-load failure and refresh-after-success assertions.
- Reused existing `myweb-audit v1.43` without a new skill-version bump because the defect exactly matched the current verified-snapshot provenance rule on a transport-backed routed page.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-11-repair-approval.yaml`
- Approved issue ids:
  - `risk-news-issue-11`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `risk-batch-11`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/risk/__tests__/News.spec.ts` -> passed `3/3`
  - `npx vitest run src/views/risk/__tests__/News.spec.ts src/views/risk/__tests__/Alerts.spec.ts src/views/risk/__tests__/Overview.spec.ts src/views/risk/__tests__/StopLoss.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts` -> passed `20/20`
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `22` structurally valid tests including the new `/risk/news` first-load failure and stale-refresh assertions
  - `timeout 180s npm run type-check` -> passed
  - `git diff --check -- web/frontend/src/views/risk/News.vue web/frontend/src/views/risk/__tests__/News.spec.ts web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-11-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-11-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-11-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-11-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/risk-news-refresh-provenance-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/risk-batch-11-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - targeted system-Chrome browser verification confirmed:
    - with browser-context interception on `**/api/announcement/list?page=1&page_size=50**`, resolved first-load failure now renders `REQ_ID: N/A`, `TODAY: --`, `ANNOUNCEMENTS: --`, `LINKED: --`, top-strip `-- / -- / -- / --`, and `获取公告失败，当前暂无已验证公告快照。`
    - the same first-load failure path no longer leaks the failed request id anywhere in the visible route shell
    - a controlled success-then-refresh-fail browser verification confirmed the same route now keeps `REQ_ID: req-live-risk-news-success`, preserves visible announcements, and shows `获取公告失败，当前仍显示上次成功同步的公告快照。`
    - natural PM2 verification confirmed `/risk/news` still reaches the route and currently renders a real request id plus honest live empty-state `0 / 0 / 0 / 0`
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system `google-chrome` Playwright-library verification for the changed browser path
  - natural PM2 browser reuse now reaches `/risk/news` and renders an honest live empty-state with a real request id, but controlled browser-context verification remains the primary proof for the first-load failure and stale-refresh regressions
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-11-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-11-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-11-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-11-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-11-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` returned `risk_level: low`, `changed_files: 102`, `changed_count: 295`, and `affected_count: 0`, but the staged set remains mixed with earlier batches and unrelated files, so the result is recorded as observation-only rather than isolated `risk-batch-11` scope

## Next Batch Plan
- Continue the risk and adjacent route families on any remaining transport/store-backed pages that still let the latest request metadata, faux zero counts, or empty-success copy impersonate verified routed truth.
