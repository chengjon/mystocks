# Batch Audit Report: data-batch-06

## Scope
- Module: data
- Pages:
  - /data/indicator
- Batch rationale: close the routed indicator workflow-truth gap and fold the idle-vs-executed result-state pattern back into the audit skill

## Agent Summary

### route-inventory
- `/data/indicator` continues to resolve directly to canonical `web/frontend/src/views/data/Advanced.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave in this batch.

### data-state-audit
- One medium-severity workflow-truth defect remained: the page treated hydrated stock-pool data as if screening had already been executed, so `not yet run` and `executed` states were collapsed.

### visual-artdeco-audit
- No batch-dominant visual defect required a repair wave.

### responsive-a11y-audit
- No new desktop-breakpoint defect required a repair wave.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Pattern Findings
- Repeated issue pattern: result-producing routed workbenches need explicit workflow-state separation between `未执行`, `已执行无结果`, and `已执行有结果`.
- Occurrence basis:
  - `/data/indicator` previously auto-populated screening output during hydration and mislabeled that state as `筛选已就绪`
- Shared component or token involved:
  - none; the repair stayed inside `Advanced.vue` plus its local data-analysis composable and mapper
- Suggested follow-up scope: extend future routed-page audits to explicitly probe pre-execution idle states, not just success, empty, and error states.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: workflow truth > generic screenful-of-data success
- primary owners selected:
  - `web/frontend/src/composables/market/useDataAnalysis.ts`
- shared-impact review items: none
- fixes applied:
  - `data-indicator-issue-02`
- deferred items: none

## Fix Summary
- Added explicit `hasExecutedScreening` state to the local data-analysis workflow.
- Prevented hydration from auto-presenting stock-pool data as executed screening results.
- Added an idle result state for the `筛选结果` tab before the user runs screening.
- Strengthened both unit-level and browser-matrix regression coverage for idle-vs-executed workflow truth.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-06-repair-approval.yaml`
- Approved issue ids:
  - `data-indicator-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `data-batch-06`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run tests/unit/views/data-advanced-screening-truth.spec.ts tests/unit/views/data-industry-refresh-fallback.spec.ts tests/unit/views/data-concept-refresh-fallback.spec.ts tests/unit/views/data-fund-flow-partial-state.spec.ts tests/unit/views/data-indicator-details.spec.ts tests/unit/views/data-advanced-cutover.spec.ts tests/unit/config/data-route-canonical-paths.spec.ts tests/unit/config/domain-body-migration-ownership.spec.ts` -> passed `17/17`
  - `node --test src/composables/market/__node_tests__/dataAnalysisData.test.ts` -> passed `4/4`
  - `timeout 180s npm run type-check` -> passed
  - `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
  - targeted system-Chrome browser verification confirmed `/data/indicator` stays idle before screening, shows `尚未执行筛选` in the results tab before execution, and only transitions to `筛选已就绪` after `执行筛选`
- Environment fallback recorded:
  - the default `npx playwright test` runner still cannot execute Chromium on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded as mixed-staged observation only for this run
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-06-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-06-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-06-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-06-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus evidence for this batch remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- If the user continues the data-domain audit, apply the strengthened workflow-truth rule to the next routed workbench where hydrated default data may still be mistaken for executed user output.
