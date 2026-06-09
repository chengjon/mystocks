# Batch Audit Report: detail-batch-02

## Scope
- Module: detail
- Pages:
  - /detail/news/:symbol
- Batch rationale: close the canonical `/detail/news/:symbol` sibling-stats contract truth gap so a dedicated live announcement stats slice no longer surfaces one live total beside label-only sibling cards or unresolved `0` fallbacks, and codify that routed failure mode as `myweb-audit v1.50`.

## Agent Summary

### route-inventory
- `/detail/news/:symbol` remains the canonical routed announcement detail workbench at `web/frontend/src/views/announcement/AnnouncementMonitor.vue`.

### functional-audit
- No new routed interaction-path defect required a separate repair wave beyond restoring honest stats-slice rendering on the existing detail news shell.

### data-state-audit
- One high-severity routed truth cluster remained: the detail route requested a multi-field stats contract but only surfaced `total_count`, leaving the sibling stat cards as label-only or unresolved zero-fallback surfaces.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed page can request a dedicated live stats or summary contract and still present broken truth if only one sibling field is wired into the visible shell while adjacent cards remain static labels or unresolved zero fallbacks.
- Occurrence basis:
  - `/detail/news/:symbol` previously surfaced only `公告总数`
  - the same route previously rendered unresolved stats as a lone `0`
  - the same route previously left `TODAY`, `IMPORTANT`, and `TRIGGERED` as label-only siblings even after live stats verified
- Shared component or token involved:
  - none for the approved product repair
- Suggested follow-up scope: continue applying `v1.50 + v1.38` to routed pages that request a dedicated live stats or summary contract but still surface only a subset of sibling fields.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed sibling-stats contract issue
- priority order applied: render all verified sibling stats > degrade every unverified sibling stat to placeholder truth > keep the repair page-local
- primary owners selected:
  - `web/frontend/src/views/announcement/AnnouncementMonitor.vue`
- shared-impact review items:
  - none for the approved product repair
- fixes applied:
  - `detail-news-issue-02`
- deferred items: none

## Fix Summary
- Added page-local `displayStats` derivation so the route now surfaces all four sibling announcement counts from the dedicated stats contract.
- Added placeholder gating so unresolved or failed stats slices render `-- / -- / -- / --` instead of one `0` plus label-only siblings.
- Strengthened the routed component regression with explicit unresolved and verified sibling-stats assertions.
- Strengthened the Phase 4 routed matrix with an explicit `/detail/news/:symbol` sibling-stats contract truth assertion.
- Introduced `myweb-audit v1.50` so future audits treat one-live-count-plus-label-only-siblings as a routed truth failure, not a cosmetic issue.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/detail-batch-02-repair-approval.yaml`
- Approved issue ids:
  - `detail-news-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `detail-batch-02`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/announcement/__tests__/AnnouncementMonitor.spec.ts` -> passed `2/2`
  - `npx vitest run src/views/announcement/__tests__/AnnouncementMonitor.spec.ts src/views/risk/__tests__/News.spec.ts` -> passed `5/5`
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `28` structurally valid tests including the new `/detail/news/:symbol` sibling-stats assertion
  - `timeout 180s npm run type-check` -> passed
  - `git diff --check -- web/frontend/src/views/announcement/AnnouncementMonitor.vue web/frontend/src/views/announcement/__tests__/AnnouncementMonitor.spec.ts web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts .claude/skills/myweb-audit/SKILL.md .claude/skills/myweb-audit/references/CHANGELOG.md .claude/skills/myweb-audit/references/audit-checklist.md .claude/agents/myweb-audit-data-state-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/findings/detail-batch-02-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/detail-batch-02-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/detail-batch-02-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/detail-batch-02-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/detail-news-sibling-stats-contract-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/detail-batch-02-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - targeted system-Chrome browser verification confirmed:
    - a controlled success path now renders `2 / 2 / 1 / 0` across the four top stat cards
    - a controlled stats-slice failure path now renders `-- / -- / -- / --` while preserving the live announcement table row
    - the stats-failure path no longer falls through to `公告总数 0` or a single-count-plus-label-only shell
    - natural PM2 `/detail/news/600519` still reaches the route and currently renders four live count cards `0 / 0 / 0 / 0`
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/detail-batch-02-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/detail-batch-02-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/detail-batch-02-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/detail-batch-02-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/detail-batch-02-manifest.yaml` -> passed
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system `google-chrome` Playwright-library verification for the changed browser path
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` returned `risk_level: low`, `changed_files: 126`, `changed_count: 317`, and `affected_count: 0`, but the staged set remains mixed with earlier batches and unrelated files, so the result is recorded as observation-only rather than isolated `detail-batch-02` scope

## Next Batch Plan
- Continue the detail and adjacent announcement route family on any remaining pages that request dedicated live stats or summary slices but still surface only a partial sibling-count shell.
