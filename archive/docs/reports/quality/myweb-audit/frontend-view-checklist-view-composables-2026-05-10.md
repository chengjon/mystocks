# Frontend View Checklist: `views/composables` Batch

Date: 2026-05-10

Scope:
- `web/frontend/src/views/composables/*.ts`
- `web/frontend/src/views/composables/__tests__/*`
- `web/frontend/src/views/composables/__node_tests__/*`

This checklist records lifecycle evidence for current `views/composables` assets. It does not approve extraction, archive movement, or deletion.

## Summary

| Group | Current Consumers | Guard/Test Status | Lifecycle Result |
| --- | --- | --- | --- |
| Trading terminal support | `web/frontend/src/views/TradingDashboard.vue` | Vitest + node test coverage; audit history treats it as page-local repair target | `active-support/trade-terminal-local` |
| Root demo support | `web/frontend/src/views/PyprofilingDemo.vue` | No direct route owner; root demo lifecycle applies | `candidate-review/demo-support-composable` |
| Legacy root-page support / residuals | No active source importer found in current static search | Some config specs read specific files | `candidate-review/legacy-root-support` |
| Technical analysis legacy helper set | No active source importer found in current static search; canonical technical composable also exists under `views/technical/composables` | `use-technical-analysis-types-cleanup.spec.ts` reads root helper | `candidate-review/legacy-technical-support` |

No file in this batch is `archive-approved`.

## Evidence

### Menu And Router

- `views/composables` is not a route or menu directory.
- Cleanup decisions must be based on source consumers, tests, docs, and owning page lifecycle, not on router/menu absence.

### Current Source Consumers

- `TradingDashboard.vue` imports `./composables/useTradingDashboard`.
- `useTradingDashboard.ts` imports local `./tradingDashboardActions`.
- `PyprofilingDemo.vue` imports `./composables/usePyprofilingDemo`.
- Static search found no current active source importer for `useAnalysis`, `useEnhancedDashboard`, `usePhase4Dashboard`, `useSettings`, or root `useTechnicalAnalysis`.
- `useTechnicalAnalysis.ts` still owns its local `useTechnicalAnalysis.shortcuts.ts` and `useTechnicalAnalysis.types.ts` helper files.

### Guard And Test References

- `src/views/composables/__tests__/useTradingDashboard.spec.ts` directly tests `useTradingDashboard`.
- `src/views/composables/__node_tests__/tradingDashboardActions.test.ts` directly tests `tradingDashboardActions`.
- `web/frontend/tests/unit/config/use-technical-analysis-types-cleanup.spec.ts` directly reads `src/views/composables/useTechnicalAnalysis.ts`.
- `web/frontend/tests/unit/config/console-log-cleanup-batch-29.spec.ts` directly reads `src/views/composables/useAnalysis.ts`.
- Historical `myweb-audit` trade batches repeatedly treat `useTradingDashboard.ts` as the page-local owner for `/trade/terminal` data retention and lightweight runtime truth handling.
- Prior directory governance already classified `src/views/composables` as a root-level legacy support layer, not as a candidate for broad `src/shared` extraction.

## Per-File Classification

| File | Current Result | Reason | Successor / Absorption Hint |
| --- | --- | --- | --- |
| `tradingDashboardActions.ts` | `active-support/trade-terminal-local` | Directly consumed by `useTradingDashboard`; node test verifies CSRF write actions | Keep paired with `useTradingDashboard` until a trade-terminal-specific extraction is approved |
| `useTradingDashboard.ts` | `active-support/trade-terminal-local` | Directly consumed by `TradingDashboard.vue`; heavily covered by trade audits and tests | Do not archive; if moved, update `/trade/terminal` and paired tests in same mutation batch |
| `__tests__/useTradingDashboard.spec.ts` | `active-test/trade-terminal-local` | Test guard for current trade terminal data truth | Move only with owning composable |
| `__node_tests__/tradingDashboardActions.test.ts` | `active-test/trade-terminal-local` | Test guard for action transport/CSRF behavior | Move only with owning action module |
| `usePyprofilingDemo.ts` | `candidate-review/demo-support-composable` | Directly consumed by root `PyprofilingDemo.vue`, a demo/root legacy page | Govern with root demo page lifecycle |
| `useTechnicalAnalysis.ts` | `candidate-review/legacy-technical-support` | No active source importer found, but config test reads it; canonical technical helper exists elsewhere | Compare with `views/technical/composables/useTechnicalAnalysis.ts` before any retirement |
| `useTechnicalAnalysis.shortcuts.ts` | `candidate-review/legacy-technical-support` | Local helper for root `useTechnicalAnalysis.ts` | Retire only with owning root helper |
| `useTechnicalAnalysis.types.ts` | `candidate-review/legacy-technical-support` | Local type helper for root `useTechnicalAnalysis.ts` | Retire only with owning root helper |
| `useAnalysis.ts` | `candidate-review/legacy-root-support` | No active source importer found, but config cleanup spec reads it | Requires root `Analysis.vue` lifecycle confirmation and test cleanup |
| `useEnhancedDashboard.ts` | `candidate-review/legacy-root-support` | No active source importer found in current static search | Compare with current `/dashboard` and root `EnhancedDashboard.vue` lifecycle before archive |
| `usePhase4Dashboard.ts` | `candidate-review/legacy-root-support` | No active source importer found for root helper; separate demo helper exists under `views/demo/composables` | Do not merge with demo fork mechanically; compare dashboard successors first |
| `useSettings.ts` | `candidate-review/legacy-root-support` | No active source importer found in current static search | Compare with canonical `views/system/Settings.vue` and settings domain pages before archive |

## Archive Eligibility

Current eligibility: not approved.

Blocking conditions:
- `useTradingDashboard.ts` and `tradingDashboardActions.ts` are active support code for `TradingDashboard.vue`.
- Paired tests under `views/composables` still protect trade terminal behavior.
- Config cleanup tests directly read some legacy files.
- Several helpers may have been superseded by domain-local composables, but successor coverage has not been formally proven per file.
- Current worktree already contains unrelated deletions/modifications in this area; this checklist must not be treated as approval to delete additional files.

Required before any archive or extraction move:
- Separate active trade-terminal support from legacy root-page support.
- For each legacy helper, record a successor page/composable or explicit `no-successor-needed` rationale.
- Remove or migrate paired tests and config guard references in the same approved mutation batch.
- If moving `useTradingDashboard`, run the trade terminal Vitest suite and wrapper-retention tests.
- If retiring technical helpers, compare against `views/technical/composables/useTechnicalAnalysis.ts` and preserve required types/shortcuts where still useful.

## Governance Conclusion

`views/composables` is not a canonical shared layer. It is a mixed support directory containing active `/trade/terminal` local logic plus legacy root/demo helpers. The correct governance action is split classification, not bulk shared extraction and not bulk archive. Only the active trade pair is excluded from archive flow; the remaining helpers stay `candidate-review` until successor mapping and guard cleanup are complete.
