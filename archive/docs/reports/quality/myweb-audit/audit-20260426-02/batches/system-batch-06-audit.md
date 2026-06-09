# Batch Audit Report: system-batch-06

## Scope
- Module: system
- Pages:
  - `/system/config`
- Batch rationale: close the routed system-config source-tab contract-truth gap so the default tab uses the live system data-source config contract and honest tab-local provenance instead of embedded sample inventory

## Agent Summary

### route-inventory
- `/system/config` continues to resolve directly to the canonical `web/frontend/src/views/system/Settings.vue` entry.

### functional-audit
- No new action-flow defect required a separate repair wave in this batch; the dominant routed issue was contract and state truth on the default `数据源` tab.

### data-state-audit
- One medium-severity issue cluster remained:
  - the default source tab still rendered sample KPI cards, sample source rows, and inherited sibling-tab `DATA` provenance instead of the live `/api/v1/data-sources/config/` contract

### visual-artdeco-audit
- No separate ArtDeco-only repair wave was required after the route-local source-tab contract fix landed.

### responsive-a11y-audit
- No new desktop-breakpoint or a11y defect required a repair wave in this batch.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Pattern Findings
- Repeated issue pattern:
  - multi-tab routed pages can leave one default tab on sample KPI cards and sample inventory rows even after a real route-level contract exists for that slice
  - active-tab provenance can drift when header meta is still driven by a sibling tab's source state
- Occurrence basis:
  - `/system/config` source tab showed `DATA: SUMMARY` and sample values `4.00`, `3/4`, `28,412`, `2.00` before repair
  - the same live route never requested `/api/v1/data-sources/config/` until the page-local fix landed
- Shared component or token involved:
  - reviewed but not changed: `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue`
  - reused but not changed: `web/frontend/src/views/artdeco-pages/system-tabs/dataManagementData.ts`
- Suggested follow-up scope:
  - future multi-tab routed-page audits should verify that every default tab with a claimed live contract actually requests and renders that contract

## Main Skill Decisions
- duplicates merged:
  - sample KPI cards, sample inventory rows, and inherited `DATA` provenance were consolidated into one tab-slice contract-truth issue because they all came from one canonical page owner on `/system/config`
- priority order applied:
  - tab-slice contract truth > count-kpi formatting > generic sample-copy cleanup
- primary owners selected:
  - `web/frontend/src/views/system/Settings.vue`
- shared-impact review items:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue` reviewed but not changed because the page-local fix was sufficient
  - `web/frontend/src/views/artdeco-pages/system-tabs/dataManagementData.ts` reused as a stable existing normalizer and not changed
- fixes applied:
  - `system-config-issue-02`
- deferred items: none

## Fix Summary
- Updated `/system/config` so the default source tab loads the live `/api/v1/data-sources/config/` contract on mount.
- Replaced sample source KPI cards and sample inventory columns with honest tab-local source-strip values plus endpoint-oriented rows.
- Switched header `DATA` provenance to the active tab so the source tab reports route-local truth instead of inheriting monitor-slice status.
- Added regression coverage for the canonical page, the ArtDeco wrapper consumer, and the routed phase-4 matrix spec.
- Extended `myweb-audit` with `v1.34` tab-slice contract truth.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-06-repair-approval.yaml`
- Approved issue ids:
  - `system-config-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch:
  - shared `ArtDecoStatCard.vue` default cleanup if more routed source-tab count surfaces accumulate

## Unresolved Items
- No approved repair remains unimplemented in `system-batch-06`.

## Reasons Not Fixed
- The shared `ArtDecoStatCard.vue` default remains unchanged because the routed source-tab defect was fixable page-locally and did not require a shared-component batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/system/__tests__/Settings.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` -> passed `6/6`
  - `npx vitest run src/views/system/__tests__/API.spec.ts src/views/system/__tests__/Health.spec.ts src/views/system/__tests__/DataSource.spec.ts src/views/system/__tests__/Settings.spec.ts src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts` -> passed `15/15`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `11` tests
  - `git diff --check -- web/frontend/src/views/system/Settings.vue web/frontend/src/views/system/__tests__/Settings.spec.ts web/frontend/src/views/artdeco-pages/system-tabs/__tests__/ArtDecoSystemSettings.spec.ts web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts .claude/skills/myweb-audit/SKILL.md .claude/skills/myweb-audit/references/audit-checklist.md .claude/agents/myweb-audit-data-state-audit.md .claude/skills/myweb-audit/references/CHANGELOG.md docs/reports/quality/myweb-audit/audit-20260426-02/manifests/system-batch-06-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/system-batch-06-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/system-batch-06-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/system-batch-06-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/system-config-source-tab-contract-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/system-batch-06-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
- Targeted routed-page verification confirmed:
  - `/system/config` now shows `DATA: REAL`
  - the source-tab strip now shows `19 / 19 / ON / <REQ_ID>` with `0` `.artdeco-stat-change` nodes
  - the routed table now shows live endpoint rows such as `AKShare龙虎榜详情数据` and `akshare.stock_lhb_detail_em`
  - the source-tab no longer shows `+0%`, `4.00`, `3/4`, `28,412`, `2.00`, or sample source rows such as `Wind`
  - actual PM2 requests reached `http://localhost:3020/api/v1/data-sources/config/`, `http://localhost:3020/api/health`, `http://localhost:3020/api/health/ready`, `http://localhost:3020/api/health/detailed`, and `http://localhost:3020/api/v1/system/settings/general` with `200`
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` runner still cannot execute Chromium on this machine because the local Playwright chromium executable is missing, so the batch relied on system `google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` is recorded as mixed-staged observation only for this run
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Continue system-domain and other multi-tab routed-page audits with the strengthened `v1.34` tab-slice contract-truth rule, especially where one tab already claims a live config, registry, or source contract but still renders sample inventory truth.
