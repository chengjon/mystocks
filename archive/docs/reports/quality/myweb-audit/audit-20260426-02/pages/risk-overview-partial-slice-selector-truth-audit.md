# Page Audit: /risk/overview partial slice selector truth

## Page
- Route: `/risk/overview`
- Canonical entry: `web/frontend/src/views/risk/Overview.vue`
- Audit focus: preserve rules-slice truth when alerts fail before the first full overview snapshot exists

## Finding
- Severity: High
- Issue id: `risk-overview-issue-16`
- Summary: the routed owner previously treated `alert-rules` and `alerts` as one global verified shell, so a first-load alerts failure hid a verified rules slice and rewrote the whole page to `当前暂无已验证风险概览快照。`

## Repair
- Added separate verified snapshot ownership for rules and alerts inside the canonical owner.
- Bound hero `REQ_ID`, summary counts, `RULES` meta, and runtime copy to the active visible slice instead of one route-global request id and verified flag.
- Preserved the existing stale-refresh behavior for a fully verified overview shell.

## Verification
- Owner regression: `npx vitest run src/views/risk/__tests__/Overview.spec.ts`
- Routed matrix coverage: `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list`
- Controlled browser proof:
  - overview shell stays `REQ_ID: N/A / ALERTS: --`
  - top stats stay partial `2 / 2 / -- / 未校验`
  - switching to `规则清单` exposes `REQ_ID: req-live-risk-overview-rules-first-success`, `RULES: 2`, and the verified rows
  - the same browser proof shows `risk alerts unavailable，当前预警消息暂不可用。`
