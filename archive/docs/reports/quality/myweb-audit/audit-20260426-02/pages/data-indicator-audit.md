# Page Audit Report: /data/indicator

## Purpose
Primary routed indicator-analysis workbench for indicator discovery, stock screening, and indicator detail inspection.

## Agent Findings

### route-inventory
- Canonical routed entry: `web/frontend/src/views/data/Advanced.vue`
- Compatibility wrapper remains thin: `web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue`

### functional-audit
- Live route-entry verification under the PM2 frontend confirmed the page loads as the canonical data-analysis route.
- The routed defect was the indicator-card interaction still dropping users into a pseudo-editor placeholder instead of a truthful detail workflow.

### data-state-audit
- The routed page already owned the indicator registry and stock-universe fetch path through `useDataAnalysis()`.
- Live browser verification after the first repair pass surfaced one real data-shape gap: registry parameter objects rendered as `[object Object]` until a second red-green fix normalized them.

## Issue Summary
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Consolidated Issues
- [Medium] Routed indicator selection still exposed pseudo-editor semantics and generic object stringification instead of a truthful detail workspace.
- Source roles: functional-audit
- Why consolidated: the misleading tab label, placeholder copy, and raw-object parameter summary were one page-local detail-surface defect centered on `Advanced.vue`.
- Primary owner: `web/frontend/src/views/data/Advanced.vue`
- Fix bucket: `fix-now`
- Reproduction or trigger:
  - open `/data/indicator`
  - wait for indicator cards
  - click the first indicator card
- Expected: indicator selection opens a real detail view with readable registry parameter labels
- Actual: the routed page previously switched to `指标编辑器` placeholder copy and could degrade real parameter objects to `[object Object]`

## Repair Plan
- Fix now:
  - rename the user-facing `editor` surface to `指标详情` while keeping the existing tab key and panel id stable
  - replace the upgrade placeholder with a real detail workspace and empty-state prompt
  - format registry parameter objects as readable `name(default)` labels
- Deferred: none
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-01-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/data/Advanced.vue`
  - updated the routed page subtitle and tab label from pseudo-editor language to truthful detail language
  - replaced the upgrade placeholder block with a real indicator detail workspace and empty-state prompt
  - added registry-aware parameter formatting for object-shaped parameter definitions
- `web/frontend/tests/unit/views/data-indicator-details.spec.ts`
  - added a regression test that locks the routed detail panel onto readable parameter labels and forbids placeholder copy
- `web/frontend/tests/e2e/phase2-mainline-matrix.spec.ts`
  - strengthened the indicator-card browser path assertion so the panel must contain `指标详情` and must not regress to `公式编辑器升级中`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend/backend were reused
  - targeted browser verification used Playwright-library control of system `google-chrome` because the default Playwright chromium bundle is unavailable on this machine
- Verified at: 2026-04-27
- Checked routes:
  - `/data/indicator`
- Checked states:
  - default
  - selected-indicator-detail
- Checked breakpoints:
  - 1920
  - 1440
  - 1280
- Validation notes:
  - `npx vitest run tests/unit/views/data-indicator-details.spec.ts tests/unit/views/data-advanced-cutover.spec.ts tests/unit/config/data-route-canonical-paths.spec.ts tests/unit/config/domain-body-migration-ownership.spec.ts` passed `13/13`
  - `timeout 180s npm run type-check` passed
  - system-Chrome browser verification after real login reached `/data/indicator`, rendered `指标详情`, removed `公式编辑器升级中`, and rendered `timeperiod(20)` for the selected indicator
  - the default `npx playwright test` Phase 2 matrix run was blocked by a missing local Playwright chromium executable, so the batch recorded that runner failure as an environment fallback rather than a page regression

## Residual Risks
- [Low] The routed detail workflow is browser-verified, but the standard Playwright test runner still needs local browser installation on this machine before the strengthened Phase 2 spec can be executed here.
- [Low] The page still surfaces `自定义指标` as a numeric stat card even though this batch only converted the active detail flow, not the broader indicator-product framing.
