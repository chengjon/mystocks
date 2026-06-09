# B4.012 frontend deletion pre-authorization

Date: 2026-06-06
Branch: `wip/root-dirty-20260403`
Mode: `no-source`

## Governance boundary

This node rechecks the B4.002 frontend deletion-retirement ledger before deletion authorization. It does not delete, restore, edit, stage, commit, or accept any frontend file.

Primary references:

- `architecture/STANDARDS.md`
- `docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE.md`
- `docs/reports/worklogs/claude-auto/b4-002-frontend-deletion-candidate-inventory-2026-06-06.md`
- `docs/reports/worklogs/claude-auto/b4-011-frontend-residual-reconciliation-2026-06-06.md`

Timing constraint:

- Land the B4.002 deletion-retirement packages first and remove the 28 deleted dirty rows from the worktree.
- Only after that should the queue move to B4.010 `TC-1 runtime tooling/config` authorization and source/config commits.

## Recheck method

Read-only checks:

- Parse the B4.002 candidate table.
- Reconfirm the 28 B4.002 paths are still deleted in current `git status --porcelain=v1 -- web/frontend`.
- Re-scan `web/frontend/src/router/index.ts` for exact route references.
- Re-scan current `web/frontend/src/**` files for exact runtime path references.
- Query OPENDOG verification status and record the stale cleanup blocker.

Exact-reference variants included forms such as:

- `views/path/File.vue`
- `views/path/File`
- `@/views/path/File.vue`
- `@/views/path/File`
- relative `../` and `./` forms

This scan intentionally does not treat broad basename matches as runtime references because owner pages can legitimately share component/style names without importing the deleted path.

## Recheck result

| Metric | Value |
| --- | ---: |
| B4.002 rows parsed | 28 |
| Current deleted status rows | 28 |
| Safe-retirement rows | 13 |
| Archive-first deletion rows | 15 |
| Current router exact references | 0 |
| Current `web/frontend/src` exact runtime references | 0 |
| Dependency-coupled restore candidates | 0 |

Conclusion: the original B4.002 route/runtime isolation conclusion still holds. The pre-authorization result is pass for package planning only. This report does not authorize actual deletion commits by itself.

## DR-A safe-retirement package

Recommended later package: `DR-A frontend safe deletion-retirement`.

Authority needed later: `deletion-retirement-authorized`.

Package rule: stage exactly these 13 deleted paths, and do not mix owner page changes, tests, config, tooling, or unrelated cleanup.

| # | Deleted path | Current status | Router refs | Runtime refs | Archive requirement |
| ---: | --- | --- | ---: | ---: | --- |
| 1 | `web/frontend/src/views/SkeletonUsage.vue` | deleted | 0 | 0 | B4.012 report row is sufficient. |
| 2 | `web/frontend/src/views/composables/useAdvancedAnalysis.ts` | deleted | 0 | 0 | B4.012 report row is sufficient; owner page remains separate. |
| 3 | `web/frontend/src/views/composables/useBacktestWizard.ts` | deleted | 0 | 0 | B4.012 report row is sufficient; owner page remains separate. |
| 4 | `web/frontend/src/views/composables/useIndustryConceptAnalysis.ts` | deleted | 0 | 0 | B4.012 report row is sufficient; owner page remains separate. |
| 5 | `web/frontend/src/views/composables/usePortfolioManagement.ts` | deleted | 0 | 0 | B4.012 report row is sufficient; owner page remains separate. |
| 6 | `web/frontend/src/views/composables/usemonitor.ts` | deleted | 0 | 0 | B4.012 report row is sufficient; owner page remains separate. |
| 7 | `web/frontend/src/views/market/composables/useTdx.ts` | deleted | 0 | 0 | B4.012 report row is sufficient; `market/Tdx.vue` remains separate. |
| 8 | `web/frontend/src/views/market/styles/Tdx.scss` | deleted | 0 | 0 | B4.012 report row is sufficient; `market/Tdx.vue` remains separate. |
| 19 | `web/frontend/src/views/styles/BacktestWizard.scss` | deleted | 0 | 0 | B4.012 report row is sufficient; owner page remains separate. |
| 20 | `web/frontend/src/views/styles/IndustryConceptAnalysis.scss` | deleted | 0 | 0 | B4.012 report row is sufficient; owner page remains separate. |
| 21 | `web/frontend/src/views/styles/PortfolioManagement.scss` | deleted | 0 | 0 | B4.012 report row is sufficient; owner page remains separate. |
| 22 | `web/frontend/src/views/styles/RealTimeMonitor.scss` | deleted | 0 | 0 | B4.012 report row is sufficient; owner page remains separate. |
| 24 | `web/frontend/src/views/styles/monitor.scss` | deleted | 0 | 0 | B4.012 report row is sufficient; owner page remains separate. |

DR-A risk: medium. The files are runtime-isolated, but deletion still changes repository history and must pass deletion-retirement commit gates.

## DR-B archive-first deletion package

Recommended later package: `DR-B frontend archive-first deletion-retirement`.

Authority needed later: `deletion-retirement-authorized` plus archive/test-baseline disposition.

Package rule: stage exactly these 15 deleted paths only after recording archive notes for evidence-coupled paths and deleted test specs.

| # | Deleted path | Current status | Router refs | Runtime refs | Archive requirement |
| ---: | --- | --- | ---: | ---: | --- |
| 9 | `web/frontend/src/views/stock-analysis/StockBacktestTab.vue` | deleted | 0 | 0 | Preserve stock-analysis style-normalization evidence note. |
| 10 | `web/frontend/src/views/stock-analysis/StockDataTab.vue` | deleted | 0 | 0 | Preserve stock-analysis style-normalization evidence note. |
| 11 | `web/frontend/src/views/stock-analysis/StockOverviewTab.vue` | deleted | 0 | 0 | Preserve stock-analysis style-normalization evidence note. |
| 12 | `web/frontend/src/views/stock-analysis/StockRealtimeTab.vue` | deleted | 0 | 0 | Preserve stock-analysis style-normalization evidence note. |
| 13 | `web/frontend/src/views/stock-analysis/StockStatusTab.vue` | deleted | 0 | 0 | Preserve stock-analysis style-normalization evidence note. |
| 14 | `web/frontend/src/views/stock-analysis/StockStrategyTab.vue` | deleted | 0 | 0 | Preserve stock-analysis style-normalization evidence note. |
| 15 | `web/frontend/src/views/strategy/styles/BatchScan.scss` | deleted | 0 | 0 | Preserve legacy strategy workbench decommission evidence note. |
| 16 | `web/frontend/src/views/strategy/styles/ResultsQuery.scss` | deleted | 0 | 0 | Preserve legacy strategy workbench decommission evidence note. |
| 17 | `web/frontend/src/views/strategy/styles/SingleRun.scss` | deleted | 0 | 0 | Preserve legacy strategy workbench decommission evidence note. |
| 18 | `web/frontend/src/views/strategy/styles/StatsAnalysis.scss` | deleted | 0 | 0 | Preserve legacy strategy workbench decommission evidence note. |
| 23 | `web/frontend/src/views/styles/StockAnalysisDemo.scss` | deleted | 0 | 0 | Preserve stock-analysis style-normalization evidence note. |
| 25 | `web/frontend/tests/unit/config/batch-scan-style-source.spec.ts` | deleted | 0 | 0 | Preserve deleted spec purpose before accepting removal. |
| 26 | `web/frontend/tests/unit/config/results-query-style-source.spec.ts` | deleted | 0 | 0 | Preserve deleted spec purpose before accepting removal. |
| 27 | `web/frontend/tests/unit/config/single-run-style-source.spec.ts` | deleted | 0 | 0 | Preserve deleted spec purpose before accepting removal. |
| 28 | `web/frontend/tests/unit/config/stats-analysis-style-source.spec.ts` | deleted | 0 | 0 | Preserve deleted spec purpose before accepting removal. |

DR-B risk: high. The paths are runtime-isolated, but the package is evidence-coupled and includes deleted tests. It must not be combined with DR-A unless the user explicitly approves a single deletion-retirement batch.

## Archive note standard for DR-B

Before staging DR-B, record a durable archive note in the deletion commit report or adjacent worklog. Each archive note should include:

- Deleted path.
- Evidence owner path or deleted spec path.
- Original B4.002 evidence-ref count.
- Current B4.012 router/runtime ref result.
- Retirement rationale.
- Whether the behavior is already represented by another active route, style contract, or governance test.
- Whether any related tests were intentionally removed, replaced, or preserved elsewhere.

Minimum archive groups:

| Group | Paths | Required note |
| --- | ---: | --- |
| stock-analysis retired tabs | 6 | Explain why retired tab components are no longer route/runtime dependencies and how style-normalization evidence is preserved. |
| strategy legacy workbench styles | 4 | Explain why legacy workbench SCSS files are retired and how decommission evidence is preserved. |
| StockAnalysisDemo style | 1 | Explain relation to stock-analysis style-normalization evidence. |
| deleted style-source specs | 4 | Preserve the purpose of each removed spec and state whether a replacement or superseding guard exists. |

## OPENDOG stale risk acceptance

Current OPENDOG verification status for project `mystocks`:

| Field | Value |
| --- | --- |
| freshness status | `stale` |
| age seconds | `1994708` |
| stale after seconds | `604800` |
| stale kinds | `test`, `lint`, `build` |
| cleanup gate | `blocked` |
| refactor gate | `blocked` |
| cleanup blocker | Recorded verification evidence is stale and should be refreshed before risky changes. |

B4.012 written risk acceptance:

- Accepted only for this `no-source` pre-authorization inventory.
- Not accepted as a waiver for deletion-retirement commits.
- Actual DR-A or DR-B deletion commits must either refresh OPENDOG verification evidence before staging/committing, or include a separate explicit human-approved stale-risk acceptance in the commit worklog.

## Deletion-retirement commit gates

Before any deletion-retirement-authorized commit:

1. Obtain explicit user approval naming the exact batch: DR-A, DR-B, or a user-approved combined batch.
2. Re-run `git status --porcelain=v1 -- web/frontend` and confirm the target paths are still deleted and no unrelated paths are staged.
3. Re-run route/runtime exact-reference check for the target paths.
4. Refresh OPENDOG verification evidence, or record explicit stale-risk acceptance for the commit batch.
5. Run GitNexus change detection before commit. If the GitNexus index is stale, run `gitnexus analyze` first.
6. Stage only the named deletion paths.
7. Confirm `git diff --cached --name-status` contains only expected `D` rows.
8. Run frontend verification appropriate to the batch:
   - DR-A minimum: frontend build and relevant frontend test gate, unless explicitly waived.
   - DR-B minimum: DR-A checks plus targeted related governance/unit tests or documented replacement evidence.
   - If E2E is skipped, record the reason and the residual risk.
9. Confirm the final report distinguishes newly introduced issues from existing debt.
10. Commit with a deletion-retirement message that names the batch and report.

Suggested commit order:

1. DR-A safe deletion-retirement.
2. DR-B archive-first deletion-retirement.
3. Only after both are landed and the 28 deleted dirty rows are gone, start B4.010 `TC-1 runtime tooling/config` authorization preflight.

## Verification performed

Read-only checks only:

- B4.002 candidate table parse.
- Current deleted status confirmation.
- Current router exact-reference scan.
- Current `web/frontend/src` exact runtime-reference scan.
- OPENDOG verification stale status query.
- Deletion package and commit gate drafting.

Not run:

- Frontend build
- Frontend type check
- Vitest
- Playwright/E2E
- PM2 service checks

Reason: B4.012 is a no-source pre-authorization pass and does not modify, delete, stage, or accept frontend files.
