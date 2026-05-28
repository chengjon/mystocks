# Backend Data-Quality Adapter Split Constructor Provider Implementation

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for review
- Prepared at: `2026-05-28T07:45:53+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `fabd674e8a748cdd2c51a80eebb5ad20b52bc737`
- Worktree branch: `g2-196-data-quality-adapter-split-implementation`
- Parent: G2.195 data-quality `adapter_split` constructor provider authorization, PR `#348`

Boundary note: this implementation uses the G2.195 authorized source lane only.
It does not edit service adapters, legacy adapters, `market_data_adapter.py`,
singleton wrappers, `DataQualityMonitor` internals, routes, frontend files,
OpenSpec changes, API contracts, config, or scripts.

## Change Summary

G2.196 implements the `adapter_split` constructor provider seam authorized by
G2.195.

The implementation:

- Adds optional `quality_monitor` injection to `BaseAdapter`.
- Preserves default singleton fallback in `BaseAdapter` for existing callers.
- Updates seven `adapter_split` subclasses to accept keyword-only
  `quality_monitor` and pass it through to `BaseAdapter`.
- Removes subclass-level `get_data_quality_monitor()` imports and assignments.
- Adds one focused regression test proving injected monitors bypass the global
  getter and are used by `_log_data_quality`.

Incidental fixes within authorized files:

- `tushare_adapter.py` imports `os` for existing `os.getenv` usage.
- `byapi_adapter.py` imports `os` for existing `os.getenv` usage.
- `tdx_adapter.py` logs `self.name` instead of undefined `TDX`.

## Implemented Paths

| Path | Change |
|---|---|
| `web/backend/app/services/adapters_split/base_adapter.py` | Optional injected `quality_monitor`, singleton fallback retained |
| `web/backend/app/services/adapters_split/baostock_adapter.py` | Keyword-only `quality_monitor` pass-through |
| `web/backend/app/services/adapters_split/tushare_adapter.py` | Keyword-only `quality_monitor` pass-through; `os` import |
| `web/backend/app/services/adapters_split/customer_adapter.py` | Preserves `ws_url`; keyword-only `quality_monitor` pass-through |
| `web/backend/app/services/adapters_split/byapi_adapter.py` | Keyword-only `quality_monitor` pass-through; `os` import |
| `web/backend/app/services/adapters_split/akshare_adapter.py` | Keyword-only `quality_monitor` pass-through |
| `web/backend/app/services/adapters_split/efinance_adapter.py` | Keyword-only `quality_monitor` pass-through |
| `web/backend/app/services/adapters_split/tdx_adapter.py` | Keyword-only `quality_monitor` pass-through; logger fix |
| `web/backend/tests/test_adapter_split_data_quality_monitor_provider.py` | Focused fake monitor constructor provider regression |

## Inventory Delta

| Item | Before G2.196 | After G2.196 |
|---|---:|---:|
| `adapter_split` subclass `get_data_quality_monitor()` calls | 7 | 0 |
| `adapter_split` subclass `get_data_quality_monitor` imports | 7 | 0 |
| `BaseAdapter` singleton fallback calls | 1 | 1 |
| Constructors accepting `quality_monitor` | 0 | 8 |
| Focused regression tests | 0 | 1 |

## TDD Evidence

Red test:

```bash
env PYTHONPATH=web/backend pytest -q -n 0 --tb=short --no-cov web/backend/tests/test_adapter_split_data_quality_monitor_provider.py
```

Expected failure observed:

```text
TypeError: BaostockAdapter.__init__() got an unexpected keyword argument 'quality_monitor'
```

Green test:

```bash
env PYTHONPATH=web/backend pytest -q -n 0 --tb=short --no-cov web/backend/tests/test_adapter_split_data_quality_monitor_provider.py
```

Result:

```text
1 passed
```

## Verification

| Check | Result |
|---|---|
| Focused pytest | `1 passed` |
| Ruff on eight adapter files plus focused test | `All checks passed` |
| Import smoke | Passed with minimal dummy required env; no service startup |
| `openspec validate migrate-backend-singletons-to-lifecycle-di --strict` | Valid; PostHog network flush noise only |
| `git diff --check` | Passed |
| Mainline scope gate | Passed after task-card schema alignment to `feature`, `domain-01`, `domain-01-node-03`, plus Function Tree catalog coverage for `adapters_split` |
| GitNexus staged detect changes | Low risk; 18 source/governance files checked before the catalog coverage amendment, 84 changed symbols, 0 affected processes |

## Preserved Boundaries

G2.196 does not touch:

- `web/backend/app/services/adapters/**`
- `web/backend/app/services/data_adapters/**`
- `web/backend/app/services/market_data_adapter.py`
- `web/backend/app/services/_data_quality_monitor_singleton.py`
- `web/backend/app/services/data_quality_monitor.py`
- `web/backend/app/api/**`
- `web/frontend/**`
- `src/**`
- `docs/api/**`
- `config/**`
- `scripts/**`
- `openspec/changes/**`
- `openspec/specs/**`

## Next Gate

If accepted, run G2.197 closeout / remaining candidate refresh before selecting
any further data-quality monitor migration lane.
