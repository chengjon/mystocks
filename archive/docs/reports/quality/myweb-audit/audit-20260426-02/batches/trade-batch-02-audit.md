# Batch Audit Report: trade-batch-02

## Scope
- Module: trade
- Pages:
  - /trade/signals
- Batch rationale: close the routed signal-surface truth gap so the current trade signals workspace cannot fabricate row detail, HOLD actions, or execution analytics from a signals-only payload

## Agent Summary

### route-inventory
- `/trade/signals` remains the canonical routed trade signals workspace at `src/views/trade/Signals.vue`.
- The page still reuses `ArtDecoTradingSignals.vue` plus the shared `strategySignalsData.ts` mapper, so the visible defect sat across a route owner plus two shared helpers rather than a single literal constant.

### functional-audit
- No new routed interaction blocker required a repair wave beyond restoring truthful signal-row and analytics behavior.

### data-state-audit
- One high-severity signal-surface truth defect remained: the page consumed current signal rows but still fabricated signal IDs, reasons, confidence, strength, HOLD actions, and execution-history or quality panels that the routed payload never actually returned.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed signals page can borrow credibility from one live list response and silently escalate that into per-row executable detail or execution analytics that are not present in the current contract.
- Occurrence basis:
  - `/trade/signals` previously fabricated local IDs such as `1000`, reasons such as `${strategy} 信号触发`, confidence values `88%` or `76%`, and star-strength surfaces from a signals-only payload
  - the same route rendered `HOLD` rows as `卖出` and fabricated history plus quality analytics from the current list itself
- Shared component or token involved:
  - `web/frontend/src/views/trade/Signals.vue`
  - `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingSignals.vue`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/strategySignalsData.ts`
- Suggested follow-up scope: extend future trade, strategy, and watchlist audits to verify that routed signal pages do not fabricate execution-grade detail from current signal rows unless those fields are truly present.

## Main Skill Decisions
- duplicates merged: yes; row-surface, HOLD-action, and secondary-analytics symptoms were merged into one canonical signal-truth issue
- priority order applied: routed signal truth > secondary analytics polish
- primary owners selected:
  - `web/frontend/src/views/trade/Signals.vue`
- shared-impact review items:
  - `trade-signals-issue-01`
- fixes applied:
  - `trade-signals-issue-01`
- deferred items: none

## Fix Summary
- Extended the shared strategy signal mapper so optional `signal_id`, `reason`, `confidence`, and `strength` fields survive normalization when the live payload provides them.
- Reworked the canonical trade signals page so row detail degrades honestly instead of fabricating local IDs, confidence, reasons, or history.
- Updated the shared signals list component so `HOLD` rows render as `观望` and remain non-executable.
- Replaced fabricated execution-history, quality, and type-accuracy claims with honest pending or unverified surfaces while preserving direct live direction counts.
- Extended `myweb-audit` with a `v1.26` signal-surface truth rule so future audits catch synthetic signal detail and HOLD mislabeling earlier.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-02-repair-approval.yaml`
- Approved issue ids:
  - `trade-signals-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch:
  - `trade-signals-issue-01`
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved trade repair remains unimplemented in `trade-batch-02`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - route-level signal-truth verification used both a real PM2 page load and a controlled `/api/v1/trade/signals` fulfillment so route health and signals-only truth could be checked separately
- Regression checks completed:
  - `node --test src/views/artdeco-pages/strategy-tabs/__node_tests__/strategySignalsData.test.ts` -> passed `3/3`
  - `npx vitest run src/views/trade/__tests__/Signals.spec.ts src/views/trade/__tests__/Portfolio.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts` -> passed `7/7`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `14` structurally valid tests including the strengthened trade-signals route assertion
  - targeted routed-page verification confirmed:
    - actual PM2 `/trade/signals` loads successfully, shows a live `REQ_ID`, keeps pending analytics honest, and does not show `88%` or `76%`
    - controlled signals-only verification shows `策略来源：Momentum Alpha`, renders the `HOLD` row as `观望`, disables its `观察` action button, and keeps `暂无已验证执行历史。`
    - the old fabricated strings `Momentum Alpha 信号触发`, `88%`, and `76%` are absent after repair
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/trade-batch-02-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/trade-batch-02-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-02-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/trade-batch-02-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/trade-batch-02-manifest.yaml` -> passed
- GitNexus staged-scope note:
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded as mixed-staged observation only for this run
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online

## Next Batch Plan
- If the user continues the trade, strategy, or watchlist audit, apply the strengthened signal-surface truth rule to other routed signal pages before trusting any per-row confidence, reason, or execution-history surfaces.
