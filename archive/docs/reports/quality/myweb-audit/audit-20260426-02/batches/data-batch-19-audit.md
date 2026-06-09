# Batch Audit Report: data-batch-19

## Scope
- Module: data
- Pages:
  - /data/indicator
- Batch rationale: close the canonical `/data/indicator` selected-indicator context leak so a later verified refresh that replaces the registry universe cannot leave the old `selected indicator` workspace visible beside the new verified registry

## Agent Summary

### route-inventory
- `/data/indicator` remains the canonical routed analysis workspace at `web/frontend/src/views/data/Advanced.vue`.

### functional-audit
- No new interaction-path defect required a separate repair wave beyond keeping the route-owned selected-indicator workspace aligned with the current verified registry universe.

### data-state-audit
- One high-severity routed selected-indicator context defect remained: a later verified refresh could replace the indicator registry universe while the `selected indicator` workspace still showed the old previously selected indicator.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: canonical workbench pages can already own a verified selector-local detail workspace but still leave that workspace mounted after the verified entity universe changes, causing the visible detail panel and visible registry or row set to disagree about the current entity truth.
- Occurrence basis:
  - `/data/indicator` previously required `data-batch-18` because a verified refresh could replace the screening results universe while the `selected stock` context survived
  - `/data/indicator` expressed the same selector-truth family again through a local `selected indicator` workspace that survived a verified indicator-registry replacement
- Shared component or token involved:
  - none for the product repair
- Suggested follow-up scope: continue applying `v1.71 + v1.70 + v1.69 + v1.66` to routed workbench and detail pages that render local selector-owned detail workspaces or entity chips above live verified universes.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` canonical selected-indicator context issue
- priority order applied: current verified registry truth > page-local containment > verification hardening
- primary owners selected:
  - `web/frontend/src/composables/market/useDataAnalysis.ts`
- shared-impact review items:
  - none for the product repair
- fixes applied:
  - `data-indicator-issue-06`
- deferred items: none

## Fix Summary
- Added a route-local selected-indicator reconciliation step in `useDataAnalysis` so each refreshed `indicators` registry revalidates `selectedIndicator` against the current verified registry universe.
- Cleared the `selected indicator` workspace when the previously selected indicator no longer exists in the refreshed verified registry.
- Strengthened owner and routed regressions to pin the exact `select MA -> verified refresh replaces registry with RSI` path.
- Reused existing `myweb-audit v1.71` selected-row context truth guidance; no new skill version was needed for this batch.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-19-repair-approval.yaml`
- Approved issue ids:
  - `data-indicator-issue-06`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `data-batch-19`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run tests/unit/views/data-advanced-screening-truth.spec.ts src/views/data/__tests__/Advanced.spec.ts tests/unit/views/data-advanced-cutover.spec.ts tests/unit/views/data-indicator-details.spec.ts` -> passed `10/10`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase2-mainline-matrix.spec.ts --list` -> listed `28` structurally valid tests including the strengthened `/data/indicator` selected-indicator refresh assertion
  - targeted system-Chrome browser verification confirmed:
    - initial verified selection mounted `selected indicator / 移动平均线 / MA`
    - after a verified refresh replaced the current registry, the editor workspace returned to `从指标库选择一个指标`
    - the stale selected-indicator workspace disappeared and `移动平均线` no longer remained in `#data-analysis-panel-editor`
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-19-raw-findings.yaml`
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-19-merged-findings.yaml`
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-19-repair-approval.yaml`
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-19-manifest.yaml`
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-19-manifest.yaml`
  - `git diff --check -- web/frontend/src/composables/market/useDataAnalysis.ts web/frontend/tests/unit/views/data-advanced-screening-truth.spec.ts web/frontend/tests/e2e/phase2-mainline-matrix.spec.ts docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-19-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-19-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-19-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-19-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/data-indicator-selected-indicator-context-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/data-batch-19-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Continue applying `v1.71 + v1.70 + v1.69 + v1.66` to canonical workbench and detail pages that render selector-owned detail workspaces, entity chips, or local context summaries above live verified universes, especially where same-instance refreshes can replace the current selector-owned entity universe.
