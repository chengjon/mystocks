# Batch Audit Report: detail-batch-05

## Scope
- Module: detail
- Pages:
  - /detail/news/:symbol
- Batch rationale: close the canonical `/detail/news/:symbol` auxiliary table-slice truth gap so `monitor-rules` and `triggered-records` failures no longer masquerade as empty-success or unlabeled stale tables while the verified announcement list remains visible, reusing existing `myweb-audit v1.65 + v1.60`.

## Agent Summary

### route-inventory
- `/detail/news/:symbol` remains the canonical routed announcement detail page at `web/frontend/src/views/announcement/AnnouncementMonitor.vue`.

### data-state-audit
- One high-severity routed truth cluster remained: auxiliary table slices on the detail/news route failed independently of the verified announcement list but still rendered as silent empty tables or unlabeled stale rows.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a canonical detail route can keep its primary list verified while sibling auxiliary table slices still misrepresent route truth if first-load failure collapses into empty-success or later refresh failure preserves rows without stale-slice note copy.
- Occurrence basis:
  - `/detail/news/:symbol` silently rendered an empty rules table when `monitor-rules` failed before any verified snapshot existed
  - the same route also kept verified rules or triggered-records rows visible after later refresh failure without explicit stale-slice notes
- Shared component or token involved:
  - none for the approved product repair
- Suggested follow-up scope: continue applying `v1.65 + v1.60` to detail or dashboard routes that mix one verified primary slice with auxiliary live tables or enrichment panels.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed auxiliary-table-slice issue
- priority order applied: preserve verified announcement list truth > make first auxiliary failure explicit > retain later auxiliary rows only with slice-local stale copy
- primary owners selected:
  - `web/frontend/src/views/announcement/composables/useAnnouncementMonitor.ts`
- shared-impact review items:
  - none for the approved product repair
- fixes applied:
  - `detail-news-issue-05`
- deferred items: none

## Fix Summary
- Updated the route-owned announcement monitor composable so `monitor-rules` and `triggered-records` now track verified-snapshot boundaries and slice-local unavailable/stale states.
- Added explicit unavailable and stale note copy to the rules and triggered-records cards.
- Preserved the verified announcement list as the primary slice throughout auxiliary slice failures.
- Added owner regressions plus a Phase 4 routed browser assertion for later auxiliary refresh failure.
- Reused existing `myweb-audit v1.65 + v1.60` instead of introducing a new skill version.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/detail-batch-05-repair-approval.yaml`
- Approved issue ids:
  - `detail-news-issue-05`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `detail-batch-05`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/announcement/__tests__/AnnouncementMonitor.spec.ts src/views/announcement/__tests__/useAnnouncementMonitor.spec.ts src/views/risk/__tests__/News.spec.ts` -> passed `11/11`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `30` tests including the new detail/news auxiliary-slice assertion
  - targeted system-Chrome browser verification confirmed:
    - the first verified snapshot shows `高重要性公告` in `监控规则管理`
    - the first verified snapshot shows `2026 年第一季度经营数据公告` in `触发记录`
    - a controlled later refresh failure now keeps those auxiliary rows visible
    - the same later-failure path now renders `当前仍显示上次成功同步的监控规则快照。`
    - the same later-failure path now renders `当前仍显示上次成功同步的触发记录快照。`
    - the verified announcement list remains visible throughout the same controlled refresh path
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - the controlled browser proof let `/api/health` and `/api/health/ready` fall through to the live backend; no auxiliary-slice assertion depended on those two requests
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` remains observation-only in this run because the staged set is mixed with earlier batches and unrelated files
