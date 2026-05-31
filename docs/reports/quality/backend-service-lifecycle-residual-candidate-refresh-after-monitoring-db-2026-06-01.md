# Backend Service Lifecycle Residual Candidate Refresh After get_monitoring_db

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Gate: `G2.280`
- Status: for review
- Prepared at: `2026-06-01T01:32:16+08:00`
- Base HEAD checked: `fcead56344110e33041319271c122e71d2b763a0`
- Parent PR: `#432`
- Parent merge commit: `fcead56344110e33041319271c122e71d2b763a0`
- Source edit authority: no

Boundary note: this report records residual candidate selection only. It does
not authorize backend source edits, test edits, route registration changes,
generated OpenAPI artifact edits, frontend/config/script edits, OpenSpec
changes, PM2 commands, or runtime state changes.

## Parent Closeout

PR `#432` merged G2.279 at
`fcead56344110e33041319271c122e71d2b763a0`.

G2.279 closed the `get_monitoring_db` route-provider sequence for the current
risk and strategy surfaces:

- strategy target direct `get_monitoring_db().log_operation(...)` calls: `0`
- strategy route dependency parameters: `6`
- risk route-body direct `get_monitoring_db().log_operation(...)` calls: `0`
- utility same-name helper in `web/backend/app/utils/risk_utils.py`: retained
  and deferred

## Scan Summary

The G2.280 scan covered:

- `web/backend/app/api`
- `web/backend/app/services`

Results:

- Python files scanned: `371`
- Getter-like names seen: `572`
- Active interesting candidates after known-closed exclusions: `31`
- Runtime/OpenAPI smoke: `548` routes, `500` OpenAPI paths, duplicate
  operation IDs `0`

The scan excluded method calls such as `object.get_data(...)` from provider
candidate ranking. It also excluded previously closed or retained surfaces such
as `get_monitoring_db`, `get_postgres_async`, `get_mock_data_manager`,
`get_calculator_factory`, `get_unified_data_service`, `get_strategy_service`,
and route-local provider wrappers created by recent G2 lanes.

## Candidate Triage

| Candidate | Active API calls | Service calls | Files | Classification | Disposition |
|---|---:|---:|---:|---|---|
| `get_integrated_services` | 0 | 7 | 1 | root facade compatibility surface | Defer to separate root facade compatibility decision |
| `get_indicator_registry` | 0 | 5 | 5 | ambiguous registry surface | Defer until registry ownership is disambiguated |
| `get_lineage_tracker` | 5 | 0 | 1 | bounded active API route helper / provider candidate | Select for next no-source ownership / route-provider decision |
| `get_postgres_connection` | 5 | 0 | 1 | control-plane DB connection helper | Defer to control-plane route/OpenAPI ownership decision |
| `get_redis_client` | 0 | 4 | 4 | infrastructure cache/client helper | Defer to infrastructure/cache ownership lane |
| `get_cache_integration` | 0 | 4 | 4 | cache integration infrastructure surface | Defer to infrastructure/cache ownership lane |
| `get_cache_manager` | 1 | 0 | 3 | ambiguous dashboard/cache helper | Defer until dashboard/core cache ownership is disambiguated |

## GitNexus Evidence

GitNexus MCP `context` for `get_integrated_services` returned `Transport closed`.
CLI fallback was used for sampled impact checks.

| Candidate | CLI result | Disposition |
|---|---|---|
| `get_integrated_services` | MEDIUM, impacted count `13`, direct `13`, processes affected `0` | Broad root facade; defer |
| `get_indicator_registry` | UNKNOWN / ambiguous across two registry definitions | Defer until disambiguated |
| `get_lineage_tracker` | MEDIUM, impacted count `5`, direct `5`, processes affected `0` | Select for next decision gate |
| `get_postgres_connection` | MEDIUM, impacted count `6`, direct `5`, processes affected `0` | Control-plane route/OpenAPI ownership; defer |
| `get_cache_manager` | UNKNOWN / ambiguous across API dashboard and core cache manager definitions | Defer until disambiguated |

The sampled CLI impact reports had a stale-index warning. Use them as
candidate-shaping evidence only; refresh the GitNexus index before relying on
graph freshness for implementation authorization.

Staged verification before commit:

- MCP `detect_changes`: `Transport closed`
- CLI fallback: `ok=true`, `status=stale`, `risk_level=low`
- changed files: `9`
- changed symbols: `0`
- affected processes: `0`
- indexed commit: `13321ab73166afc0990b097503294a883842a941`
- current commit: `fcead56344110e33041319271c122e71d2b763a0`
- stale reason: `current_commit_differs_from_indexed_commit`

## Decision

G2.280 recommends:

`G2.281 no-source data_lineage get_lineage_tracker ownership / route-provider decision`

Rationale:

- `get_lineage_tracker` is the most bounded active API route helper candidate
  after `get_monitoring_db` closeout.
- It has `5` active bare calls in one active route module:
  `web/backend/app/api/data_lineage.py`.
- GitNexus CLI sampling found a non-ambiguous target with MEDIUM risk and `0`
  affected processes.
- It is a better next governance step than opening a broad root facade,
  registry, cache, or control-plane DB helper lane.

G2.281 should decide ownership and future route-provider strategy only. It must
not perform source implementation unless a later authorization package is
reviewed and accepted.

## Stale Policy

This report is stale if any of these change before review:

- current HEAD differs from
  `fcead56344110e33041319271c122e71d2b763a0`
- PR `#432` merge state or merge commit changes
- runtime route count or OpenAPI path count changes
- residual candidate scan output changes
