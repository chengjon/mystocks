# Page Audit Report: /data/indicator

## Purpose
Residual truthfulness cleanup for the routed indicator summary strip after the detail-workspace repair in `data-batch-01`.

## Agent Findings

### route-inventory
- Canonical routed entry remains `web/frontend/src/views/data/Advanced.vue`.
- Compatibility wrapper remains thin: `web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue`.

### functional-audit
- No new interaction-path defect was selected in this residual batch.

### data-state-audit
- The routed summary strip still claimed `自定义指标` despite the current page exposing indicator browsing, screening, and detail inspection only.
- The underlying stats contract still hardcoded `customIndicators: 0`, making the original KPI a permanently-zero capability claim rather than a useful routed metric.

## Issue Summary
- Blocking: 0
- High: 0
- Medium: 0
- Low: 1

## Consolidated Issues
- [Low] Indicator summary stats implied unsupported custom-indicator authoring capability.
- Source roles: data-state-audit
- Why consolidated: the misleading stat label and permanently-zero capability claim belonged to one page-local truthfulness defect in the routed summary strip.
- Primary owner: `web/frontend/src/views/data/Advanced.vue`
- Fix bucket: `fix-now`
- Reproduction or trigger:
  - inspect the summary stat labels in `Advanced.vue`
  - compare them with the currently exposed routed tabs and actions
- Expected: summary KPIs should report real available routed capability or visible state
- Actual: the page surfaced `自定义指标: 0` without any routed create/edit custom-indicator workflow

## Repair Plan
- Fix now:
  - rename the summary stat to `当前分类指标`
  - bind the value to the visible indicator count for the current routed category
- Deferred: none
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-02-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/data/Advanced.vue`
  - replaced the unsupported `自定义指标` KPI with `当前分类指标`
  - bound the routed summary strip to `filteredIndicators.length`
- `web/frontend/tests/unit/views/data-indicator-details.spec.ts`
  - added a regression assertion that the routed page no longer claims custom-indicator authoring capability

## Verification
- Verification policy: code-review-only
- Browser project or runtime reuse: existing PM2 frontend/backend remained online; this residual batch did not require a new page-specific browser path because the defect was a routed stat-label truth mismatch
- Verified at: 2026-04-27
- Checked routes:
  - `/data/indicator`
- Checked states:
  - default
- Checked breakpoints:
  - 1920
  - 1440
  - 1280
- Validation notes:
  - `npx vitest run tests/unit/views/data-indicator-details.spec.ts tests/unit/views/data-advanced-cutover.spec.ts` passed `3/3`
  - `timeout 180s npm run type-check` passed
  - `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online

## Residual Risks
- [Low] The routed page still does not provide real custom-indicator authoring; if that workflow is later introduced, the stats contract and audit expectations should be revisited together.
