# Steward Tree Branch Register

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: compact active branch / PR register
- Prepared at: `2026-06-03T22:23:56+08:00`
- Current workspace HEAD checked: `06b0fc09548774ba997784c878349c25087d7c88`
- Accepted PR anchor: PR `#474` merge commit `2ebff6d7ded33403c691a60fc43f87dabf90a975`

Boundary note: this register records relationship state only. It does not merge
PRs, change issue labels, authorize source implementation, or replace GitHub
PR state.

## Active / Recent G Nodes And PRs

| PR | Branch / node | Base | State | Relationship |
|---|---|---|---|---|
| `TBD` | `g2-330-service-lifecycle-di-global-residual-candidate-screening` | `wip/root-dirty-20260403` | `PLANNED_NO_SOURCE` | Screen normalized residual pool seeded by `strategy_management/_strategy_execution_router.py`; no source authorization |
| `TBD` | `g2-329-service-lifecycle-di-branch-anchor-reconciliation-before-next-residual-selection` | `wip/root-dirty-20260403` | `ACCEPTED_REVIEWED_NO_SOURCE` | Reconciled branch-anchor drift and excluded watchlist false-positive statistics from candidate pool |
| `TBD` | `g2-328-technical-analysis-datasourcefactory-provider-closeout-residual-refresh` | `wip/root-dirty-20260403` | `ACCEPTED_REVIEWED_NO_SOURCE` | Closed local technical_analysis provider lane for governance only; no PR/merge claimed |
| `TBD` | `g2-327-technical-analysis-datasourcefactory-provider-implementation` | `wip/root-dirty-20260403` | `REVIEWED_BUT_NOT_MERGED` | Source implementation accepted locally by human maintainer; state remains source_implementation_review_required |
| `TBD` | `g2-326-technical-analysis-datasourcefactory-provider-authorization-preflight` | `wip/root-dirty-20260403` | `ACCEPTED_MERGED` | Bounded future G2.327 source scope prepared; no source edits performed |
| `TBD` | `g2-325-technical-analysis-datasourcefactory-ownership-decision` | `wip/root-dirty-20260403` | `ACCEPTED_MERGED` | Classified `technical_analysis.py` as active route-local DataSourceFactory provider seam candidate |
| `TBD` | `g2-324-service-lifecycle-di-residual-candidate-selection` | `wip/root-dirty-20260403` | `ACCEPTED_MERGED` | Selected `technical_analysis.py` as next no-source ownership-decision candidate from accepted G2.322/G2.323 evidence |
| `TBD` | `g2-323-watchlist-datasourcefactory-provider-steward-surface-compaction` | `wip/root-dirty-20260403` | `ACCEPTED_MERGED` | Compact-surface freeze accepted; current files keep only active gate, parent chain, and evidence refs |
| `TBD` | `g2-322-watchlist-datasourcefactory-provider-closeout-residual-refresh` | `wip/root-dirty-20260403` | `ACCEPTED_MERGED` | Closed accepted G2.321 and refreshed DataSourceFactory residual observations |
| `#474` | `g2-321-watchlist-datasourcefactory-provider-implementation` | `wip/root-dirty-20260403` | `MERGED` at `2ebff6d7ded33403c691a60fc43f87dabf90a975` | Source implementation accepted/merged after human review |

## Current Boundary

- G2.323 is accepted_merged as a no-source steward surface compaction / baseline freeze gate.
- G2.324 is accepted_merged as a no-source residual candidate selection gate.
- G2.325 is accepted_merged as a no-source ownership decision gate.
- G2.326 is accepted_merged as a no-source authorization preflight gate.
- G2.327 source implementation is reviewed-but-not-merged; it is not accepted_merged.
- G2.328 is accepted reviewed no-source and does not claim PR creation or merge.
- G2.329 is accepted reviewed no-source branch-anchor reconciliation.
- G2.330 is planned no-source global residual candidate screening.
- Current steward files should keep only the active gate, parent chain, and evidence references.
- Long history stays in `archive/`, `completed-ledger.md`, historical reports, and generated evidence.
- G2.328 and G2.329 authorize governance artifacts only; no source, tests, API contract, frontend, config, script, OpenSpec, PM2, runtime state, or shared DataSourceFactory implementation edits are authorized by these gates.
