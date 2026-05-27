# Backend Strategy Adapter Provider Design

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Work item: G2.173
- State: ready for review
- Date: 2026-05-27
- Current HEAD: `b867716f77f8f509d1a7ec49c76346422bfd66ac`
- Parent PR: `#325` merged, `docs(governance): select strategy adapter residual track`
- Scope: design/authorization package for Strategy adapter/provider duplication

## Boundary

This package does not edit backend source, tests, route behavior, OpenAPI exposure, frontend code, PM2 workflows, OpenSpec content, config, scripts, compatibility surfaces, or issue labels.

This package selects the canonical adapter ownership and authorizes only a future narrow G2.174 implementation lane after review. No source implementation is performed here.

## Parent State

PR `#325` was merged into `wip/root-dirty-20260403` at:

```text
b867716f77f8f509d1a7ec49c76346422bfd66ac
```

The local evidence worktree and remote `wip/root-dirty-20260403` both pointed at that commit during collection.

## Current Shape

Two modules define a full `StrategyDataSourceAdapter` implementation:

| Path | Lines | Class | Role observed |
|---|---:|---|---|
| `web/backend/app/services/adapters/strategy_adapter.py` | 368 | `StrategyDataSourceAdapter` | Canonical implementation path through `app.services.adapters` and `app.services.data_adapter`. |
| `web/backend/app/services/data_adapters/strategy.py` | 367 | `StrategyDataSourceAdapter` | Legacy direct path with duplicate implementation. |

Both modules expose the same adapter class name and the same provider/helper shape:

- `_get_strategy_service`
- `_get_mock_manager`
- `_is_mock_mode`
- `_should_use_mock_fallback`
- `get_data`
- `_fetch_strategy_data`
- `_get_mock_strategy_data`
- `health_check`
- `get_metrics`

Both `_get_strategy_service` helpers call public `get_strategy_service()`.

## Canonical Ownership Decision

Canonical implementation path:

```text
web/backend/app/services/adapters/strategy_adapter.py
```

Reasons:

- `web/backend/app/services/data_adapter.py` is explicitly documented as a backward-compatible entrypoint and states that actual implementations were split into `app.services.adapters`.
- `web/backend/app/services/data_adapter.py` imports `StrategyDataSourceAdapter` from `app.services.adapters`.
- `web/backend/app/services/adapters/__init__.py` exports `StrategyDataSourceAdapter` from `.strategy_adapter`.
- `web/backend/app/services/data_source_factory/data_source_factory.py` imports `StrategyDataSourceAdapter` through `app.services.data_adapter`, which resolves to `app.services.adapters`.
- `web/backend/tests/test_logging_noise_regressions.py` imports the canonical `app.services.adapters.strategy_adapter` path.

Legacy compatibility path:

```text
web/backend/app/services/data_adapters/strategy.py
```

Reasons:

- It has no package-level export through `web/backend/app/services/data_adapters/__init__.py` because that file is absent.
- Production direct references to `app.services.data_adapters.strategy` were not found in the current scan.
- `web/backend/tests/test_adapter_mock_fallback_controls.py` still imports this path directly, so compatibility behavior must be preserved during migration.

## Reference Evidence

Current reference scan:

| Surface | Evidence |
|---|---|
| Factory path | `data_source_factory.py` imports `StrategyDataSourceAdapter` through `app.services.data_adapter`, which re-exports from `app.services.adapters`. |
| Canonical package export | `web/backend/app/services/adapters/__init__.py` exports `StrategyDataSourceAdapter`. |
| Legacy package export | `web/backend/app/services/data_adapters/__init__.py` is absent. |
| Canonical test | `test_logging_noise_regressions.py` imports `app.services.adapters.strategy_adapter`. |
| Legacy direct test | `test_adapter_mock_fallback_controls.py` imports `app.services.data_adapters.strategy`. |

## GitNexus Evidence

File-level impact:

| Target | Risk | Impacted count | Direct upstream |
|---|---|---:|---|
| `web/backend/app/services/adapters/strategy_adapter.py` | LOW | 2 | `web/backend/app/services/adapters/__init__.py` |
| `web/backend/app/services/data_adapters/strategy.py` | LOW | 0 | none |

Class context:

| Target | Context |
|---|---|
| `adapters/strategy_adapter.py::StrategyDataSourceAdapter` | Class found at `20-366`; no incoming class references in GitNexus; has `get_metrics` method edge. |
| `data_adapters/strategy.py::StrategyDataSourceAdapter` | Class found at `17-365`; no incoming class references in GitNexus; has `close` method edge. |

Helper context:

| Target | Incoming | Outgoing |
|---|---|---|
| `adapters/strategy_adapter.py::_get_strategy_service` | `_fetch_strategy_data`, `health_check` | `get_strategy_service` |
| `data_adapters/strategy.py::_get_strategy_service` | `_fetch_strategy_data`, `health_check` | `get_strategy_service` |

Broad public getter state:

- `get_strategy_service` remains CRITICAL from G2.172 evidence.
- Public getter retirement is not authorized here.

## Verification

Executed at current HEAD `b867716f77f8f509d1a7ec49c76346422bfd66ac`:

| Check | Result |
|---|---|
| Parent PR state | `#325` is `MERGED` |
| Adapter and logging focused tests | `16 passed in 4.24s` |
| Strategy route provider + backtest regressions | `8 passed in 5.43s` |
| OpenAPI smoke | `routes=548`, `paths=500`, `duplicate_operation_ids=0`, `duplicate_operation_id_warnings=0`, `total_warnings_captured=121` |

OpenAPI smoke used minimal non-secret placeholder environment values to satisfy the application import gate. This design package does not edit route or OpenAPI files.

## Authorization Decision

Authorize a future G2.174 source-capable implementation only after this design package is reviewed and accepted.

Future G2.174 allowed source/test scope:

| Path | Allowed future action |
|---|---|
| `web/backend/app/services/data_adapters/strategy.py` | Convert duplicate implementation into a thin compatibility wrapper that re-exports canonical `StrategyDataSourceAdapter` from `app.services.adapters.strategy_adapter`. |
| `web/backend/tests/test_adapter_mock_fallback_controls.py` | Add or update focused tests proving the legacy direct import resolves to the canonical class and existing fallback controls remain intact. |
| `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` | Record implementation and review state. |
| `.planning/codebase/generated/*strategy-adapter-provider*2026-05-27.json` | Record machine-readable evidence. |
| `docs/reports/quality/*strategy-adapter-provider*2026-05-27.md` | Record implementation or closeout evidence. |
| `governance/mainline/task-cards/pr-*.yaml` | Record mainline scope gate metadata. |

Future G2.174 required properties:

- Keep `app.services.adapters.strategy_adapter.StrategyDataSourceAdapter` as the canonical implementation.
- Preserve direct import compatibility for `app.services.data_adapters.strategy.StrategyDataSourceAdapter`.
- Do not edit `web/backend/app/services/adapters/strategy_adapter.py`.
- Do not edit `web/backend/app/services/data_adapter.py`.
- Do not edit `web/backend/app/services/data_source_factory/data_source_factory.py`.
- Do not edit Strategy route provider fallback.
- Do not edit `web/backend/app/tasks/backtest_tasks.py`.
- Do not delete or modify public `get_strategy_service()`.
- Use TDD red/green before source implementation.
- Run GitNexus impact before editing the authorized source symbol/file.
- Run staged GitNexus `detect_changes` before commit.

Expected future outcome:

- `web/backend/app/services/data_adapters/strategy.py` stops carrying a full duplicate implementation.
- Legacy direct import remains functional.
- Current adapter behavior remains covered by focused tests.
- Public Strategy service getter remains unchanged.

## Non-Goals

G2.174 must not:

- remove the canonical adapter implementation;
- edit `strategy_adapter.py`;
- edit factory registration;
- edit route provider fallback;
- reopen the backtest resolver seam;
- retire public `get_strategy_service()`;
- change route/API behavior, OpenAPI exposure, frontend, PM2, OpenSpec, config, scripts, or issue labels.

## Rollback

If this design/authorization package is rejected, revert only the G2.173 governance PR. That removes this report, generated JSON, task card, and steward-tree update. No runtime behavior is affected.

