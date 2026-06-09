# Batch Audit Report: data-batch-15

## Scope
- Module: data
- Pages:
  - /data/fund-flow
- Batch rationale: reuse the existing `v1.43 + v1.41 + v1.39` rules so the canonical `/data/fund-flow` route stops treating failed ranking refresh request ids as if they represented the currently visible verified ranking snapshot

## Agent Summary

### route-inventory
- `/data/fund-flow` continues to resolve directly to canonical `web/frontend/src/views/data/FundFlow.vue`.

### functional-audit
- No new routed interaction-path defect required a separate repair wave in this batch.

### data-state-audit
- One high-severity routed request-provenance defect remained: after a successful fund-flow sync, a failed ranking refresh could replace hero `REQ` with the failed retry id even though the visible ranking rows and row count still belonged to the earlier verified snapshot.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: routed hero request metadata can still drift to the latest transport attempt when a page displays a stale but verified ranking snapshot after refresh failure.
- Occurrence basis:
  - `/data/fund-flow` previously preserved the visible `2`-row ranking table after refresh failure
  - the same route still replaced hero `REQ` with the failed ranking refresh request id, creating a provenance mismatch between metadata and visible rows
- Shared component or token involved:
  - none for the product repair
- Suggested follow-up scope: continue applying `v1.41` request-provenance checks to remaining routes that still derive `REQ`, `REQ_ID`, or similar meta directly from `lastRequestId` after refresh-warning fallbacks.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed request-provenance cluster issue
- priority order applied: routed visible-snapshot truth > page-local containment
- primary owners selected:
  - `web/frontend/src/views/data/FundFlow.vue`
- shared-impact review items:
  - none for the product repair
- fixes applied:
  - `data-fund-flow-issue-03`
- deferred items: none

## Fix Summary
- Added a page-local verified-request-id state so hero `REQ` now tracks the request that actually produced the current visible ranking snapshot.
- Kept failed first-load behavior honest by continuing to degrade hero `REQ` to `N/A` before any verified snapshot exists.
- Strengthened the routed component regression with an explicit success-then-refresh-fail request-provenance case.
- Strengthened the Phase 2 matrix with explicit `/data/fund-flow` stale-refresh request-provenance assertions.
- Reused `myweb-audit v1.43`, `v1.41`, and `v1.39` instead of introducing a new skill version.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-15-repair-approval.yaml`
- Approved issue ids:
  - `data-fund-flow-issue-03`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `data-batch-15`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/data/__tests__/FundFlow.spec.ts` -> passed `5/5`
  - `npx vitest run src/views/data/__tests__/FundFlow.spec.ts src/views/data/__tests__/Industry.spec.ts src/views/data/__tests__/Concepts.spec.ts tests/unit/views/data-fund-flow-partial-state.spec.ts tests/unit/views/data-industry-refresh-fallback.spec.ts tests/unit/views/data-concept-refresh-fallback.spec.ts` -> passed `17/17`
  - `npx playwright test tests/e2e/phase2-mainline-matrix.spec.ts --list` -> listed `21` structurally valid tests including the strengthened `/data/fund-flow` refresh-provenance assertions
  - `timeout 180s npm run type-check` -> passed
  - `git diff --check -- web/frontend/src/views/data/FundFlow.vue web/frontend/src/views/data/__tests__/FundFlow.spec.ts web/frontend/tests/e2e/phase2-mainline-matrix.spec.ts docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-15-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-15-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-15-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-15-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/data-fund-flow-refresh-request-provenance-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/data-batch-15-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - targeted system-Chrome browser verification confirmed:
    - failed first-load `/data/fund-flow` renders `ROWS: --`, `REQ: N/A`, and a failure shell without leaking failed request ids
    - a controlled success-then-ranking-refresh-fail path keeps `REQ: req-data-b15-ranking-success`, preserves the visible `2`-row ranking summary, and still shows the partial warning
    - natural PM2 `/data/fund-flow` currently bounces through `/dashboard -> /login` after initial route mount, so natural-route success proof is recorded as environment observation only
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-15-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-15-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-15-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-15-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-15-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` returned `risk_level: low`, `changed_files: 126`, `changed_count: 317`, and `affected_count: 0`

## Next Batch Plan
- Continue the data and adjacent runtime family on any remaining top-level request-metadata surfaces that still derive `REQ`, `REQ_ID`, or similar meta directly from the latest transport attempt instead of the currently visible verified snapshot.
