# Backend Data-Quality Market Data Adapter Provider Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: review candidate
- Prepared at: `2026-05-28T17:41:53+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `ded789ee5d49d6ddcce5d8a69af1901a8481d1f0`
- Worktree branch: `g2-207-data-quality-market-data-adapter-provider-authorization`
- Scope: governance authorization package only
- Source edit authority: none

## Parent State

PR `#359` merged G2.206 at
`ded789ee5d49d6ddcce5d8a69af1901a8481d1f0`.

G2.206 classified `web/backend/app/services/market_data_adapter.py` as an
active data-source-factory compatibility facade and selected this G2.207
authorization package as the next gate.

## Current Target Evidence

| Item | Evidence |
|---|---|
| Target file | `web/backend/app/services/market_data_adapter.py` |
| File size | 481 lines |
| Existing constructor | `def __init__(self, config: Dict[str, Any])` at line 38 |
| Existing getter import | `from app.services.data_quality_monitor import get_data_quality_monitor` at line 10 |
| Existing getter call | `monitor = get_data_quality_monitor()` at line 327 |
| Direct app importer | `web/backend/app/services/data_source_factory/data_source_factory.py` |
| GitNexus upstream impact | LOW, impacted count `3`, direct `1`, processes affected `0` |

The direct app importer currently instantiates the adapter as
`MarketDataSourceAdapter(config.__dict__)`. Future implementation must preserve
that call form unless a later authorization explicitly grants factory source
edits.

## Authorization Decision

This PR authorizes a future G2.208 implementation lane, but does not implement
it.

| Future lane | Authorized source path | Authorized test paths |
|---|---|---|
| G2.208 data-quality `market_data_adapter.py` provider seam implementation | `web/backend/app/services/market_data_adapter.py` | `web/backend/tests/test_market_data_adapter_quality_monitor_provider.py`, `web/backend/tests/test_market_data_service_getter_retirement.py` |

Future implementation may also run consumer compatibility tests against
`web/backend/tests/_test_data_source_factory_management.py`, but this
authorization does not grant source edits under `web/backend/app/services/data_source_factory/**`.

## Authorized Future Shape

G2.208 may add a narrow quality-monitor provider seam with these constraints:

- Preserve the existing positional `config` argument.
- Add only keyword-only optional injection parameters, such as
  `quality_monitor` or a provider callable.
- Preserve default singleton fallback behavior when no injection is supplied.
- Make `_trigger_quality_monitoring` use the injected monitor/provider when
  provided.
- Keep `app.services.market_data_adapter` and `MarketDataSourceAdapter`
  import-compatible.
- Keep `data_source_factory` compatible with
  `MarketDataSourceAdapter(config.__dict__)`.

## Required Future Tests

G2.208 must use TDD:

| Phase | Required evidence |
|---|---|
| RED | A focused test fails before implementation because injected monitor/provider is not accepted or not used |
| GREEN | Focused tests pass after the provider seam is implemented |
| Regression | Existing market data service getter retirement and data-source-factory compatibility tests remain passing |

Required future check set:

- `web/backend/tests/test_market_data_adapter_quality_monitor_provider.py`
- `web/backend/tests/test_market_data_service_getter_retirement.py`
- `web/backend/tests/_test_data_source_factory_management.py`
- targeted ruff for the authorized source and test files
- OpenSpec strict validation for `migrate-backend-singletons-to-lifecycle-di`
- staged GitNexus change detection before commit

## Required Future GitNexus Gate

Before editing source in G2.208, run GitNexus impact for:

- `web/backend/app/services/market_data_adapter.py`
- `MarketDataSourceAdapter`

If either impact returns HIGH or CRITICAL risk, stop and return to review.

## Explicit Non-Goals

This authorization does not grant:

- source edits in G2.207
- source edits to `web/backend/app/services/data_source_factory/**`
- deletion of `market_data_adapter.py`
- thin-wrapper conversion of `market_data_adapter.py`
- singleton wrapper deletion or privatization
- `DataQualityMonitor` internals
- route or OpenAPI changes
- frontend changes
- OpenSpec proposal creation
- GitHub issue label changes

## Evidence Artifacts

| Artifact | Role |
|---|---|
| `.planning/codebase/generated/data-quality-market-data-adapter-ownership-decision-2026-05-28.json` | G2.206 ownership decision evidence |
| `docs/reports/quality/backend-data-quality-market-data-adapter-ownership-decision-2026-05-28.md` | G2.206 human-readable ownership decision |
| `.planning/codebase/generated/data-quality-market-data-adapter-provider-authorization-2026-05-28.json` | G2.207 machine-readable authorization package |
| `docs/reports/quality/backend-data-quality-market-data-adapter-provider-authorization-2026-05-28.md` | G2.207 human-readable authorization package |
| `governance/mainline/task-cards/pr-360.yaml` | G2.207 governance-only PR scope card |
