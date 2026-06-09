# Batch Audit Report: strategy-batch-03

## Scope
- Module: strategy
- Pages:
  - /strategy/pos
  - /trade/positions
- Batch rationale: positions workbench truth closure across the strategy wrapper route, the canonical trade route, and the remaining embedded ArtDeco consumer

## Agent Summary

### route-inventory
- `/strategy/pos` is a compatibility wrapper over `src/views/trade/Center.vue`.
- `/trade/positions` is the canonical routed positions workbench.
- The remaining family divergence was `ArtDecoTradingCenter#trade-positions`, which still used `ArtDecoPositionMonitor.vue` as a placeholder fork before repair.

### functional-audit
- Routed position pages were already healthy.
- The actual defect was the embedded consumer still presenting a non-functional placeholder instead of the canonical workbench.

### data-state-audit
- `Center.vue` already owned the true position rows, loading, empty, and retry contract.
- The embedded consumer bypassed that contract entirely before repair.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Pattern Findings
- Repeated issue pattern: the routed migration to domain-level canonical pages completed for positions, but one ArtDeco embedded consumer was still stranded on a placeholder-only parallel truth source.
- Occurrence basis:
  - `/strategy/pos` already reused `Center.vue`
  - `/trade/positions` already routed directly to `Center.vue`
  - `ArtDecoTradingCenter#trade-positions` still used `ArtDecoPositionMonitor.vue` placeholder copy
- Shared component or token involved:
  - `web/frontend/src/views/trade/Center.vue`
  - `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPositionMonitor.vue`
  - `web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue`
- Suggested follow-up scope: when later batches review other legacy ArtDeco hosts, keep applying the same wrapper-first convergence rule instead of leaving placeholder forks behind.

## Main Skill Decisions
- duplicates merged: yes; route-truth drift and data-state drift were merged into the same embedded convergence issue
- priority order applied: canonical truth convergence > legacy placeholder retention
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPositionMonitor.vue`
- shared-impact review items:
  - `strategy-pos-issue-01`
- fixes applied:
  - `strategy-pos-issue-01`
- deferred items: none

## Fix Summary
- Replaced `ArtDecoPositionMonitor.vue` placeholder content with a thin wrapper over `src/views/trade/Center.vue`.
- Activated `Center.vue` embedded mode via `:positions="[]"` so the legacy host keeps the embedded shell without turning back into a routed-style duplicate.
- Added regression coverage to keep the embedded wrapper on the canonical page and to assert the old placeholder copy is gone.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-03-repair-approval.yaml`
- Approved issue ids:
  - `strategy-pos-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch:
  - `strategy-pos-issue-01`
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved strategy repair remains unimplemented in `strategy-batch-03`.
- The embedded ArtDeco consumer is now source-locked to the canonical page, but it still lacks a dedicated routed browser path for live panel assertions.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted live browser verification reused the PM2 frontend via `PLAYWRIGHT_EXTERNAL_FRONTEND=1`
- Regression checks completed:
  - `timeout 180s npm run type-check` -> passed
  - `npx vitest run tests/unit/views/trade-wrapper-retention.spec.ts` -> passed `5/5`
  - `env PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://127.0.0.1:3020 npx playwright test --config playwright.config.js --project=chromium tests/e2e/phase3-mainline-matrix.spec.ts --grep "Strategy-Pos|Trade-Positions"` -> passed `2/2`
  - `pm2 list` -> `mystocks-backend` and `mystocks-frontend` online
- Shared patterns verified:
  - `/strategy/pos` and `/trade/positions` still render the canonical position ledger
  - the embedded position monitor can no longer regress to a placeholder-only fork without failing `trade-wrapper-retention.spec.ts`
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged" })` returned `risk_level: low`, `changed_files: 64`, `changed_count: 204`, and `affected_count: 0`, but the staged set remained mixed with earlier batch artifacts
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-03-merged-findings.yaml` passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-03-repair-approval.yaml` passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/strategy-batch-03-manifest.yaml` passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/strategy-batch-03-manifest.yaml` passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - `vue-tsc --noEmit` passed under the explicit `timeout 180s npm run type-check` run

## Next Batch Plan
- If the user continues the routed-family audit after this closure, move into the next requested route family rather than reopening the now-converged positions workbench family.
