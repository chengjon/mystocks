# Batch Audit Report: data-batch-13

## Scope
- Module: data
- Pages:
  - /data/concept
- Batch rationale: close the canonical `/data/concept` request-provenance defect so first-load failures and stale-refresh failures cannot leak failed `REQ` ids or faux empty summary truth into visible route metadata when the rendered concept snapshot was never verified or still belongs to an earlier successful sync, while reusing existing `myweb-audit v1.41` route-truth and `v1.39` verification-method rules

## Agent Summary

### route-inventory
- `/data/concept` continues to resolve directly to canonical `web/frontend/src/views/data/Concepts.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave in this batch.

### data-state-audit
- One high-severity routed request-provenance cluster remained: the page treated the latest request id as if it always represented the currently visible concept snapshot, even when the latest request had failed before any verified board existed or after a successful board was already on screen.

### visual-artdeco-audit
- No batch-dominant visual defect required a repair wave.

### responsive-a11y-audit
- No new desktop-breakpoint defect required a repair wave.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: routed request metadata can leak failure-attempt provenance when a page-level request wrapper exposes the most recent request id rather than the request id that produced the currently visible verified concept snapshot.
- Occurrence basis:
  - `/data/concept` previously rendered a failed first-load concept `request_id` plus `SECTORS: 0 / LEADER: N/A` before any verified concept snapshot existed
  - the same route previously replaced the hero `REQ` with a failed refresh request id even though the visible rows still came from the earlier successful concept sync
- Shared component or token involved:
  - none for the product repair
- Suggested follow-up scope: continue applying `v1.41` request/envelope truth checks to remaining routes that expose top-level `REQ`, `REQ_ID`, or similar meta directly from `lastRequestId`, especially where stale-refresh warnings claim the page is preserving a previous successful snapshot.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed request-provenance cluster issue
- priority order applied: routed visible-snapshot truth > page-local containment
- primary owners selected:
  - `web/frontend/src/views/data/Concepts.vue`
- shared-impact review items:
  - none for the product repair
- fixes applied:
  - `data-concept-issue-02`
- deferred items: none

## Fix Summary
- Added a page-local verified-request-id state so the routed hero `REQ` now tracks the request that actually produced the visible concept snapshot.
- Added a first-load/failure placeholder gate so hero `REQ / SECTORS / LEADER` and content summary metadata degrade to `N/A / --` before any verified concept snapshot exists.
- Strengthened the routed component regression with first-load failure and stale-refresh failure cases.
- Strengthened the Phase 2 matrix with explicit `/data/concept` failure-provenance assertions.
- Reused `myweb-audit v1.41` for route-truth handling and `v1.39` for browser-context interception fallback.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-13-repair-approval.yaml`
- Approved issue ids:
  - `data-concept-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `data-batch-13`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/data/__tests__/Concepts.spec.ts tests/unit/views/data-concept-refresh-fallback.spec.ts src/views/data/__tests__/FundFlow.spec.ts` -> passed `8/8`
  - `npx playwright test tests/e2e/phase2-mainline-matrix.spec.ts --list` -> listed `19` structurally valid tests including the new `/data/concept` request-provenance assertions
  - `timeout 180s npm run type-check` -> passed
  - `git diff --check -- web/frontend/src/views/data/Concepts.vue web/frontend/src/views/data/__tests__/Concepts.spec.ts web/frontend/tests/e2e/phase2-mainline-matrix.spec.ts docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-13-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-13-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-13-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-13-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/data-concept-request-provenance-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/data-batch-13-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - targeted system-Chrome browser verification confirmed:
    - with browser-context interception and `serviceWorkers: block`, failed first-load `/data/concept` now renders `REQ: N/A`, `SECTORS: --`, `LEADER: --`, `POSITIVE: --`, `NEGATIVE: --`, and top stat values `-- / -- / -- / --`
    - the same first-load failure route no longer leaks the failed request id anywhere in the visible page shell
    - a controlled success-then-fail refresh path now keeps `REQ: req-data-b13-success`, preserves the visible `机器人` and `卫星互联网` rows, and shows the stale-refresh warning without leaking the failed retry id
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-13-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/data-batch-13-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/data-batch-13-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-13-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/data-batch-13-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Continue the data and adjacent runtime family on any remaining top-level request-metadata surfaces that still derive `REQ` directly from the latest transport attempt instead of the currently visible verified snapshot.
