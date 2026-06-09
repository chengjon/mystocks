# Batch Audit Report: system-batch-15

## Scope
- Module: system
- Pages:
  - `/system/api`
- Batch rationale: close the routed `/system/api` pending-label truth gap so the visible observability shell no longer presents `N/A / N/A / 3` before any verified system probe snapshot exists

## Agent Summary

### route-inventory
- `/system/api` remains the canonical system monitoring route at `web/frontend/src/views/system/API.vue`.

### functional-audit
- No cross-route product redesign was needed; the defect stayed inside the delayed-first-load route shell for the observability deck.

### data-state-audit
- One high-severity issue remained:
  - probe-dependent summary labels and shell meta implied a real system probe snapshot before the route had verified any probe payload

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern:
  - first-load stats strips and shell-meta labels can present real-looking `N/A` or static counts before a route has verified its primary snapshot
- Occurrence basis:
  - `/system/api` loaded with a delayed first `/api/health` response
  - until repair, the visible stats strip and content-shell meta rendered `服务名称: N/A / 版本: N/A / 中间件项: 3`
  - the same shell therefore looked like a real system probe snapshot instead of a pending route shell
- Shared component or token involved:
  - `web/frontend/src/views/system/API.vue`
- Suggested follow-up scope:
  - continue scanning system observability routes where summary labels and shell meta are both derived from the same first-load probe snapshot

## Main Skill Decisions
- duplicates merged:
  - pending stats-strip labels, content-shell meta, and backend status-card labels were kept as one route-truth issue because all three came from the same first-load system probe boundary
- priority order applied:
  - verified route truth > convenience `N/A` placeholders
- primary owners selected:
  - `web/frontend/src/views/system/API.vue`
- shared-impact review items:
  - none beyond the local Phase 4 routed proof extension
- fixes applied:
  - `system-api-issue-01`
- deferred items: none

## Fix Summary
- Kept probe-dependent summary labels unresolved until the first verified system probe snapshot exists.
- Kept content-shell meta and backend status-card labels aligned with the same unresolved state.
- Added owner regression coverage for the delayed-first-load route shell.
- Extended the routed Phase 4 Chromium proof for `/system/api`.
- Reused stable `myweb-audit v2.0` families and updated route references plus artifacts.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-15-repair-approval.yaml`
- Approved issue ids:
  - `system-api-issue-01`
- Deferred issue ids: none

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - repo default Playwright `chromium` runner succeeded for the targeted system api proof
- Regression checks completed:
  - `npx vitest run src/views/system/__tests__/API.spec.ts -t "keeps stat-strip labels unresolved while the first system probe snapshot is still pending"` -> first failed, then passed `1/1`
  - `npx vitest run src/views/system/__tests__/API.spec.ts src/views/system/__tests__/Health.spec.ts src/views/system/__tests__/Resources.spec.ts src/views/system/__tests__/DataSource.spec.ts src/views/system/__tests__/Settings.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` -> passed `30/30`
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts:2591` -> passed `1/1`
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `43` tests
  - controlled browser proof confirmed the same route stays at `UNKNOWN / -- / -- / --` until the delayed system probe resolves
- PM2 remained online:
  - `mystocks-backend` at `http://localhost:8020`
  - `mystocks-frontend` at `http://localhost:3020`

## Next Batch Plan
- Continue scanning canonical system observability routes where summary labels and shell meta still derive from the same unresolved first-load probe or telemetry snapshot.
