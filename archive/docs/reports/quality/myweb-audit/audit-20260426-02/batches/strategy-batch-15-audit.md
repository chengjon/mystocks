# Batch Audit Report: strategy-batch-15

## Scope
- Module: strategy
- Pages:
  - /strategy/backtest
- Batch rationale: extend freshness-provenance auditing so the canonical strategy-backtest route no longer lets rejected manual run actions stamp hero freshness metadata with the local current clock before any verified strategy context exists.

## Agent Summary

### route-inventory
- `/strategy/backtest` remains the canonical routed backtest workbench through `web/frontend/src/views/strategy/Backtest.vue` and its downstream owner `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the rejected-run guard inside `runBacktest()` advanced the hero freshness surface with `new Date().toLocaleString()` whenever no verified strategy context existed, so a warning-only local interaction could masquerade as fresh routed sync truth.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: freshness-provenance audits must inspect rejected or no-op manual actions separately from first-load shell rendering and refresh-failure paths, because local warning flows can still mutate hero freshness metadata without producing any new verified routed snapshot.
- Occurrence basis:
  - `/strategy/backtest` already had a visible hero freshness surface through `最后更新 / UPDATED`
  - the rejected-run guard still treated missing strategy context as an excuse to stamp local current time
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
- Suggested follow-up scope: continue applying `v1.54` to routed workbenches, action hubs, and detail pages whose manual actions can be triggered before a verified route context exists.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: action-triggered freshness truth > route-local hero provenance
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
- shared-impact review items:
  - `web/frontend/src/views/strategy/Backtest.vue` was reviewed as the routed wrapper and did not require a separate repair
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue` inherits the safer freshness truth without a separate template rewrite
- fixes applied:
  - `strategy-backtest-issue-04`
- deferred items:
  - no strategy-service or backend backtest-schema redesign was approved for this batch

## Fix Summary
- Removed the local-current-clock fallback from the route-local rejected-run guard when no verified strategy context exists.
- Added owner-level regression coverage so clicking `启动回测` after a failed or unresolved first load now requires `UPDATED: --`.
- Added routed Phase 3 matrix coverage so `/strategy/backtest` keeps hero freshness metadata honest in browser verification after the same rejected action path.
- Promoted `myweb-audit` to `v1.54` for action-triggered freshness truth on unresolved-context manual actions.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-15-repair-approval.yaml`
- Approved issue ids:
  - `strategy-backtest-issue-04`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved strategy repair remains unimplemented in `strategy-batch-15`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - auth-seeded browser contexts plus browser-context interception with `serviceWorkers: block` were used to isolate the `first-load fail -> click run` freshness path
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts` -> passed `20/20`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `41` structurally valid tests including the strengthened `/strategy/backtest` rejected-action assertion
  - targeted routed-page verification confirmed:
    - the controlled authenticated `first-load fail -> click run` route kept `最后更新 / UPDATED` at `--`
    - the same controlled verification confirmed the warning banner `未绑定有效策略ID，无法启动真实回测。` appears without mutating hero freshness
    - natural PM2 verification confirmed `/strategy/backtest` still reaches the route and keeps the surrounding shell stable while this guard remains route-local

## Artifact Checklist
- Manifest: `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/strategy-batch-15-manifest.yaml`
- Raw findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-15-raw-findings.yaml`
- Merged findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-15-merged-findings.yaml`
- Approval package: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-15-repair-approval.yaml`
- Page report: `docs/reports/quality/myweb-audit/audit-20260426-02/pages/strategy-backtest-action-triggered-freshness-truth-audit.md`
- Closeout update: `docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
