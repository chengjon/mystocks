# Batch Audit Report: system-batch-13

## Scope
- Module: system
- Pages:
  - `/system/resources`
- Batch rationale: close the routed `/system/resources` pending-count truth gap so the visible resource shell no longer presents `0 / 0 / 0` before any verified resource snapshot exists

## Agent Summary

### route-inventory
- `/system/resources` remains the canonical system resources route at `web/frontend/src/views/system/Resources.vue`.

### functional-audit
- No cross-route product redesign was needed; the defect stayed inside the delayed-first-load route shell for the resource observatory.

### data-state-audit
- One high-severity issue remained:
  - resource-dependent counts and section headers implied a real empty snapshot before the route had verified any system resources payload

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern:
  - first-load stats strips and section counters can present real-looking zero counts before a route has verified its primary snapshot
- Occurrence basis:
  - `/system/resources` loaded with a delayed first `/api/v1/system/resources` response
  - until repair, the visible stats strip and section headers rendered `0 / 0 / 0` and `0 tracked`
  - the same shell therefore looked like a real empty node snapshot instead of a pending route shell
- Shared component or token involved:
  - `web/frontend/src/views/system/Resources.vue`
- Suggested follow-up scope:
  - continue scanning system and observability routes where stats strips and section headers are both derived from the same first-load snapshot

## Main Skill Decisions
- duplicates merged:
  - pending stats-strip counts and pending section-header counters were kept as one route-truth issue because both came from the same first-load resource snapshot boundary
- priority order applied:
  - verified route truth > convenience zero placeholders
- primary owners selected:
  - `web/frontend/src/views/system/Resources.vue`
- shared-impact review items:
  - none beyond the local Phase 4 routed proof extension
- fixes applied:
  - `system-resources-issue-01`
- deferred items: none

## Fix Summary
- Kept resource-dependent stats-strip counts unresolved until the first verified resource snapshot exists.
- Kept resource section headers at `-- tracked` until the same verified snapshot exists.
- Added owner regression coverage for the delayed-first-load route shell.
- Extended the routed Phase 4 Chromium proof for `/system/resources`.
- Reused stable `myweb-audit v2.0` families and updated route references plus artifacts.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-13-repair-approval.yaml`
- Approved issue ids:
  - `system-resources-issue-01`
- Deferred issue ids: none

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - repo default Playwright `chromium` runner succeeded for the targeted system resources proof
- Regression checks completed:
  - `npx vitest run src/views/system/__tests__/Resources.spec.ts -t "keeps stats-strip counts unresolved while the first resource snapshot is still pending"` -> first failed, then passed `1/1`
  - `npx vitest run src/views/system/__tests__/Resources.spec.ts` -> passed `3/3`
  - `npx vitest run src/views/system/__tests__/Resources.spec.ts src/views/system/__tests__/DataSource.spec.ts src/views/system/__tests__/Settings.spec.ts src/views/system/__tests__/API.spec.ts src/views/system/__tests__/Health.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` -> passed `28/28`
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts -g "System-Resources keeps stats-strip counts unresolved while the first resource snapshot is still pending"` -> passed `1/1`
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `41` tests
  - controlled browser proof confirmed the same route stays at `UNKNOWN / N/A / -- / -- / --` until the delayed resource snapshot resolves
- PM2 remained online:
  - `mystocks-backend` at `http://localhost:8020`
  - `mystocks-frontend` at `http://localhost:3020`

## Next Batch Plan
- Continue scanning canonical system and workbench routes that combine top-level stats strips with section-level counters, especially where delayed first-load shells can still fake empty verified state.
