# Backend Data Quality Adapter Seam Design Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: governance design decision review candidate
- Prepared at: `2026-05-28T02:10:15+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `ea659d52903a5e9884d396069526ea08f15109a6`
- Worktree branch: `g2-194-data-quality-adapter-seam-design`
- Scope: data-quality adapter constructor seam design / test-double decision
- Source edit authority: none

Boundary note: this package selects the next governance gate. It does not
authorize adapter constructor implementation, legacy adapter edits, singleton
wrapper deletion, `DataQualityMonitor` internals, frontend edits, `src` edits,
`docs/api` edits, or OpenSpec change/spec edits.

## Parent State

| Item | State | Evidence |
|---|---|---|
| G2.193 data-quality route provider closeout / refresh | Merged | PR `#346`, merge commit `ea659d52903a5e9884d396069526ea08f15109a6` |
| G2.194 data-quality adapter seam design | For review | This report plus `.planning/codebase/generated/data-quality-adapter-seam-design-decision-2026-05-28.json` |

## Current Inventory

At HEAD `ea659d52903a5e9884d396069526ea08f15109a6`, the remaining data-quality
monitor surface is no longer a route-body migration. It is an adapter and
compatibility seam.

| Metric | Count |
|---|---:|
| Files scanned | 14 |
| `get_data_quality_monitor()` calls | 15 |
| `monitor_data_quality()` calls | 1 |
| `__init__` definitions in scanned files | 15 |
| Constructors already accepting a quality monitor parameter | 0 |

Quality monitor methods used by the remaining surfaces:

- `check_data_quality`
- `evaluate_data_quality`

Existing test files that already touch related adapter names:

- `web/backend/tests/test_logging_noise_regressions.py`
- `web/backend/tests/_test_data_source_factory_management.py`
- `web/backend/tests/_test_data_source_factory_support.py`
- `web/backend/tests/test_market_data_service_getter_retirement.py`
- `tests/backend/test_data_adapter_regression.py`

## Surface Classification

| Surface | Files | Getter calls | Current shape | Decision |
|---|---:|---:|---|---|
| `adapters_split` constructor surface | 8 | 8 | `BaseAdapter` plus seven subclasses call `get_data_quality_monitor()` during `__init__` | Select as next governance target |
| service adapter runtime monitoring | 2 | 2 | config constructors plus async `_trigger_quality_monitoring()` runtime getter | Defer until `adapters_split` pattern is proven |
| legacy adapter runtime monitoring | 2 | 2 | compatibility package with async `_trigger_quality_monitoring()` runtime getter | Defer to compatibility ownership decision |
| `market_data_adapter.py` compatibility surface | 1 | 1 | market-data adapter runtime monitoring getter | Defer to market-data compatibility decision |
| singleton wrapper / backing API | 1 | 2 + 1 helper | retained `get_data_quality_monitor` / `monitor_data_quality` backing API | Retain; not a deletion candidate |

The `adapters_split` target is cohesive because all eight files share the same
constructor-time dependency pattern:

- `web/backend/app/services/adapters_split/base_adapter.py`
- `web/backend/app/services/adapters_split/baostock_adapter.py`
- `web/backend/app/services/adapters_split/tushare_adapter.py`
- `web/backend/app/services/adapters_split/customer_adapter.py`
- `web/backend/app/services/adapters_split/byapi_adapter.py`
- `web/backend/app/services/adapters_split/akshare_adapter.py`
- `web/backend/app/services/adapters_split/efinance_adapter.py`
- `web/backend/app/services/adapters_split/tdx_adapter.py`

## GitNexus Evidence

| Target | Risk | Summary |
|---|---|---|
| `get_data_quality_monitor` | CRITICAL | 24 impacted symbols, 20 direct callers, 7 affected processes, 4 affected modules |
| `BaseAdapter` | MEDIUM | 7 impacted subclasses, 0 affected processes |

The `get_data_quality_monitor` risk remains cross-cutting. G2.194 therefore
does not authorize source edits. It only selects the next authorization package.

## Design Decision

G2.194 selects:

`G2.195 data-quality adapter_split constructor provider authorization package`

G2.195 should authorize, but still not implement, a future implementation lane
for the `adapters_split` constructor seam. The likely future implementation lane
should be G2.196 after G2.195 acceptance.

The future authorization candidate should be limited to:

- `web/backend/app/services/adapters_split/base_adapter.py`
- `web/backend/app/services/adapters_split/baostock_adapter.py`
- `web/backend/app/services/adapters_split/tushare_adapter.py`
- `web/backend/app/services/adapters_split/customer_adapter.py`
- `web/backend/app/services/adapters_split/byapi_adapter.py`
- `web/backend/app/services/adapters_split/akshare_adapter.py`
- `web/backend/app/services/adapters_split/efinance_adapter.py`
- `web/backend/app/services/adapters_split/tdx_adapter.py`
- focused adapter constructor/provider tests
- G2.195/G2.196 governance evidence

The future authorization candidate must continue to forbid:

- `web/backend/app/services/adapters/**`
- `web/backend/app/services/data_adapters/**`
- `web/backend/app/services/market_data_adapter.py`
- `web/backend/app/services/_data_quality_monitor_singleton.py`
- `web/backend/app/services/data_quality_monitor.py`
- frontend, `src`, `docs/api`, config, scripts, and OpenSpec change/spec edits

## Test-Double Contract

Future implementation should define focused test evidence around a fake monitor
contract before changing adapter constructors.

Proposed fake:

- `FakeDataQualityMonitor.check_data_quality(data, source_or_context)` records
  calls and returns a truthy `{"is_valid": True}` style result.
- `FakeDataQualityMonitor.evaluate_data_quality(...)` is async, records calls,
  and returns a truthy result for later runtime-monitoring tracks.

Future implementation must prove:

- adapter constructors can receive the fake monitor or provider without calling
  the global getter
- `BaseAdapter._log_data_quality` uses the injected monitor
- subclass constructors do not overwrite the injected monitor with the singleton
- default constructor behavior still preserves current runtime behavior

## Explicit Non-Goals

- No backend source edits.
- No test edits.
- No adapter constructor implementation.
- No legacy adapter compatibility edits.
- No singleton wrapper deletion.
- No `DataQualityMonitor` implementation rewrite.
- No frontend edits.
- No `src` edits.
- No `docs/api` edits.
- No OpenSpec change/spec edits.

## Next Gate

If accepted, start:

`G2.195 data-quality adapter_split constructor provider authorization package`

Do not implement adapter changes from G2.194.

## Evidence Artifacts

| Artifact | Role |
|---|---|
| `.planning/codebase/generated/data-quality-route-provider-closeout-refresh-2026-05-28.json` | G2.193 closeout / refresh evidence |
| `docs/reports/quality/backend-data-quality-route-provider-closeout-refresh-2026-05-28.md` | G2.193 closeout / refresh report |
| `.planning/codebase/generated/data-quality-adapter-seam-design-decision-2026-05-28.json` | G2.194 machine-readable design decision evidence |
| `docs/reports/quality/backend-data-quality-adapter-seam-design-decision-2026-05-28.md` | G2.194 design decision report |
| `governance/mainline/task-cards/pr-347.yaml` | G2.194 governance PR scope card |
