# Page Audit Report: /risk/management

## Purpose
Primary routed risk-management workbench for reviewing holdings-based risk exposure, concentration, and alert-style surfaces.

## Agent Findings

### route-inventory
- Canonical routed entry remains `web/frontend/src/views/risk/Center.vue`.

### functional-audit
- No new routed interaction defect required a repair wave beyond restoring truthful alert or action semantics on the holdings-derived table.

### data-state-audit
- One medium-severity alert-policy truth defect existed before repair: the page loaded live positions exposure data but labeled those rows as true alerts, stop-loss states, and action recommendations without any live alert-policy inputs.

### visual-artdeco-audit
- No visual-dominant defect required a repair wave in this batch.

### responsive-a11y-audit
- No new desktop-breakpoint defect required a repair wave in this batch.

## Issue Summary
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Consolidated Issues
- `risk-management-issue-02`
  - Repair target: `web/frontend/src/views/artdeco-pages/risk-tabs/riskManagementData.ts`
  - Outcome: fixed in `risk-batch-03`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Verified at: 2026-04-28
- Checked routes:
  - `/risk/management`
- Checked states:
  - default
  - empty
- Checked breakpoints:
  - 1920
  - 1440
  - 1280
- Validation notes:
  - routed mapper regressions now confirm positions-only payloads degrade stop-status and action fields to `未校验` and `待复核` instead of inferred stop-loss or action semantics
  - routed panel regressions now confirm holdings-derived rows render `风险观察列表`, `策略状态`, and `复核状态` plus the pending-policy note instead of the old alert-engine wording
  - targeted browser verification confirmed the live routed page issues `/api/v1/trade/positions`, renders `风险观察列表`, `未校验`, and `待复核`, and the action toast now states that policy inputs are still pending
  - the old table title `风险预警列表` and stop-status labels such as `已触发` or `接近` are absent from the routed surface after repair

## Residual Risks
- [Low] The routed page now separates exposure observations from true alert semantics, but the `高风险 / 中风险 / 低风险` row tiers are still local exposure heuristics rather than backend policy labels.
- [Low] The repo's default `npx playwright test` Chromium runner still cannot execute this path on this machine because the local Playwright chromium bundle is missing.
