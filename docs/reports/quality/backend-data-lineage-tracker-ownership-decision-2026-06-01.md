# Backend data_lineage get_lineage_tracker Ownership Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Gate: `G2.281`
- Status: for review
- Prepared at: `2026-06-01T01:56:44+08:00`
- Base HEAD checked: `1707284bceeef8992641290d86790c1699975f5a`
- Parent PR: `#433`
- Parent merge commit: `1707284bceeef8992641290d86790c1699975f5a`
- Source edit authority: no
- Autopilot status: stop at PR review gate

Boundary note: this report records an ownership and route-provider decision
only. It does not authorize backend source edits, test edits, route registration
changes, generated OpenAPI artifact edits, frontend/config/script edits,
OpenSpec changes, PM2 commands, or runtime state changes.

## Autopilot Stop Reason

The maintainer's limited-autopilot rule allows automatic merging only when
GitNexus risk remains low and no new affected symbols or processes appear.

For `get_lineage_tracker`, GitNexus CLI impact reports:

- risk: `MEDIUM`
- impacted count: `5`
- direct callers: `5`
- affected processes: `0`
- affected module: `Api`
- index status: stale warning

Staged verification for this governance-only PR reports:

- MCP `detect_changes`: `Transport closed`
- CLI fallback: `ok=true`, `status=stale`, `risk_level=low`
- changed files: `9`
- changed symbols: `0`
- affected processes: `0`
- indexed commit: `bf65ba60483469d5a973543a3ed3b421434ae1da`
- current commit: `1707284bceeef8992641290d86790c1699975f5a`

Because the risk is `MEDIUM`, this G2.281 PR must stop at human review. Codex
must not auto-merge this PR or start a follow-up source implementation lane.

## Parent State

PR `#433` merged G2.280 at
`1707284bceeef8992641290d86790c1699975f5a`.

G2.280 selected `get_lineage_tracker` as the next bounded no-source decision
target after the `get_monitoring_db` sequence closed.

## Surface Summary

Current owner surface:

- route module: `web/backend/app/api/data_lineage.py`
- helper: `get_lineage_tracker`
- definition line: `92`
- active direct calls: `5`
- active route handlers: `5`
- cross-module incoming calls: none found by GitNexus CLI context

Current helper behavior:

- creates an `asyncpg` raw connection from PostgreSQL settings
- creates `LineageStorage`
- creates `LineageTracker`
- returns `(tracker, connection_adapter)`

Active callers:

| Handler | Route | Method | Direct call line |
|---|---|---|---:|
| `record_lineage` | `/api/v1/lineage/record` | POST | 149 |
| `get_upstream_lineage` | `/api/v1/lineage/{node_id}/upstream` | GET | 226 |
| `get_downstream_lineage` | `/api/v1/lineage/{node_id}/downstream` | GET | 336 |
| `get_lineage_graph` | `/api/v1/lineage/graph` | POST | 424 |
| `analyze_impact` | `/api/v1/lineage/impact` | POST | 540 |

## Route / OpenAPI Smoke

Runtime/OpenAPI smoke with placeholder import-time environment values recorded:

- FastAPI routes: `548`
- OpenAPI paths: `500`
- duplicate operation IDs: `0`

Lineage paths present:

- `/api/v1/lineage/graph`
- `/api/v1/lineage/impact`
- `/api/v1/lineage/record`
- `/api/v1/lineage/{node_id}/downstream`
- `/api/v1/lineage/{node_id}/upstream`
- `/api/v1/governance/lineage/stats`

Known smoke log noise: app import emitted the existing mock backtest
`NotImplementedError` log. The smoke still completed and produced route/OpenAPI
counts.

## Decision

Classification:

`get_lineage_tracker` is a bounded active API route helper / provider candidate.

Ownership:

The current helper belongs to the `data_lineage.py` route module. It is not a
root service facade, not a registry surface, and not a route-registration or
OpenAPI exposure issue.

Recommended next gate:

`G2.282 no-source data_lineage get_lineage_tracker provider authorization package`

Important boundary:

G2.281 does not authorize source implementation. A future G2.282 may draft a
path-limited authorization package for a route-local provider/dependency seam,
but that authorization must be reviewed because the current GitNexus sampled
risk is `MEDIUM`.

## Stale Policy

This report is stale if any of these change before review:

- current HEAD differs from
  `1707284bceeef8992641290d86790c1699975f5a`
- PR `#433` merge state or merge commit changes
- runtime route count or OpenAPI path count changes
- `data_lineage.py` `get_lineage_tracker` call sites change
- GitNexus risk or affected symbol/process counts change
