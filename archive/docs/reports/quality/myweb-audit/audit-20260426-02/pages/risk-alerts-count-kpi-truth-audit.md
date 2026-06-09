# Page Audit Report: /risk/alerts

## Purpose
Alert governance surface for reviewing rules and recent alerts without overstating count-only KPI movement semantics.

## Agent Findings

### route-inventory
- Routed entrypoint remains `web/frontend/src/views/risk/Alerts.vue`.

### functional-audit
- No new interaction blocker was selected for this page in the current batch.

### data-state-audit
- The routed KPI strip reused shared stat-card defaults that rendered count-only cards as if they carried movement truth.

### visual-artdeco-audit
- No primary visual defect was selected beyond the KPI truth issue itself.

### responsive-a11y-audit
- No new responsive or accessibility blocker was selected for this page in the current batch.

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- [High] The canonical alerts KPI strip rendered exact-decimal counts and fabricated flat-delta chrome such as `+0%`.
- Source roles: data-state-audit
- Why consolidated: one shared stat-card default affected all four count-only routed KPI cards together
- Primary owner: `web/frontend/src/views/risk/Alerts.vue`
- Fix bucket: `fix-now`
- Reproduction or trigger: open `/risk/alerts` and inspect the top KPI strip
- Expected: the routed surface should render plain counts because the page exposes no delta baseline for these cards
- Actual: the strip showed count cards as movement cards by inheriting shared stat-card defaults

## Shared Impact
- Shared component or layout involved: `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue`
- Impact basis: the same shared default pattern was also reproduced on `/risk/news` and `/watchlist/manage`
- Potentially affected related pages:
  - `/risk/news`
  - `/watchlist/manage`
- Follow-up check needed: yes
- Decision timing: pre-repair
- Staged-scope follow-up needed: mixed staged observation only; no isolated staged verdict was used for this page

## Repair Plan
- Fix now: pass plain string counts and explicitly disable `show-change` on the routed alerts KPI strip
- Fix with shared-impact review: defer any shared `ArtDecoStatCard.vue` default change to a later dedicated shared-surface batch because the shared blast radius is high
- Deferred: shared stat-card default change
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/surface-batch-01-repair-approval.yaml`
- Manifest resume cursor after approval: `targeted-live-verification`

## Fixes Applied
- `web/frontend/src/views/risk/Alerts.vue` now passes stringified counts and `:show-change="false"` to the routed KPI strip
- `web/frontend/src/views/risk/__tests__/Alerts.spec.ts` now guards against `.artdeco-stat-change`, `+0%`, and decimal-formatted count values on the canonical route
- `web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts` now asserts the routed alerts KPI strip stays free of faux delta chrome

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse: targeted browser verification reused the existing PM2 frontend via Playwright-library control of system `google-chrome`
- Verified at: 2026-04-29
- Checked routes:
  - `/risk/alerts`
- Checked states:
  - default
  - empty
- Checked breakpoints:
  - 1440
- Validation notes: real backend login plus targeted PM2 verification confirmed KPI values `8 / 8 / 0 / 0`, zero `.artdeco-stat-change` nodes, and no `+0%` or decimal-formatted count text after repair

## Residual Risks
- [Low] The underlying shared `ArtDecoStatCard.vue` defaults still carry the same risky behavior for other routes that have not yet opted out explicitly.
- Reason: this batch intentionally stayed page-local because the shared owner had a HIGH GitNexus blast radius.
- Next action: continue auditing remaining count-only routed KPI surfaces and decide later whether a dedicated shared-surface batch should narrow and safely change the shared stat-card default.
