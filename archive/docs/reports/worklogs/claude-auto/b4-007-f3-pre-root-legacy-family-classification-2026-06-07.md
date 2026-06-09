# B4.007-F3-pre Root Legacy Family Classification

Date: 2026-06-07
Branch: `wip/root-dirty-20260403`
Mode: no-source classification
Authority: inventory and family grouping only

## Boundary

This report starts the F3 root legacy family-batch archive line after B4.007-M3 closed the mainline route governance node.

Allowed in this step:

- Read-only route/menu/pageConfig/reference/test evidence collection.
- Family classification and batch sequencing.
- Governance report writing under `docs/reports/worklogs/claude-auto/`.

Not allowed in this step:

- No source edits.
- No test edits.
- No file moves.
- No archive or deletion action.
- No business logic changes.
- No changes to ST-HOLD, `marketKlineData`, or external dirty files.

## Candidate Reconciliation

F1 history contained 12 archive-only root legacy candidates. Current F3 scope is 11 existing files because:

- `web/frontend/src/views/AdvancedAnalysis.vue` no longer exists in the working tree and is excluded from the F3 family archive queue.

The 11 current F3 Backlog files are:

| File | Exists | Current status | Router exact | Menu exact | pageConfig exact | Runtime src exact refs |
|---|---:|---|---:|---:|---:|---:|
| `web/frontend/src/views/Analysis.vue` | yes | modified | no | no | no | 0 |
| `web/frontend/src/views/IndustryConceptAnalysis.vue` | yes | modified | no | no | no | 0 |
| `web/frontend/src/views/MarketData.vue` | yes | modified | no | no | no | 0 |
| `web/frontend/src/views/monitor.vue` | yes | modified | no | no | no | 0 |
| `web/frontend/src/views/PortfolioManagement.vue` | yes | modified | no | no | no | 0 |
| `web/frontend/src/views/RealTimeMonitor.vue` | yes | modified | no | no | no | 0 |
| `web/frontend/src/views/StockDetail.vue` | yes | modified | no | no | no | 0 |
| `web/frontend/src/views/Stocks.vue` | yes | modified | no | no | no | 0 |
| `web/frontend/src/views/TaskManagement.vue` | yes | modified | no | no | no | 0 |
| `web/frontend/src/views/TdxMarket.vue` | yes | modified | no | no | no | 0 |
| `web/frontend/src/views/TechnicalAnalysis.vue` | yes | modified | no | no | no | 0 |

Common finding:

- None of the 11 files is a current router/menu/pageConfig truth source.
- None has exact runtime source references outside itself.
- Risk is not from active navigation; risk is from test/config vocabulary, historical E2E specs, broad name collisions, and the fact that all 11 files currently carry tracked modifications.

## Family Groups

### Family A: Low-risk Static Archive Group

Files:

- `web/frontend/src/views/TdxMarket.vue`

Evidence:

- No router/menu/pageConfig exact reference.
- No runtime src exact reference.
- No exact current frontend unit/E2E reference found in active frontend test paths.
- Only low-volume historical wording appears in old proposal/task docs.

Risk:

- Low runtime risk.
- Still a tracked modified source file, so archive must preserve current content and use path-scoped staging.

Recommended action after authorization:

- Archive as the first low-risk F3 family batch or merge with Family B only if the approved scope explicitly says so.
- Gate: path-scoped diff, GitNexus staged detect, type-check, and business smoke only if source movement occurs.

### Family B: Entry-guard Dependency Group

Files:

- `web/frontend/src/views/IndustryConceptAnalysis.vue`
- `web/frontend/src/views/PortfolioManagement.vue`
- `web/frontend/src/views/TaskManagement.vue`

Evidence:

- No router/menu/pageConfig exact reference.
- No runtime src exact reference.
- `root-demo-style-entrypoints.spec.ts` still references these names as root legacy entrypoint/style guard vocabulary.
- `IndustryConceptAnalysis.vue` also has a legacy E2E exact path reference in `tests/e2e/industry-concept-integration.spec.js`.

Risk:

- Low runtime risk.
- Medium validation risk because archive movement can break root-demo/style guard assertions unless those tests are intentionally updated or reclassified.

Recommended action after authorization:

- Archive the files and update only the corresponding guard/test vocabulary in the same family batch.
- Do not change route behavior or business page logic.
- Gate: focused guard tests plus stable unit suite; then type-check and business smoke.

### Family C: High-reference Config/E2E Group

Files:

- `web/frontend/src/views/Analysis.vue`
- `web/frontend/src/views/MarketData.vue`
- `web/frontend/src/views/monitor.vue`
- `web/frontend/src/views/TechnicalAnalysis.vue`

Evidence:

- No router/menu/pageConfig exact reference and no runtime src exact reference.
- `Analysis.vue` has exact references from legacy E2E specs such as `tests/e2e/analysis-integration.spec.js` and `tests/e2e/fixed-pages-e2e.spec.js`, plus many broad `Analysis` vocabulary hits.
- `MarketData.vue` has exact legacy E2E/test references such as `tests/e2e/market-data-integration.spec.js`.
- `monitor.vue` has no exact active route reference, but broad lowercase `monitor` vocabulary appears in config/test surfaces, including `web/frontend/src/config/api.js`, `web/frontend/src/config/menu.config.js`, and monitoring-related test files.
- `TechnicalAnalysis.vue` has exact historical test/change references and broad technical-analysis test vocabulary.

Risk:

- Medium to high validation risk because broad names overlap with active concepts (`analysis`, `monitor`, `market data`, `technical analysis`).
- Case-sensitive `monitor.vue` remains a platform-sensitive path.

Recommended action after authorization:

- Treat as a test/config vocabulary reconciliation family, not a simple move-only archive.
- Before source movement, decide which legacy E2E/config anchors are obsolete versus still testing a supported route.
- Gate: affected legacy E2E/test anchor review, stable unit suite, type-check, and PM2 business smoke.

### Family D: Independent High-risk Group

Files:

- `web/frontend/src/views/RealTimeMonitor.vue`
- `web/frontend/src/views/StockDetail.vue`
- `web/frontend/src/views/Stocks.vue`

Evidence:

- No router/menu/pageConfig exact reference and no runtime src exact reference.
- These names overlap with active product-critical concepts:
  - realtime market monitoring,
  - stock detail routes,
  - watchlist/stocks workflows.
- `RealTimeMonitor.vue` has exact legacy E2E/change references including `tests/e2e/realtime-monitor.spec.ts` and `tests/e2e/realtime-monitor-integration.spec.js`.
- `StockDetail.vue` has exact legacy E2E/change references including `tests/e2e/stock-detail-integration.spec.js`.
- `Stocks.vue` is referenced by CI/gate vocabulary and has broad stock-related references across tests/contracts.

Risk:

- Highest F3 risk despite no active route truth binding.
- Each name maps to a critical business concept and can easily hide obsolete-versus-active test ambiguity.

Recommended action after authorization:

- Do not merge with lower-risk archive families.
- Run as an isolated high-risk source/test archive package.
- Require explicit successor mapping before movement:
  - realtime successor: current `/market/realtime` route family,
  - stock detail successor: current detail route components,
  - stocks/watchlist successor: current `/watchlist/*` route family.
- Gate: successor-route smoke, affected legacy E2E disposition, stable unit suite, type-check, and PM2 business smoke.

## Proposed Execution Order

1. Family A: low-risk static archive pilot.
2. Family B: entry-guard dependency group.
3. Family C: high-reference config/E2E group.
4. Family D: independent high-risk group.

This preserves the strategy shift away from single-file cleanup while still keeping risk gradients visible.

## Required Authorization Shape For Next Step

Each family needs a separate source-authorized archive approval before implementation.

For each approved family, the batch should explicitly name:

- exact files to archive,
- destination archive path,
- whether matching tests/config anchors may be updated,
- focused tests to run,
- whether legacy E2E anchors are deleted, updated, or deferred,
- whether the family is archive-only or deletion-retirement.

## Current No-source Result

B4.007-F3-pre completed as no-source classification only.

No source files were edited, moved, deleted, staged, or committed by this report step.

Validation recorded for this no-source report:

- `git diff --check -- docs/reports/worklogs/claude-auto/b4-007-f3-pre-root-legacy-family-classification-2026-06-07.md`: passed.
- OPENDOG verification: fresh; failing runs `0`; cleanup blockers `0`; refactor blockers `0`.
- Latest OPENDOG build/test evidence remains the B4.007-M3 gate:
  - type-check passed,
  - PM2 business smoke passed with chromium `55/55`.

The F3 family archive line can now proceed to the first family-specific authorization package.
