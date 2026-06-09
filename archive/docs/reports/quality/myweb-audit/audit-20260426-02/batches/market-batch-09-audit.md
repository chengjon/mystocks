# Batch Audit Report: market-batch-09

## Scope
- Module: market
- Pages:
  - /market/realtime
- Batch rationale: apply existing selector-scoped verified-snapshot truth to the canonical realtime preset selector so same-instance preset switches no longer keep the previous preset's verified quote rows visible under a new unresolved preset shell

## Agent Summary

### route-inventory
- `/market/realtime` remains the canonical realtime route at `web/frontend/src/views/market/Realtime.vue`.

### data-state-audit
- One high-severity selector truth defect remained: the route still treated one global verified quote snapshot as proof for every local preset.
- The defect appeared when the same mounted route switched from a verified `核心蓝筹样本` preset to another preset whose first load had not verified yet.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed market page can already own a local preset selector but still keep one route-global verified row set and request provenance, so same-instance selector switches leak old rows into a newly requested preset before that preset verifies.
- Occurrence basis:
  - `/market/realtime` owned the preset selector in the route itself
  - the visible rows and hero `TRACE_ID` were not preset-scoped
  - the active shell could therefore inherit stale rows and provenance from the previously verified preset
- Shared component or helper involved:
  - none beyond the canonical route owner
- Suggested follow-up scope: continue applying existing selector-scoped verified-snapshot truth to routed market or workbench pages that can switch local presets, periods, or sample groups without remounting.

## Main Skill Decisions
- duplicates merged: no
- priority order applied: selector-scoped verified-snapshot truth > selector-owned row provenance > pending-selector honesty
- primary owner selected:
  - `web/frontend/src/views/market/Realtime.vue`
- shared-impact review items:
  - none beyond the canonical realtime route
- fixes applied:
  - `market-realtime-issue-03`
- deferred items: none

## Fix Summary
- Stored verified quote snapshots by preset instead of one route-global `overview`.
- Scoped hero `TRACE_ID` to the active preset's own verified request provenance.
- Rendered visible quote rows only from the active preset's verified snapshot.
- Added owner and Phase 1 routed regressions that lock the `核心蓝筹样本 -> 金融权重样本` same-instance unresolved-switch proof.
- Reused existing `myweb-audit v1.71` / `v1.68` selector rules without adding a new version.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/market-batch-09-repair-approval.yaml`
- Approved issue ids:
  - `market-realtime-issue-03`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `market-batch-09`.

## Reasons Not Fixed
- The repair intentionally stayed inside the canonical realtime owner; no shared request-wrapper, table, or dashboard primitive was changed.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - browser-context interception with `serviceWorkers: block` isolated the `核心蓝筹样本 -> 金融权重样本` unresolved preset-switch proof on `/market/realtime`
- Regression checks completed:
  - `npx vitest run src/views/market/__tests__/Realtime.spec.ts src/views/market/__tests__/LHB.spec.ts src/views/market/__tests__/Technical.spec.ts` -> passed `12/12`
  - `npx vitest run src/views/market/__tests__/Realtime.spec.ts -t "does not leak the previous preset rows into a new preset while that preset is still on its first unresolved load"` -> passed `1/1` after first reproducing the expected red failure
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed the new market realtime preset-selector assertion in a structurally valid matrix
  - `timeout 180s npm run type-check` -> failed only on pre-existing unrelated errors in `src/components/technical/composables/useKLinePatternOverlays.ts`; no new type errors were introduced by this batch's touched files
  - targeted routed-page verification confirmed:
    - `/market/realtime` first shows a verified `核心蓝筹样本` snapshot with `3` visible rows
    - after switching to active `金融权重样本` while the finance-preset request is unresolved, the route no longer shows the old preset rows
    - the unresolved finance path now renders `TRACE_ID: N/A / SAMPLE: --` and the pending distribution copy
- `pm2 list` must confirm `mystocks-backend` and `mystocks-frontend` online at closeout
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path

## Next Batch Plan
- Continue applying selector-scoped verified-snapshot truth to routed market, dashboard, and detail pages that can switch local selectors without remounting.
