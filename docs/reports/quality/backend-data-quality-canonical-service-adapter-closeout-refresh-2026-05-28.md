# Backend Data-Quality Canonical Service Adapter Closeout / Refresh

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Node: G2.201 data-quality canonical service adapter closeout / refresh
- Status: closeout and residual refresh
- Prepared at: `2026-05-28T11:30:22+08:00`
- Base HEAD checked: `cbd9b3a7ee730c72a63dbc7adb6490564c12c71e`
- Parent implementation: G2.200, PR `#353`, merge commit `cbd9b3a7ee730c72a63dbc7adb6490564c12c71e`
- Source edit authority: no

Boundary note: this closeout records accepted implementation evidence and selects
the next decision gate. It does not authorize source edits, legacy adapter
migration, wrapper deletion, route changes, OpenAPI contract changes, frontend
changes, config/script changes, OpenSpec changes, or GitHub issue label changes.

## Closeout Result

G2.200 is closed as the canonical service adapter monitor-injection lane.

| Surface | Result |
|---|---|
| `DashboardDataSourceAdapter` | Accepts keyword-only `quality_monitor`; preserves positional `config` construction; falls back to `get_data_quality_monitor()` when no monitor is injected |
| `DataDataSourceAdapter` | Accepts keyword-only `quality_monitor`; preserves positional `config` construction; falls back to `get_data_quality_monitor()` when no monitor is injected |
| Focused provider tests | Prove injected monitors bypass the module-level global getter for both canonical adapters |
| Function-tree / mainline mapping | `domain-01-node-03` covers the two canonical service adapter paths and focused test path |

## Post-Merge Verification

| Check | Result |
|---|---|
| GitHub PR `#353` | `MERGED` at `cbd9b3a7ee730c72a63dbc7adb6490564c12c71e` |
| Focused regression package | `21 passed` |
| Import smoke | Passed with minimal dummy required env through `app.services.data_adapter` and `data_source_factory` |
| OpenSpec validation | `openspec validate migrate-backend-singletons-to-lifecycle-di --strict` passed; PostHog network flush warning is telemetry noise |
| JSON/YAML parse | Passed for generated closeout JSON, `steward-index.json`, and `pr-354.yaml` |
| Markdown governance | Passed, `checked_files=6`, `errors=0` |
| Diff whitespace | `git diff --check` passed |
| GitNexus staged scope | Low risk, `changed_files=9`, `changed_symbols=0`, `affected_processes=0` |
| Mainline scope gate | Passed, `changed_files=9`, `violations=0`, report `/tmp/pr354-mainline-governance-report.json` |

## Residual Scan

Command:

```bash
rg -n "get_data_quality_monitor\\(" web/backend/app/services web/backend/app/api -g '*.py'
```

At HEAD `cbd9b3a7ee730c72a63dbc7adb6490564c12c71e`, the scan finds 9 calls.

| Bucket | Files | Calls | Decision |
|---|---:|---:|---|
| Route provider backing | 1 | 1 | Retained provider backing getter from prior route provider lane |
| `adapter_split` base fallback | 1 | 1 | Closed adapter_split lane; retain default singleton fallback |
| Canonical service adapter fallback | 2 | 2 | Closed by G2.200; retain fallback for default construction |
| Legacy data adapters | 2 | 2 | Select as G2.202 compatibility ownership decision target; no source authority from G2.201 |
| `market_data_adapter.py` facade | 1 | 1 | Defer as root compatibility facade surface until an owner-specific decision package |
| Singleton wrapper / backing API | 1 | 2 | Retain backing API; not a deletion lane |

## GitNexus Reference

| Target | Risk | Impact |
|---|---|---|
| `web/backend/app/services/data_adapters/dashboard.py` | LOW | `impacted_count=0`, `processes_affected=0` |
| `web/backend/app/services/data_adapters/data_source.py` | LOW | `impacted_count=0`, `processes_affected=0` |
| `web/backend/app/services/market_data_adapter.py` | LOW | `impacted_count=3`, `direct=1`, `processes_affected=0` |
| `web/backend/app/services/_data_quality_monitor_singleton.py` | LOW | `impacted_count=19`, `direct=1`, `processes_affected=0` |

The two legacy data adapter files show no graph consumers in this index, but
static non-use is not deletion authority. They still need an explicit
compatibility ownership decision before source implementation, retirement, or
wrapper changes.

## Next Gate

Start G2.202 as a decision-only package:

| Future gate | Scope | Source authority |
|---|---|---|
| G2.202 data-quality legacy adapter compatibility ownership decision | Classify `web/backend/app/services/data_adapters/dashboard.py` and `web/backend/app/services/data_adapters/data_source.py`; decide whether to authorize a future implementation lane, retain as compatibility, or defer | No |

G2.202 must not batch `market_data_adapter.py`, singleton wrapper retirement,
route/provider changes, canonical service adapter edits, OpenAPI contracts,
frontend, config, scripts, or OpenSpec changes.
