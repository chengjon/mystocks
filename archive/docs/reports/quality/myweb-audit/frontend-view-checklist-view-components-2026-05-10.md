# Frontend View Checklist: `views/components` Batch

Date: 2026-05-10

Scope:
- `web/frontend/src/views/components/RiskOverviewTab.vue`
- `web/frontend/src/views/components/StopLossMonitoringTab.vue`
- `web/frontend/src/views/components/composables/useStopLossMonitoringTab.ts`
- `web/frontend/src/views/components/styles/RiskOverviewTab.css`
- `web/frontend/src/views/components/styles/StopLossMonitoringTab.css`

This checklist records lifecycle evidence only. It does not approve archive moves, shared extraction, or deletion.

## Summary

| File Group | Route/Menu Status | Direct Runtime Import Status | Guard Status | Lifecycle Result |
| --- | --- | --- | --- | --- |
| `RiskOverviewTab.vue` + style | Not in current router or menu | No active source import found | `lint:artdeco:changed` directory coverage; support style normalization spec | `candidate-review/legacy-risk-asset` |
| `StopLossMonitoringTab.vue` + composable/style | Not in current router or menu | No active source import found | `lint:artdeco:changed` directory coverage | `candidate-review/legacy-risk-asset` |

No file in this batch is `archive-approved`.

## Evidence

### Menu And Router

- `web/frontend/src/router/index.ts` does not register `views/components/*`.
- `web/frontend/src/layouts/MenuConfig.ts` does not expose `views/components/*`.
- Current risk route truth has already moved to canonical risk pages, especially `web/frontend/src/views/risk/Overview.vue`; the historical ArtDeco risk wrapper is separate from this `views/components` directory.

### Direct Code References

- Static search found no active `web/frontend/src` importer for `RiskOverviewTab.vue`.
- Static search found no active `web/frontend/src` importer for `StopLossMonitoringTab.vue`.
- `StopLossMonitoringTab.vue` imports only its local `./composables/useStopLossMonitoringTab`.
- Both view files import local CSS under `views/components/styles`.

### Guard And Historical References

- `web/frontend/package.json` includes `--target-dir src/views/components --changed-from-git` in `lint:artdeco:changed`.
- `web/frontend/tests/unit/config/support-component-style-normalization.spec.ts` directly reads `src/views/components/styles/RiskOverviewTab.css`.
- Historical directory governance notes classify `src/views/components` as `待判定，但偏向历史残留`, with explicit guidance to keep it, not extract it into `src/shared`, and not use it as a migration blocker.
- Historical reports describe these files as risk-management week assets, not current canonical route owners.

## Asset Notes

### `RiskOverviewTab.vue`

- Contains risk metric cards, portfolio risk evolution chart, risk distribution chart, system health, active monitoring stats, and recent activity list.
- Uses direct `/api/risk-management/v31/*` fetch calls and chart initialization.
- Contains static/fallback live-looking values such as GPU utilization simulation and fixed risk-distribution slices.
- If ever formalized, it needs replacement with canonical `/risk/*` data truth and verified cleanup of timer/chart lifecycle handling.

### `StopLossMonitoringTab.vue`

- Contains position monitoring, stop-loss execution history, add/edit/remove position flow, and stop-loss strategy controls.
- `useStopLossMonitoringTab.ts` calls `/api/risk-management/v31/stop-loss/*` endpoints and also keeps mocked execution-history fallback records after a successful response.
- This is a potentially reusable stop-loss workflow asset, but it is not currently a routed canonical page.
- If absorbed, the successor should be a canonical risk route or a risk-domain component with explicit API contract ownership.

## Classification

| File | Selector | Stats/Metric Cards | Shared Composable | Current Result | Successor / Absorption Hint |
| --- | --- | --- | --- | --- | --- |
| `views/components/RiskOverviewTab.vue` | Yes | Yes | No | `candidate-review/legacy-risk-asset` | Compare against canonical `views/risk/Overview.vue` before any archive decision |
| `views/components/styles/RiskOverviewTab.css` | N/A | N/A | N/A | `candidate-review/support-style` | Retire only with owning RiskOverviewTab lifecycle |
| `views/components/StopLossMonitoringTab.vue` | Yes | Yes | Local composable | `candidate-review/legacy-risk-asset` | Candidate for absorption into canonical risk stop-loss/positions workflow |
| `views/components/composables/useStopLossMonitoringTab.ts` | Yes | N/A | Local only | `candidate-review/support-composable` | Keep co-located unless 2+ canonical consumers are proven |
| `views/components/styles/StopLossMonitoringTab.css` | N/A | N/A | N/A | `candidate-review/support-style` | Retire only with owning StopLossMonitoringTab lifecycle |

## Archive Eligibility

Current eligibility: not approved.

Blocking conditions:
- Directory-level ArtDeco changed-scope gate still covers `src/views/components`.
- At least one test directly reads a support style file under this directory.
- `StopLossMonitoringTab` has functional risk workflow logic and API endpoint semantics that may be reusable.
- `RiskOverviewTab` contains risk visualization assets that require comparison against canonical risk route coverage before retirement.
- No approved mutation batch has retired the guards or recorded successor/no-successor rationale.

Required before any archive move:
- Confirm canonical risk pages fully cover or intentionally reject the risk overview and stop-loss workflow assets.
- Remove or migrate style-source and directory gate coverage in the same approved mutation batch.
- Record per-file successor or `no-successor-needed` rationale.
- Run risk route smoke/E2E if any asset is absorbed into canonical risk pages.

## Governance Conclusion

`views/components` is not an active route or menu owner, and it should not be promoted into shared infrastructure by default. It remains a legacy risk asset group under `candidate-review`; archive is blocked until canonical risk coverage, guard retirement, and successor mapping are completed.
