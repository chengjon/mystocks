# Batch Audit Report: detail-batch-01

## Scope
- Module: detail
- Pages:
  - /detail/graphics/:symbol
- Batch rationale: close the canonical `/detail/graphics/:symbol` primary-snapshot provenance gap so unresolved or failed primary K-line requests cannot leak faux `REQ_ID / POINTS` truth into the visible detail shell, while later failed refreshes preserve the last verified primary sample instead of overwriting hero metadata with failed retry provenance

## Agent Summary

### route-inventory
- `/detail/graphics/:symbol` continues to resolve directly to canonical `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave in this batch.

### data-state-audit
- One high-severity routed primary-snapshot provenance cluster remained: the page treated the latest transport request as if it always represented the currently visible primary K-line sample, even when the latest request was unresolved, had failed before any verified sample existed, or had failed after a successful primary sync was already on screen.

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
- Repeated issue pattern: a canonical detail route can mix one primary snapshot request with secondary enrichment requests and still expose hero `REQ_ID / POINTS` or similar primary-shell meta directly from the latest transport attempt instead of the verified primary snapshot currently visible on screen.
- Occurrence basis:
  - `/detail/graphics/:symbol` previously rendered `POINTS: 0` while the first primary K-line request was still unresolved
  - the same route previously leaked a failed first-load K-line `request_id` before any verified primary sample existed
  - the same route previously replaced the visible hero `REQ_ID` and point-count shell with failed refresh provenance after a later `开始分析` retry failed
- Shared component or token involved:
  - none for the product repair
- Suggested follow-up scope: continue applying `v1.45 + v1.43 + v1.39` checks to remaining canonical detail or mixed-primary/secondary routes that still expose hero request surfaces directly from the latest transport attempt.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed primary-snapshot provenance issue
- priority order applied: primary-snapshot truth > page-local containment > verification hardening
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue`
- shared-impact review items:
  - none for the product repair
- fixes applied:
  - `detail-graphics-issue-01`
- deferred items: none

## Fix Summary
- Added page-local verified-primary-snapshot state so the detail route hero `REQ_ID` now tracks the request that actually produced the visible K-line sample.
- Added unresolved first-load and failed first-load placeholder gating so hero `POINTS` degrades to `--` and `REQ_ID` is suppressed before any verified primary snapshot exists.
- Preserved the last verified request id and visible K-line sample when a later `开始分析` refresh fails after success.
- Strengthened the routed component regression with unresolved first-load, first-load failure, and stale-refresh failure cases.
- Strengthened the Phase 1 matrix with explicit `/detail/graphics/:symbol` primary-snapshot provenance assertions.
- Introduced `myweb-audit v1.45` detail-primary snapshot provenance guidance for canonical detail routes that mix one primary snapshot request with secondary enrichment requests.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/detail-batch-01-repair-approval.yaml`
- Approved issue ids:
  - `detail-graphics-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `detail-batch-01`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/analysis-tabs/__tests__/KLineAnalysis.spec.ts src/views/market/__tests__/Technical.spec.ts` -> passed `6/6`
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed `27` structurally valid tests including the new `/detail/graphics/:symbol` provenance assertions
  - `timeout 180s npm run type-check` -> passed
  - targeted system-Chrome browser verification confirmed:
    - unresolved first-load `/detail/graphics/600519` now renders `POINTS: --` and suppresses `REQ_ID`
    - failed first-load `/detail/graphics/600519` now renders `POINTS: --`, shows `K线数据加载失败，当前暂无已验证K线分析快照。`, and does not leak the failed request id
    - a controlled success-then-fail `开始分析` refresh path now keeps `REQ_ID: req-live-kline-success`, preserves `POINTS: 2`, and shows `K线数据加载失败，当前仍显示上次成功同步的K线分析快照。`
    - natural PM2 `/detail/graphics/600519` currently renders a real request id and live point count `57`
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/detail-batch-01-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/detail-batch-01-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/detail-batch-01-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/detail-batch-01-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/detail-batch-01-manifest.yaml` -> passed
  - `git diff --check -- web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue web/frontend/src/views/artdeco-pages/analysis-tabs/__tests__/KLineAnalysis.spec.ts web/frontend/tests/e2e/phase1-mainline-matrix.spec.ts .claude/skills/myweb-audit/SKILL.md .claude/skills/myweb-audit/references/audit-checklist.md .claude/agents/myweb-audit-data-state-audit.md .claude/skills/myweb-audit/references/CHANGELOG.md docs/reports/quality/myweb-audit/audit-20260426-02/findings/detail-batch-01-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/detail-batch-01-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/detail-batch-01-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/detail-batch-01-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/detail-graphics-primary-snapshot-provenance-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/detail-batch-01-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict
