# Batch Audit Report: risk-batch-15

## Scope
- Module: risk
- Pages:
  - /risk/stop-loss
- Batch rationale: close the canonical `/risk/stop-loss` implicit selector-truth gap so a later primary-watchlist switch cannot leave the previous verified stop-loss cards, counts, or request provenance visible when the newly derived selector has no verified stock snapshot, while codifying new `myweb-audit v1.69` guidance

## Agent Summary

### route-inventory
- `/risk/stop-loss` remains the canonical routed stop-loss workbench at `web/frontend/src/views/risk/StopLoss.vue`.
- The same owner continues to feed the legacy wrapper `web/frontend/src/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue`, so the current repair stays page-local and consumer-compatible.

### functional-audit
- No new routed click-flow defect required a separate repair wave beyond honest selector-scoped stop-loss snapshot ownership on the canonical route.

### data-state-audit
- One high-severity routed selector-truth defect remained: the route derived its active selector from the live primary-watchlist slice and then treated an older verified stop-loss snapshot as proof for the newly derived selector after that selector's stock slice failed.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed page can correctly retain stale-state copy for one verified selector and still leak wrong route truth if a later selector-discovery slice changes the active entity before the new selector owns any verified rows.
- Occurrence basis:
  - `/risk/stop-loss` promoted the new primary watchlist immediately after `/v1/monitoring/watchlists` resolved
  - the route still used one global verified flag, so `watchlist:101` cards and `req-stoploss-101-success` remained visible after `watchlist:202/stocks` failed
- Shared component or token involved:
  - none for the approved product repair
- Suggested follow-up scope: continue applying `v1.69 + v1.68 + v1.66` checks to routed pages that derive active selectors indirectly from live slices such as primary watchlists, default portfolios, or route-owned implicit entity pickers.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed implicit-selector truth issue
- priority order applied: selector-owned snapshot truth > page-local containment > routed verification hardening
- primary owners selected:
  - `web/frontend/src/views/risk/StopLoss.vue`
- shared-impact review items:
  - `web/frontend/src/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue` was reviewed as a direct consumer and did not require a separate repair
- fixes applied:
  - `risk-stop-loss-issue-15`
- deferred items: none

## Fix Summary
- Added selector-scoped verified snapshot tracking to the canonical stop-loss owner so request provenance, tally cards, and visible stop-loss rows stay keyed to the currently derived primary watchlist.
- Updated first-load failure, pending, and runtime-copy logic to use `hasVerifiedCurrentStopLossSnapshot` instead of one route-global verified flag.
- Added an owner-level regression for the `watchlist:101 -> watchlist:202 -> 202/stocks failure` path.
- Added a Phase 4 routed matrix assertion that guards the same selector-switch failure truth on `/risk/stop-loss`.
- Promoted `myweb-audit` to `v1.69` for implicit selector-discovery truth.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-15-repair-approval.yaml`
- Approved issue ids:
  - `risk-stop-loss-issue-15`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `risk-batch-15`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/risk/__tests__/StopLoss.spec.ts` -> passed `5/5`
  - `npx vitest run src/views/risk/__tests__/StopLoss.spec.ts src/views/risk/__tests__/Center.spec.ts src/views/risk/__tests__/Overview.spec.ts src/views/risk/__tests__/Alerts.spec.ts src/views/risk/__tests__/News.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts tests/unit/views/risk-center-template-retention.spec.ts` -> passed `27/27`
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `32` structurally valid tests including the new `/risk/stop-loss` selector-switch refresh-failure assertion
  - targeted system-Chrome browser verification confirmed:
    - the initial verified selector path renders `REQ_ID: req-live-stoploss-101-success`, `2` cards, and `贵州茅台`
    - after the primary watchlist switches to `watchlist:202` and `watchlist:202/stocks` fails, the route renders `REQ_ID: N/A`, `CRITICAL: --`, `TRIGGERED: --`, `-- / -- / -- / --`, `0` cards, and `watchlist 202 stocks unavailable，当前暂无已验证止损快照。`
    - the same controlled proof confirms old selector-owned content such as `贵州茅台` and `req-live-stoploss-101-success` no longer leaks into the new derived selector shell
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system `google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-15-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-15-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-15-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-15-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-15-manifest.yaml` -> passed
  - `git diff --check -- web/frontend/src/views/risk/StopLoss.vue web/frontend/src/views/risk/__tests__/StopLoss.spec.ts web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts .claude/skills/myweb-audit/SKILL.md .claude/skills/myweb-audit/references/CHANGELOG.md .claude/skills/myweb-audit/references/audit-checklist.md .claude/agents/myweb-audit-data-state-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-15-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-15-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-15-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-15-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/risk-stop-loss-implicit-selector-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/risk-batch-15-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` returned `risk_level: low`, `changed_files: 126`, `changed_count: 317`, and `affected_count: 0`

## Next Batch Plan
- Continue applying `v1.69 + v1.68 + v1.66` to routed pages that derive active selectors indirectly from live slices and can otherwise leak the previous selector's verified rows, counts, or request provenance after the new derived selector fails before first verification.
