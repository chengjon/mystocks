# Backend Data-Quality Market Data Adapter Ownership Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: review candidate
- Prepared at: `2026-05-28T17:17:56+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `44909f5d048700115da6a9eb9345957b8af3d077`
- Worktree branch: `g2-206-data-quality-market-data-adapter-ownership-decision`
- Scope: governance decision package only
- Source edit authority: none

## Parent State

PR `#358` merged G2.205 at
`44909f5d048700115da6a9eb9345957b8af3d077`.

G2.205 closed the two legacy data adapter wrapper targets and selected
`market_data_adapter.py` as the next owner-specific compatibility facade to
classify before singleton wrapper retirement can be considered.

## Target Facts

| Item | Current evidence |
|---|---|
| Target file | `web/backend/app/services/market_data_adapter.py` |
| File size | 481 lines |
| Local classes | `DataSourceMetrics`, `MarketDataSourceAdapter` |
| `get_data_quality_monitor` import | line 10 |
| `get_data_quality_monitor` call | line 327 inside `_trigger_quality_monitoring` |
| Direct app consumer | `web/backend/app/services/data_source_factory/data_source_factory.py` |
| GitNexus upstream impact | LOW, impacted count `3`, direct `1`, processes affected `0` |

Direct app references are limited to:

| File | Role |
|---|---|
| `web/backend/app/services/data_source_factory/data_source_factory.py:32` | Imports `MarketDataSourceAdapter` |
| `web/backend/app/services/data_source_factory/data_source_factory.py:113` | Instantiates `MarketDataSourceAdapter(config.__dict__)` |

Relevant test references already exist in:

- `web/backend/tests/_test_data_source_factory_support.py`
- `web/backend/tests/_test_data_source_factory_management.py`
- `web/backend/tests/test_market_data_service_getter_retirement.py`

## Decision

`market_data_adapter.py` is an active data-source-factory compatibility facade,
not a deletion candidate and not a simple thin-wrapper candidate.

| Question | Decision |
|---|---|
| Delete now? | No |
| Convert to thin wrapper now? | No |
| Open source implementation from this PR? | No |
| Next gate | G2.207 data-quality `market_data_adapter.py` provider seam authorization |
| Future implementation shape candidate | Preserve `MarketDataSourceAdapter` and the module path; authorize a narrow optional quality monitor/provider seam that defaults to current singleton behavior |

## Recommended G2.207 Authorization Shape

G2.207 should be an authorization package, not an implementation PR.

Recommended future source candidate:

| Path | Candidate role |
|---|---|
| `web/backend/app/services/market_data_adapter.py` | Add optional injected quality monitor/provider seam while preserving default construction |

Recommended future tests:

| Path | Candidate role |
|---|---|
| `web/backend/tests/test_market_data_adapter_quality_monitor_provider.py` | Prove injected monitor bypasses the module-level getter for market data adapter quality monitoring |
| `web/backend/tests/test_market_data_service_getter_retirement.py` | Preserve existing compatibility expectations |

The direct app consumer
`web/backend/app/services/data_source_factory/data_source_factory.py` must remain
compatible. It should be tested in the future lane, but source edits to
`data_source_factory` should remain forbidden unless the G2.207 authorization
explicitly grants them.

## Explicit Non-Goals

This decision does not authorize:

- backend source edits
- deletion of `market_data_adapter.py`
- conversion of `market_data_adapter.py` to a thin wrapper
- source edits to `data_source_factory`
- singleton wrapper deletion or privatization
- `DataQualityMonitor` internals
- route or OpenAPI changes
- frontend changes
- OpenSpec proposal creation
- GitHub issue label changes

## Residual Position

| Surface | Current handling after G2.206 |
|---|---|
| Legacy data adapter wrappers | Closed by G2.204/G2.205 |
| `market_data_adapter.py` facade | Selected for G2.207 authorization |
| Singleton wrapper / backing API | Retain until market adapter facade and remaining fallback surfaces have accepted closeout evidence |

## Evidence Artifacts

| Artifact | Role |
|---|---|
| `.planning/codebase/generated/data-quality-legacy-adapter-compatibility-wrapper-closeout-refresh-2026-05-28.json` | G2.205 closeout / residual refresh evidence |
| `docs/reports/quality/backend-data-quality-legacy-adapter-compatibility-wrapper-closeout-refresh-2026-05-28.md` | G2.205 human-readable closeout / residual refresh |
| `.planning/codebase/generated/data-quality-market-data-adapter-ownership-decision-2026-05-28.json` | G2.206 machine-readable decision evidence |
| `docs/reports/quality/backend-data-quality-market-data-adapter-ownership-decision-2026-05-28.md` | G2.206 human-readable decision report |
| `governance/mainline/task-cards/pr-359.yaml` | G2.206 governance-only PR scope card |
