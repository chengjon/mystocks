# Batch Audit Report: strategy-batch-14

## Scope
- Module: strategy
- Pages:
  - /strategy/backtest
- Batch rationale: extend freshness-provenance auditing so the canonical strategy-backtest route no longer lets report rows backfill missing completion metadata with the local current clock.

## Agent Summary

### route-inventory
- `/strategy/backtest` remains the canonical routed backtest workbench through `web/frontend/src/views/strategy/Backtest.vue` and its downstream owner `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the result-sync mapper substituted `new Date().toLocaleString()` when a valid synced backtest result omitted completion metadata, so `报告中心 / 生成时间` could present a fabricated local current-time freshness stamp.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: freshness-provenance audits must inspect row-level result timestamps such as `generatedAt`, `updatedAt`, or `completed_at` separately from hero freshness metadata, because routed report tables can still fabricate local current-time truth even when the header already passed earlier freshness checks.
- Occurrence basis:
  - `/strategy/backtest` already had a visible report-table freshness surface through `生成时间`
  - the result-sync mapper still treated missing completion metadata as an excuse to synthesize local current time
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
- Suggested follow-up scope: continue applying `v1.48` to routed report tables, result ledgers, and summary surfaces whose visible freshness cells depend on optional backend completion metadata.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: row-level result freshness truth > route-local report-table provenance
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
- shared-impact review items:
  - `web/frontend/src/views/strategy/Backtest.vue` was reviewed as the routed wrapper and did not require a separate repair
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue` inherits the safer row-level placeholder truth without a separate template rewrite
- fixes applied:
  - `strategy-backtest-issue-03`
- deferred items:
  - no strategy-service or backend backtest-schema redesign was approved for this batch

## Fix Summary
- Removed local-current-clock fallback from the route-local report timestamp formatter when synced backtest results omit completion metadata.
- Added owner-level regression coverage so `报告中心 / 生成时间` now requires `--` in that missing-metadata path.
- Added routed Phase 3 matrix coverage so `/strategy/backtest` keeps report-row freshness metadata honest in browser verification.
- Promoted `myweb-audit` to `v1.48` for row-level result freshness provenance on routed report tables and ledgers.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-14-repair-approval.yaml`
- Approved issue ids:
  - `strategy-backtest-issue-03`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved strategy repair remains unimplemented in `strategy-batch-14`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - auth-seeded browser contexts plus browser-context interception with `serviceWorkers: block` were used to isolate the missing-completion-metadata report-row state
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts` -> passed `19/19`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `41` structurally valid tests including the strengthened `/strategy/backtest` report-row assertion
  - targeted routed-page verification confirmed:
    - the controlled missing-completion-metadata route rendered `策略 101 ... --` in the first `报告中心` row
    - the same controlled verification confirmed the page no longer substitutes the local current clock for missing result freshness
    - natural PM2 verification confirmed `/strategy/backtest` still reaches the route and keeps the surrounding workbench shell stable while this repair remains route-local

## Artifact Checklist
- Manifest: `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/strategy-batch-14-manifest.yaml`
- Raw findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-14-raw-findings.yaml`
- Merged findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-14-merged-findings.yaml`
- Approval package: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-14-repair-approval.yaml`
- Page report: `docs/reports/quality/myweb-audit/audit-20260426-02/pages/strategy-backtest-report-timestamp-provenance-audit.md`
- Closeout update: `docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
