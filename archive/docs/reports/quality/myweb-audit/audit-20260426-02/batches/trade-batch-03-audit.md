# Batch Audit Report: trade-batch-03

## Scope
- Module: trade
- Pages:
  - /trade/history
- Batch rationale: close the routed stale-refresh truth gap on the trade history workbench and fold the newly observed mock-transport verification handling back into myweb-audit.

## Agent Summary

### route-inventory
- `/trade/history` remains the canonical routed trade-ledger workbench at `web/frontend/src/views/trade/History.vue`.
- The stale-refresh defect is page-local; no shared mapper or wrapper owned the failing data-retention branch.

### functional-audit
- No new routed interaction-path defect required a repair wave beyond restoring honest refresh-failure behavior.

### data-state-audit
- One high-severity stale-refresh truth defect remained: after a successful history load, a failed manual refresh still cleared the retained ledger and switched the page into a first-load-style empty or error state.
- The live verification also exposed a reusable audit-method nuance: on this route, env-level mock transport short-circuits `apiClient` through `mockApiClient`, so browser network interception is not a reliable way to prove or falsify the page's request behavior.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a single-request routed workbench can still collapse refresh failures into first-load failure handling and erase the last-known-good surface even when the route previously loaded correctly.
- Occurrence basis:
  - `/trade/history` previously set `internalHistory.value = []` whenever `exec()` returned `null`, so a manual refresh failure hid the last successful ledger instead of keeping it visible with a stale-data warning
- Shared component or token involved:
  - none; the routed defect was page-local to `web/frontend/src/views/trade/History.vue`
- Suggested follow-up scope:
  - continue auditing other routed workbenches with manual refresh actions for the same v1.15 stale-refresh truth gap
  - when a routed page is short-circuited by `mockApiClient` or equivalent in-process transport, treat normal browser interception as inapplicable and switch to a documented in-page override for controlled live verification

## Main Skill Decisions
- duplicates merged: none
- priority order applied: routed stale-refresh truth > verification-surface hygiene
- primary owners selected:
  - `web/frontend/src/views/trade/History.vue`
- shared-impact review items: none
- fixes applied:
  - `trade-history-issue-01`
- deferred items: none

## Fix Summary
- Removed the failed-refresh branch that wiped `internalHistory`.
- Split refresh-failure status and messaging from first-load failure handling so retained ledger rows now coexist with `刷新异常` and explicit stale-data copy.
- Restricted the hard empty-error panel to first-load or no-data failures only.
- Extended targeted route coverage with both a unit regression and a Phase 3 routed browser scenario for success-then-refresh-fail.
- Extended `myweb-audit` to `v1.28` so future live audits recognize when env-level mock transport bypasses browser interception and switch to a documented in-page override instead of misclassifying the route.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-03-repair-approval.yaml`
- Approved issue ids:
  - `trade-history-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved trade repair remains unimplemented in `trade-batch-03`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - the actual PM2 route was verified as loaded first, then the stale-refresh path was verified on the same routed page via an in-page `apiClient.get` override because the current runtime short-circuits `/trade/history` through `mockApiClient` generic fallback instead of a browser-observable network request
- Regression checks completed:
  - `npx vitest run src/views/trade/__tests__/History.spec.ts` -> passed `1/1`
  - `npx vitest run src/views/trade/__tests__/History.spec.ts src/views/trade/__tests__/Signals.spec.ts src/views/trade/__tests__/Portfolio.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts` -> passed `8/8`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `15` structurally valid tests including the strengthened trade-history route assertion
  - targeted routed-page verification confirmed:
    - actual PM2 `/trade/history` loads successfully, shows a real `REQ_ID`, and currently renders an honest empty-history surface
    - controlled success-then-refresh-fail verification on the same routed page shows `600519` and `已成交`, keeps the ledger rows mounted after the failed refresh, labels the page `刷新异常`, and shows `交易历史接口失败，当前仍展示上次成功同步的交易历史记录。`
    - the hard empty failure panel `交易历史拉取失败，当前无法展示真实记录。` stays absent once retained successful rows exist
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
  - because `/trade/history` currently resolves through env-level mock transport, browser network interception was treated as inapplicable for the controlled stale-refresh proof and was replaced with an in-page module override that was explicitly recorded in the manifest and page report
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/trade-batch-03-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/trade-batch-03-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-03-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/trade-batch-03-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/trade-batch-03-manifest.yaml` -> passed
- GitNexus staged-scope note:
  - `gitnexus_detect_changes({ scope: "staged" })` returned `risk_level: low`, `changed_files: 77`, `changed_count: 256`, and `affected_count: 0`, but the staged set remained mixed with earlier batch files so the result is recorded as observation-only rather than isolated `trade-batch-03` scope
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online

## Next Batch Plan
- If the user continues the trade, strategy, or watchlist audit, prioritize routed pages that still combine manual refresh, route-local retained content, and env-level mock transport so both stale-refresh truth and verification-surface truth stay aligned.
