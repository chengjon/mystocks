> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Lane: G2.210 data-quality monitor residual ownership decision
- Prepared at: `2026-05-28T20:48:36+08:00`
- Base branch: `wip/root-dirty-20260403`
- Base HEAD checked: `33b6ace2f68e23bcf07a12f53511d1f7b9fb8230`
- Parent lane: G2.209 data-quality `market_data_adapter.py` provider seam closeout / residual refresh
- Parent PR: `#362`
- Parent merge commit: `33b6ace2f68e23bcf07a12f53511d1f7b9fb8230`
- Source edit authority: none

Boundary note: this report records ownership classification and next-gate
requirements only. It does not authorize backend source edits, getter deletion,
route/OpenAPI changes, frontend changes, OpenSpec edits, issue label changes,
PM2 commands, or PR merges.

## Decision

G2.210 classifies the remaining data-quality monitor residuals as a high-risk
root ownership surface, not as another routine adapter or service implementation
lane.

The current root is `get_data_quality_monitor()` in
`web/backend/app/services/_data_quality_monitor_singleton.py`. GitNexus reports
CRITICAL upstream impact for that symbol: 24 impacted symbols, 20 direct
dependents, 7 affected execution flows, and 4 affected modules.

Because of that blast radius, the next action is G2.211, a dedicated
singleton/backing API authorization package. G2.210 must not open a source
implementation lane by itself.

## Current Residual Scan

Scan command intent: count `get_data_quality_monitor|DataQualityMonitor` in
`web/backend/app/services` and `web/backend/tests` at HEAD
`33b6ace2f68e23bcf07a12f53511d1f7b9fb8230`.

| Scope | Files | Hits |
|---|---:|---:|
| Service residuals | 7 | 21 |
| Test references | 7 | 17 |

Service classification:

| Surface | Matches | Classification | G2.210 handling |
|---|---:|---|---|
| `web/backend/app/services/market_data_adapter.py` | 2 | Closed market-data adapter fallback | Preserve closed status from G2.208/G2.209 |
| `web/backend/app/services/adapters/dashboard_adapter.py` | 2 | Closed canonical service adapter fallback | Preserve closed status from G2.200/G2.201 |
| `web/backend/app/services/adapters/data_adapter.py` | 2 | Closed canonical service adapter fallback | Preserve closed status from G2.200/G2.201 |
| `web/backend/app/services/adapters_split/base_adapter.py` | 2 | Closed adapter-split fallback | Preserve closed status from G2.196/G2.197 |
| `web/backend/app/services/data_quality_monitor.py` | 4 | Public singleton facade | Requires G2.211 authorization decision |
| `web/backend/app/services/_data_quality_monitor_singleton.py` | 6 | Singleton backing API | Requires G2.211 authorization decision |
| `web/backend/app/services/data_adapter.py.backup.20260130` | 3 | Historical backup | Separate repository hygiene authority required |

The test files are evidence of compatibility coverage, not source authority:

- `web/backend/tests/test_adapter_split_data_quality_monitor_provider.py`
- `web/backend/tests/test_data_quality_canonical_service_adapter_provider.py`
- `web/backend/tests/test_data_quality_legacy_data_adapter_compat.py`
- `web/backend/tests/test_data_quality_route_provider_regressions.py`
- `web/backend/tests/test_large_file_split_regressions.py`
- `web/backend/tests/test_logging_noise_regressions.py`
- `web/backend/tests/test_market_data_adapter_quality_monitor_provider.py`

## GitNexus Impact

GitNexus command:

```bash
gitnexus impact get_data_quality_monitor --direction upstream --include-tests --max-depth 2
```

Recorded result:

| Field | Value |
|---|---:|
| Target | `Function:web/backend/app/services/_data_quality_monitor_singleton.py:get_data_quality_monitor` |
| Risk | CRITICAL |
| Impacted count | 24 |
| Direct dependents | 20 |
| Affected processes | 7 |
| Affected modules | 4 |

Affected module groups: `Services`, `Data_adapters`, `Api`, and `Adapters`.

The d=1 dependents include data-quality route handlers, canonical service
adapters, adapter-split constructors, the market-data adapter trigger, and
`monitor_data_quality()`. This confirms that direct deletion or migration of the
singleton helper is a cross-module ownership decision.

## Ownership Outcome

| Ownership surface | Decision |
|---|---|
| Closed `market_data_adapter.py` fallback | Do not reopen without contradictory current HEAD evidence |
| Closed canonical service adapter fallbacks | Do not reopen without contradictory current HEAD evidence |
| Closed `adapter_split` fallback | Do not reopen without contradictory current HEAD evidence |
| `data_quality_monitor.py` public facade | Route into G2.211 authorization package |
| `_data_quality_monitor_singleton.py` backing API | Route into G2.211 authorization package |
| Historical backup file | Keep outside service lifecycle DI; handle only through repository hygiene authority |

## Next Gate

Start G2.211 data-quality monitor singleton/backing API authorization package
only after this decision package is accepted.

G2.211 should remain governance-only until it explicitly defines:

- consumer matrix for data-quality route callers, service adapters,
  adapter-split constructors, and `monitor_data_quality()`
- public facade versus private singleton helper ownership
- allowed source paths and focused test paths for any later implementation
- rollback plan preserving route/API behavior and default fallback compatibility
- stop rule if GitNexus still reports HIGH or CRITICAL risk after scoping

## Non-Goals

- Do not edit `web/backend/**` in G2.210.
- Do not delete or rename `get_data_quality_monitor()`.
- Do not reopen closed G2.196/G2.197, G2.200/G2.201, or G2.208/G2.209 source
  lanes from this report.
- Do not treat `data_adapter.py.backup.20260130` cleanup as service lifecycle
  DI implementation authority.

## Verification Plan

This package should be accepted only if:

- JSON/YAML parse succeeds for the generated evidence and task card.
- Markdown governance passes for this report and updated steward tree files.
- OpenSpec validation passes for `migrate-backend-singletons-to-lifecycle-di`.
- `git diff --check` and cached diff checks pass.
- Mainline scope gate confirms only the listed governance paths changed.
- GitNexus staged change detection reports no unexpected source impact.
