# Batch Audit Report: trade-batch-04

## Scope
- Module: trade
- Pages:
  - /trade/terminal
- Batch rationale: close the routed lightweight-runtime demo truth gap on the trade terminal and fold that newly observed success-path placeholder pattern back into myweb-audit.

## Agent Summary

### route-inventory
- `/trade/terminal` remains the canonical terminal route at `web/frontend/src/views/TradingDashboard.vue`.
- The route is a repo-truth exception and should not be inferred from the generic `views/trade/*.vue` convention.

### functional-audit
- No new routed interaction-path defect required a repair wave beyond restoring honest lightweight-runtime semantics on the primary terminal surface and risk-report dialog.

### data-state-audit
- One high-severity lightweight-runtime demo truth defect remained: the page accepted successful runtime responses that only proved demo availability and upgraded them into live trading-monitoring semantics.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed page can still become misleading even when every request succeeds if the backend contract only provides availability or demo runtime payloads and the frontend upgrades that to live-session truth.
- Occurrence basis:
  - `/trade/terminal` previously converted a success-path `session_id: null` into `fallback-offline`, kept exact KPI cards and healthy risk labels, and surfaced `系统运行正常，继续监控` even though the backend module explicitly documents itself as a lightweight runtime availability surface
- Shared component or token involved:
  - `web/frontend/src/views/composables/useTradingDashboard.ts`
- Suggested follow-up scope:
  - continue auditing runtime, monitoring, or terminal-style routed pages for successful placeholder payloads that still masquerade as live operations
  - treat documented lightweight availability APIs and demo rows as a first-class audit dimension, not only failed-request fallback paths

## Main Skill Decisions
- duplicates merged: none
- priority order applied: lightweight-runtime demo truth > page-local terminal polish
- primary owners selected:
  - `web/frontend/src/views/composables/useTradingDashboard.ts`
- shared-impact review items: none
- fixes applied:
  - `trade-terminal-issue-01`
- deferred items: none

## Fix Summary
- Stopped normalizing a success-path `session_id: null` into `fallback-offline`.
- Added lightweight-runtime demo detection based on no session plus demo strategies and zeroed runtime summaries.
- Degraded runtime alert copy, KPI cards, session details, risk badges, market-state labeling, and risk-report guidance to explicit pending-runtime semantics.
- Extended both composable regression coverage and routed E2E coverage for the lightweight runtime demo path.
- Extended `myweb-audit` to `v1.30` so future route audits check successful demo availability payloads as rigorously as failure-path placeholders.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-04-repair-approval.yaml`
- Approved issue ids:
  - `trade-terminal-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved trade repair remains unimplemented in `trade-batch-04`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - the actual PM2 backend route naturally reproduced the lightweight-runtime demo path, so the repaired truth surface was verified without additional route fulfillment or transport overrides
- Regression checks completed:
  - `npx vitest run src/views/composables/__tests__/useTradingDashboard.spec.ts` -> passed `2/2`
  - `npx vitest run src/views/composables/__tests__/useTradingDashboard.spec.ts src/views/trade/__tests__/History.spec.ts src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/Signals.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts` -> passed `10/10`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/trade-terminal.spec.ts --list` -> listed `2` structurally valid trade-terminal tests including the strengthened lightweight-runtime demo route assertion
  - targeted routed-page verification confirmed:
    - actual PM2 `/trade/terminal` now shows `当前展示轻量运行时占位数据`
    - the KPI strip now renders `待接入` instead of exact live-trading numbers
    - the session details now show `会话ID 轻量占位` and `运行状态 待接入`
    - the risk panel now renders `风险监控 待接入`
    - the risk-report dialog now shows `当前仅展示轻量运行时占位数据，实盘风控建议待接入。`
    - the old success-path strings `fallback-offline`, `风险监控 正常`, and `系统运行正常，继续监控` are absent
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/trade-batch-04-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/trade-batch-04-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-04-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/trade-batch-04-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/trade-batch-04-manifest.yaml` -> passed
- GitNexus staged-scope note:
  - `gitnexus_detect_changes({ scope: "staged" })` returned `risk_level: low`, `changed_files: 77`, `changed_count: 256`, and `affected_count: 0`, but the staged set remained mixed with earlier batch files so the result is recorded as observation-only rather than isolated `trade-batch-04` scope
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online

## Next Batch Plan
- If the user continues the trade or adjacent runtime audit wave, prioritize routed pages that consume success-path runtime, monitoring, or demo availability endpoints so successful placeholder payloads cannot quietly bypass truth checks that already exist for failed requests.
