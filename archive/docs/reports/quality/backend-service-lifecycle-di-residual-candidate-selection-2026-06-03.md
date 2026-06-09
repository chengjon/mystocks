# Backend Service Lifecycle DI Residual Candidate Selection

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Summary

- Node: `G2.324 service lifecycle DI residual candidate selection`
- Type: no-source residual candidate selection
- Prepared at: `2026-06-03T17:11:52+08:00`
- Current workspace HEAD checked: `33e8af754c815a1c1c3e1e49a7d5453881534cca`
- Accepted PR anchor: PR `#474` merged at `2026-06-02T16:23:25Z`, merge commit `2ebff6d7ded33403c691a60fc43f87dabf90a975`

## Parent State

| Node | State | Evidence |
|---|---|---|
| `G2.321 watchlist DataSourceFactory provider implementation` | accepted/merged | PR `#474` merge commit `2ebff6d7ded33403c691a60fc43f87dabf90a975` |
| `G2.322 watchlist DataSourceFactory provider closeout / residual refresh` | accepted_merged | Residual observations retained in generated evidence/report refs |
| `G2.323 watchlist DataSourceFactory provider steward surface compaction` | accepted_merged | Current steward surfaces compacted and baseline frozen |
| `G2.324 service lifecycle DI residual candidate selection` | accepted_merged | This no-source selection report |

## Candidate Inputs

Accepted G2.322 evidence recorded these remaining observations:

| Candidate | DataSourceFactory calls | get_data_source observations | Handling |
|---|---:|---:|---|
| `web/backend/app/api/dashboard_data_source.py` | 0 | 3 | Not selected; accepted evidence records observations without DataSourceFactory construction |
| `web/backend/app/api/technical_analysis.py` | 8 | 8 | Selected; largest active route-body residual candidate |
| `web/backend/app/api/watchlist.py` | 1 | 1 | Not selected; retained provider backing, not route-body residual |

## Decision

G2.324 selects `web/backend/app/api/technical_analysis.py` as the next no-source ownership-decision candidate.

Next gate:

`G2.325 technical_analysis DataSourceFactory ownership decision / no-source`

This does not authorize implementation. A future source lane still requires a separate no-source authorization package and human review before merge.

## Boundaries

Forbidden surfaces:

- `web/`
- `src/`
- `tests/`
- `docs/api/`
- `config/`
- `scripts/`
- `openspec/`
- PM2 or runtime state

## Verification Notes

- This report is governance-only. It does not replace runtime route/OpenAPI validation.
- No source implementation is authorized by G2.324.
- Existing dirty worktree artifacts outside this G2.324 scope are not accepted by this node.
