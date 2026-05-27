# Backend Data-Quality Adapter Split Constructor Provider Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: for review
- Prepared at: `2026-05-28T02:31:48+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD: `e30e16605df6aaa333989a7ac247bab3dcd0dd01`
- Worktree branch: `g2-195-data-quality-adapter-split-authorization`
- Parent: G2.194 data-quality adapter constructor seam design, PR `#347`
- Source edit authority in this package: none

Boundary note: this report authorizes a future implementation lane only after
review acceptance. It does not edit source, tests, OpenSpec changes, route
contracts, frontend files, PM2 workflows, or issue labels.

## Decision

G2.195 authorizes the next implementation lane shape, not the implementation
itself.

If this package is accepted, the next source lane should be:

`G2.196 data-quality adapter_split constructor provider implementation`

The future implementation may only introduce injectable data-quality monitor
construction for `adapter_split` classes. Runtime defaults must remain
compatible, and the global singleton path must remain available for callers that
do not inject a monitor.

## Current Evidence

G2.194 proved that `get_data_quality_monitor` remains cross-cutting and must
not be migrated in a single broad batch. G2.195 narrows the first source lane to
the `adapter_split` constructor seam.

| Evidence | Value |
|---|---:|
| `adapter_split` files in future source scope | 8 |
| constructors with a quality monitor parameter | 0 |
| `BaseAdapter` direct subclass extenders | 7 |
| `get_data_quality_monitor` impacted symbols | 24 |
| `get_data_quality_monitor` direct callers | 20 |
| `get_data_quality_monitor` affected processes | 7 |

GitNexus evidence at authorization time:

| Target | Risk | Meaning for G2.196 |
|---|---|---|
| `BaseAdapter` | MEDIUM | Future source lane must update all seven direct subclass extenders or prove they remain compatible |
| `get_data_quality_monitor` | CRITICAL | Future source lane may only reduce the `adapter_split` constructor calls; all other callers remain forbidden |

## Future Authorized Paths

If accepted, G2.196 may edit only these source files:

| Path | Future use |
|---|---|
| `web/backend/app/services/adapters_split/base_adapter.py` | Add injectable monitor/provider defaulting to current singleton behavior |
| `web/backend/app/services/adapters_split/baostock_adapter.py` | Pass injected monitor/provider through constructor |
| `web/backend/app/services/adapters_split/tushare_adapter.py` | Pass injected monitor/provider through constructor |
| `web/backend/app/services/adapters_split/customer_adapter.py` | Preserve `ws_url`; add injection as keyword-only |
| `web/backend/app/services/adapters_split/byapi_adapter.py` | Pass injected monitor/provider through constructor |
| `web/backend/app/services/adapters_split/akshare_adapter.py` | Pass injected monitor/provider through constructor |
| `web/backend/app/services/adapters_split/efinance_adapter.py` | Pass injected monitor/provider through constructor |
| `web/backend/app/services/adapters_split/tdx_adapter.py` | Pass injected monitor/provider through constructor |

Future authorized test path:

| Path | Future use |
|---|---|
| `web/backend/tests/test_adapter_split_data_quality_monitor_provider.py` | Focused regression tests for fake monitor injection, subclass pass-through, and default compatibility |

## Future Forbidden Paths

The future G2.196 source lane must not touch:

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

## Constructor Policy

Future G2.196 implementation should follow these constraints:

- `BaseAdapter` may accept an optional injected monitor or provider.
- The default path must keep current `get_data_quality_monitor()` behavior for
  callers that do not inject anything.
- Each `adapter_split` subclass may accept the same injection hook and pass it
  to `BaseAdapter`.
- Subclasses must not overwrite an injected monitor with a singleton result.
- `CustomerAdapter` must preserve existing `ws_url` compatibility; any injection
  parameter should be keyword-only.

This package intentionally does not choose exact Python type aliases or final
parameter names. G2.196 must choose them in source context and prove them through
tests.

## Test-Double Contract

Future G2.196 tests should use a fake monitor with these methods:

| Method | Required behavior |
|---|---|
| `check_data_quality(data, source_or_context)` | Synchronous; records calls and returns a truthy quality result |
| `evaluate_data_quality(...)` | Async; records calls and returns a truthy result for later runtime-monitoring lanes |

Required future assertions:

- `BaseAdapter` can use the fake monitor without calling the global getter.
- Each subclass can receive the fake monitor/provider through its constructor.
- Subclass constructors do not replace the injected monitor with a singleton.
- Default construction still works for existing runtime callers.

## Required Future Checks

Future G2.196 must run at least:

```bash
pytest -q -n 0 --tb=short --no-cov web/backend/tests/test_adapter_split_data_quality_monitor_provider.py
ruff check web/backend/app/services/adapters_split/base_adapter.py web/backend/app/services/adapters_split/baostock_adapter.py web/backend/app/services/adapters_split/tushare_adapter.py web/backend/app/services/adapters_split/customer_adapter.py web/backend/app/services/adapters_split/byapi_adapter.py web/backend/app/services/adapters_split/akshare_adapter.py web/backend/app/services/adapters_split/efinance_adapter.py web/backend/app/services/adapters_split/tdx_adapter.py web/backend/tests/test_adapter_split_data_quality_monitor_provider.py
openspec validate migrate-backend-singletons-to-lifecycle-di --strict
```

Before committing the future implementation, stage only the authorized paths and
run `gitnexus_detect_changes(scope=staged)`.

## Review Questions

- Is the future source scope narrow enough for one implementation PR?
- Does the package keep service adapters, legacy adapters, `market_data_adapter.py`,
  singleton wrappers, and `DataQualityMonitor` internals out of scope?
- Does the future test-double contract prove the constructor seam without
  relying on broad runtime behavior?
- Is G2.196 clearly an implementation lane that still needs separate review
  after this authorization package is accepted?

## Next Gate

If accepted, start G2.196 data-quality `adapter_split` constructor provider
implementation. Do not start source changes from G2.195 itself.
