# Backend Data-Quality Monitor Closeout Refresh

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Node: G2.197 data-quality monitor closeout / remaining candidate refresh
- Status: for review
- Prepared at: `2026-05-28T09:14:57+08:00`
- Base HEAD checked: `e4245ebe54c5ad6d2aebf4802d165d59700c9eeb`
- Parent PR: `#349`
- Parent merge commit: `e4245ebe54c5ad6d2aebf4802d165d59700c9eeb`
- Source edit authority: no

Boundary note: this report records closeout and next-gate classification only. It
does not authorize backend source changes, test changes, OpenSpec proposal
creation, route/OpenAPI changes, issue label changes, PM2 commands, or PR merges.

## Parent Closeout

PR `#349` merged G2.196 and closed the authorized `adapter_split` constructor
provider implementation lane.

| Item | Current result |
|---|---:|
| `adapter_split` subclass `get_data_quality_monitor()` calls | 0 |
| `adapter_split` subclass `get_data_quality_monitor` imports | 0 |
| `BaseAdapter` fallback `get_data_quality_monitor()` calls | 1 |
| Constructors accepting `quality_monitor` | 8 |
| Focused regression test | 1 passed in G2.196 |

The remaining `BaseAdapter` fallback is intentional compatibility behavior. It is
not counted as a subclass migration residual and must not be deleted by this
closeout package.

## Current Residual Inventory

At HEAD `e4245ebe54c5ad6d2aebf4802d165d59700c9eeb`, the refresh scanned
`web/backend/app/services/**/*.py`.

| Bucket | Files | Getter calls | Getter imports | Current decision |
|---|---:|---:|---:|---|
| `adapter_split` | 8 | 1 | 1 | Closed; only `BaseAdapter` compatibility fallback remains |
| service adapters | 2 | 2 | 2 | Defer to residual adapter ownership decision |
| legacy data adapters | 2 | 2 | 2 | Defer to legacy compatibility decision |
| `market_data_adapter.py` compatibility facade | 1 | 1 | 1 | Defer as root compatibility facade surface |
| singleton wrapper / canonical monitor | 2 | 2 | 1 | Retain backing API and canonical implementation; not a deletion lane |

Residual candidate paths:

| Bucket | Paths |
|---|---|
| service adapters | `web/backend/app/services/adapters/dashboard_adapter.py`, `web/backend/app/services/adapters/data_adapter.py` |
| legacy data adapters | `web/backend/app/services/data_adapters/dashboard.py`, `web/backend/app/services/data_adapters/data_source.py` |
| compatibility facade | `web/backend/app/services/market_data_adapter.py` |
| retained wrapper / implementation | `web/backend/app/services/_data_quality_monitor_singleton.py`, `web/backend/app/services/data_quality_monitor.py` |

## Decision

G2.197 closes the `adapter_split` subclass constructor provider lane and refreshes
the remaining data-quality monitor surfaces. It does not choose another source
implementation lane.

The next recommended gate is:

| Next gate | Type | Source authority | Purpose |
|---|---|---|---|
| G2.198 data-quality residual adapter ownership decision | decision package | no | Decide whether the next lane should target service adapters, legacy data adapters, `market_data_adapter.py`, or wrapper retention |

G2.198 should remain decision-only unless a later authorization packet explicitly
selects a path-limited implementation lane.

## Preserved Boundaries

G2.197 does not touch:

- `web/backend/**`
- `web/frontend/**`
- `src/**`
- `tests/**`
- `config/**`
- `scripts/**`
- `openspec/changes/**`
- `openspec/specs/**`

## Verification

| Check | Result |
|---|---|
| Parent PR state | `#349` is `MERGED` at `e4245ebe54c5ad6d2aebf4802d165d59700c9eeb` |
| Residual scan | `152` service Python files scanned; `15` files contain monitor refs |
| Source edit scope | No backend source edits in this package |
| Next-gate classification | G2.198 decision-only residual adapter ownership package |
| JSON parse | Passed for generated artifact and `steward-index.json` |
| Markdown governance | `errors=0`, `checked_files=6` |
| OpenSpec strict validate | `migrate-backend-singletons-to-lifecycle-di` valid |
| GitNexus staged detect changes | Low risk; 9 changed governance files, 0 changed symbols, 0 affected processes |
| Mainline scope gate | Passed after task-card required governance metadata was added |
