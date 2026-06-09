# Batch Audit Report: detail-batch-03

## Scope
- Module: detail
- Pages:
  - /detail/news/:symbol
- Batch rationale: close the canonical `/detail/news/:symbol` stale-summary truth gap so a failed later announcement stats refresh no longer leaves old sibling counts looking current, and codify that routed failure mode as `myweb-audit v1.53`.

## Agent Summary

### route-inventory
- `/detail/news/:symbol` remains the canonical routed announcement detail workbench at `web/frontend/src/views/announcement/AnnouncementMonitor.vue`.

### functional-audit
- No new interaction-path defect required a separate repair wave beyond restoring honest stats-refresh degradation on the existing detail news shell.

### data-state-audit
- One high-severity routed truth cluster remained: a later failure of the dedicated announcement stats slice silently preserved old sibling counts instead of degrading that stat strip back to explicit placeholder truth.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed page can correctly wire a dedicated live sibling-stats contract on first success and still misrepresent route truth later if a failed stats refresh silently preserves those old sibling counts.
- Occurrence basis:
  - `/detail/news/:symbol` kept previously verified announcement stat counts after the dedicated stats slice failed on a later refresh
  - the same route did not expose explicit slice-local stale-summary UX proving those counts were intentionally retained
- Shared component or token involved:
  - none for the approved product repair
- Suggested follow-up scope: continue applying `v1.53 + v1.43` to routed pages that show dedicated sibling stat cards driven by their own summary slice but may silently keep old counts after later refresh failures.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed stale-summary issue
- priority order applied: clear failed stats slice back to placeholder truth > preserve independent verified announcement rows > keep the repair inside the smallest stable owner
- primary owners selected:
  - `web/frontend/src/views/announcement/composables/useAnnouncementMonitor.ts`
- shared-impact review items:
  - none for the approved product repair
- fixes applied:
  - `detail-news-issue-03`
- deferred items: none

## Fix Summary
- Updated the view-local announcement monitor composable so a failed `/api/announcement/stats` refresh clears `stats.value` instead of silently preserving old sibling counts.
- Preserved the independent verified announcement row slice while degrading the failed stats strip back to `-- / -- / -- / --`.
- Added a composable regression for the exact `success -> stats-refresh-fail` path.
- Strengthened the Phase 4 routed matrix with an explicit `/detail/news/:symbol` stale-stats refresh assertion.
- Introduced `myweb-audit v1.53` so future audits treat silent stale sibling-count retention as a routed data-state truth defect.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/detail-batch-03-repair-approval.yaml`
- Approved issue ids:
  - `detail-news-issue-03`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `detail-batch-03`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts src/views/announcement/__tests__/AnnouncementMonitor.spec.ts` -> passed `3/3`
  - `npx vitest run src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts src/views/announcement/__tests__/AnnouncementMonitor.spec.ts src/views/risk/__tests__/News.spec.ts` -> passed `6/6`
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `29` structurally valid tests including the new `/detail/news/:symbol` stale-stats refresh assertion
  - `timeout 180s npm run type-check` -> passed
  - targeted system-Chrome browser verification confirmed:
    - a controlled success path now renders `2 / 2 / 1 / 0` across the four top stat cards
    - a later failing stats refresh now renders `-- / -- / -- / --`
    - the verified announcement row `2026 年第一季度经营数据公告` remains visible after that stats refresh failure
    - natural PM2 `/detail/news/600519` still reaches the route and currently renders four live count cards `0 / 0 / 0 / 0`
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` remains observation-only in this run because the staged set is mixed with earlier batches and unrelated files

## Next Batch Plan
- Continue the detail and adjacent announcement route family on any remaining pages that request dedicated live stats or summary slices but may still silently preserve sibling counts after later refresh failures.
