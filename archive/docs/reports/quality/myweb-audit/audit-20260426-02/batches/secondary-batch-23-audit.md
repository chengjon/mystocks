# Batch Audit Report: secondary-batch-23

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) Phase4Dashboard.vue`
- Batch rationale: continue the secondary inventory repair phase by collapsing the top-level legacy phase-4 dashboard into a thin wrapper because a semantically matching canonical dashboard owner already exists

## Agent Summary

### route-inventory
- `Phase4Dashboard.vue` remained in the high-priority shortlist because it still combined local stats-strip, selector tabs, and shared-composable chart shell semantics.
- The current project already exposes a semantically matching canonical dashboard owner at `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`.

### data-state-audit
- `Phase4Dashboard.vue` still rendered local market-stats cards, market-overview tabs, watchlist rows, and risk-alert shell truth as if they were an active dashboard surface.
- The local `usePhase4Dashboard()` composable and chart wiring made this page another forked dashboard truth source instead of a simple alias.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: canonical owner delegation > no forked dashboard shell > no new snapshot layer
- primary owners selected:
  - `web/frontend/src/views/Phase4Dashboard.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-23`
- deferred items: none

## Fix Summary
- Replaced `Phase4Dashboard.vue` with a thin wrapper over the canonical dashboard owner.
- Removed the local pseudo-live dashboard shell instead of trying to repair its cards, tabs, or charts in place.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted legacy secondary page
- Regression checks completed:
  - `cd web/frontend && npx vitest run src/views/__tests__/Phase4Dashboard.spec.ts src/views/__tests__/Dashboard.spec.ts src/views/__tests__/EnhancedDashboard.spec.ts` -> passed (`3/3`)
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed (`275` view files, `40` routed, `235` unrouted, `H=40 / M=100 / L=95`)
  - `npm run test:myweb-audit:skill` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --all --run-id audit-20260426-02 --batch-id secondary-batch-23` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-23-manifest.yaml` -> passed
- Runtime and repo gates:
  - `cd web/frontend && timeout 180s npm run type-check` -> failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - `pm2 list` -> passed; `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `git diff --check -- web/frontend/src/views/Phase4Dashboard.vue web/frontend/src/views/__tests__/Phase4Dashboard.spec.ts .claude/skills/myweb-audit/references/secondary-view-inventory.md .claude/skills/myweb-audit/references/secondary-view-inventory.json docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-23-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/secondary-batch-23-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/secondary-batch-23-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/phase4-dashboard-legacy-canonical-wrapper-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-23-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/manifests/secondary-batch-23-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - `gitnexus_detect_changes({ scope: "staged" })` -> mixed observation only (`risk_level: medium`, `changed_files: 120`, `changed_count: 316`, `affected_count: 3`) because the staged index is already contaminated by unrelated files in this worktree
- No Playwright batch was added because this repair targets an unrouted legacy page with no canonical routed proof surface in the current router graph.
