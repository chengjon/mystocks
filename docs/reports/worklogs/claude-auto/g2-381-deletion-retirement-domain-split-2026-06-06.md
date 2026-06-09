# G2.381 Deletion-Retirement Candidate Domain Split

> **Date**: 2026-06-06
>
> **Mode**: `no-source`
>
> **source_edit_authority**: `false`
>
> **test_edit_authority**: `false`
>
> **Scope**: current tracked deletion candidates (`D`) in the dirty worktree
>
> **Guide**: `docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE.md`

## 1. Boundary

This node only splits deletion candidates into domains and proposes follow-up inventories.

Allowed:

- read-only deletion candidate inventory
- domain grouping
- risk ordering and next-node recommendation
- writing this report

Forbidden:

- accepting any deletion
- staging deleted files
- restoring deleted files
- committing deletion candidates
- editing source/test/frontend files
- archiving OpenSpec changes

## 2. Evidence Summary

Current tracked deletion candidates:

```text
deletion_count: 112
```

By top-level path:

| Top-level path | Count |
|---|---:|
| `openspec` | 76 |
| `web` | 32 |
| `DELETION-CANDIDATES.md` | 1 |
| `docs` | 1 |
| `scripts` | 1 |
| `tests` | 1 |

By domain:

| Domain | Count | Initial risk | Initial disposition |
|---|---:|---|---|
| OpenSpec changes | 76 | High | Do not accept. Requires OpenSpec active-change/spec validation and archive/delete decision. |
| Web frontend | 28 | High | Do not accept. Requires route/view/style/test ownership checks and frontend gates. |
| Web backend | 4 | Medium/High | Backup-looking files, but still require reference/path and service-boundary checks. |
| Root deletion candidate registry | 1 | Medium | Do not accept until replacement/disposition is clear. |
| Docs | 1 | Medium | Do not accept until doc canonicality is checked. |
| Scripts | 1 | Medium/High | Do not accept until command/tool ownership is checked. |
| Tests | 1 | Medium/High | Do not accept until paired script/test retirement is proven. |

## 3. Domain Details

### 3.1 OpenSpec Changes

Count: `76`.

Largest subgroups:

| Subgroup | Count |
|---|---:|
| `openspec/changes/add-broker-acknowledgement-reconciliation-contract` | 6 |
| `openspec/changes/add-miniqmt-live-bridge-runtime-contract` | 5 |
| `openspec/changes/add-miniqmt-primary-broker-adapter-runtime` | 5 |
| `openspec/changes/add-windows-qmt-agent-reference-service` | 5 |
| `openspec/changes/add-windows-qmt-agent-runtime-contract` | 5 |
| `openspec/changes/add-broker-channel-topology-for-miniqmt-and-tdx` | 4 |
| `openspec/changes/add-kronos-integration-contract` | 4 |
| `openspec/changes/add-page-audit-orchestration-governance` | 4 |
| `openspec/changes/add-portfolio-attribution-analysis` | 4 |
| `openspec/changes/add-stop-hook-graphiti-task-closeout` | 4 |
| `openspec/changes/add-windows-qmt-contract-acceptance-harness` | 4 |
| `openspec/changes/add-windows-qmt-contract-formal-sequence` | 4 |
| `openspec/changes/add-windows-qmt-service-readiness-probe` | 4 |
| `openspec/changes/align-artdeco-stateful-primitives-with-design` | 4 |
| `openspec/changes/align-business-route-status-and-tooltip-surfaces` | 4 |
| `openspec/changes/implement-pinia-api-standardization` | 4 |
| `openspec/changes/update-miniqmt-phase-a-contract-hardening` | 4 |

Sample deleted paths include:

```text
openspec/changes/add-broker-acknowledgement-reconciliation-contract/design.md
openspec/changes/add-broker-acknowledgement-reconciliation-contract/proposal.md
openspec/changes/add-broker-acknowledgement-reconciliation-contract/specs/architecture-governance/spec.md
openspec/changes/add-broker-acknowledgement-reconciliation-contract/specs/broker-acknowledgement-reconciliation/spec.md
openspec/changes/add-broker-channel-topology-for-miniqmt-and-tdx/design.md
openspec/changes/add-containerized-runtime-deployment-capability/tasks.md
openspec/changes/add-kronos-integration-contract/proposal.md
openspec/changes/add-miniqmt-live-bridge-runtime-contract/design.md
```

Decision: OpenSpec deletion must be its own no-source inventory before any delete acceptance. It must run `openspec list`, inspect active changes/specs, and validate whether each deleted change was archived, superseded, or accidentally removed.

### 3.2 Web Frontend

Count: `28`.

Deleted path set:

```text
web/frontend/src/views/SkeletonUsage.vue
web/frontend/src/views/composables/useAdvancedAnalysis.ts
web/frontend/src/views/composables/useBacktestWizard.ts
web/frontend/src/views/composables/useIndustryConceptAnalysis.ts
web/frontend/src/views/composables/usePortfolioManagement.ts
web/frontend/src/views/composables/usemonitor.ts
web/frontend/src/views/market/composables/useTdx.ts
web/frontend/src/views/market/styles/Tdx.scss
web/frontend/src/views/stock-analysis/StockBacktestTab.vue
web/frontend/src/views/stock-analysis/StockDataTab.vue
web/frontend/src/views/stock-analysis/StockOverviewTab.vue
web/frontend/src/views/stock-analysis/StockRealtimeTab.vue
web/frontend/src/views/stock-analysis/StockStatusTab.vue
web/frontend/src/views/stock-analysis/StockStrategyTab.vue
web/frontend/src/views/strategy/styles/BatchScan.scss
web/frontend/src/views/strategy/styles/ResultsQuery.scss
web/frontend/src/views/strategy/styles/SingleRun.scss
web/frontend/src/views/strategy/styles/StatsAnalysis.scss
web/frontend/src/views/styles/BacktestWizard.scss
web/frontend/src/views/styles/IndustryConceptAnalysis.scss
web/frontend/src/views/styles/PortfolioManagement.scss
web/frontend/src/views/styles/RealTimeMonitor.scss
web/frontend/src/views/styles/StockAnalysisDemo.scss
web/frontend/src/views/styles/monitor.scss
web/frontend/tests/unit/config/batch-scan-style-source.spec.ts
web/frontend/tests/unit/config/results-query-style-source.spec.ts
web/frontend/tests/unit/config/single-run-style-source.spec.ts
web/frontend/tests/unit/config/stats-analysis-style-source.spec.ts
```

Decision: frontend deletion candidates are high risk. They include views, composables, styles, and tests. Do not accept them as one deletion batch. Split by route/domain and check `web/frontend/src/router/index.ts`, active route specs, import references, unit tests, and route-header handoff boundaries.

### 3.3 Web Backend

Count: `4`.

Deleted path set:

```text
web/backend/app/services/data_adapter.py.backup.20260130
web/backend/app/services/watchlist_service.py.bak2
web/backend/app/services/watchlist_service.py.bak3
web/backend/app/services/watchlist_service.py.before_schema_update
```

Decision: backend candidates look like backup/temporary files, but deletion still needs proof. Check active imports, dynamic paths, docs references, and whether a prior cleanup charter already authorized backup-file retirement.

### 3.4 Singletons

Count: `4`.

Deleted path set:

```text
DELETION-CANDIDATES.md
docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md
scripts/opencode/sync_omc_model_catalog.py
tests/unit/test_sync_omc_model_catalog.py
```

Decision: these cannot be handled as one group.

- `DELETION-CANDIDATES.md`: root governance registry. Needs replacement/disposition proof before deletion acceptance.
- `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md`: documentation canonicality check required.
- `scripts/opencode/sync_omc_model_catalog.py` and `tests/unit/test_sync_omc_model_catalog.py`: likely paired script/test retirement candidate; must be evaluated together.

## 4. Decision Table

| Candidate group | Count | Proposed next node | Mode | Required evidence before acceptance |
|---|---:|---|---|---|
| OpenSpec changes | 76 | `G2.382 openspec deletion-retirement active-change inventory` | no-source | `openspec list`, active change/spec inspection, archive/supersession evidence. |
| Web frontend | 28 | `G2.383 frontend deletion-retirement route-domain inventory` | no-source | Router/import/style/test ownership checks, route-header handoff review. |
| Web backend backups | 4 | `G2.384 backend backup-file deletion-retirement inventory` | no-source | Import/reference scans, backup-file policy, focused backend smoke if accepted later. |
| Root/docs/script/test singletons | 4 | `G2.385 singleton deletion-retirement inventory` | no-source | Per-file canonicality or paired script/test retirement evidence. |

## 5. Closeout

G2.381 produced only this domain-split report.

No deletion was accepted.
No deletion was staged.
No file was restored.
No source changed.
No tests changed.
No commit was made.
