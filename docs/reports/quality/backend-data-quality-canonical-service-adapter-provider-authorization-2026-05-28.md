# Backend Data-Quality Canonical Service Adapter Provider Authorization

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Node: G2.199 data-quality canonical service adapter provider authorization
- Status: for review
- Prepared at: `2026-05-28T10:14:06+08:00`
- Base HEAD checked: `a6b54ddfb24055552d634757f01dc03bd6ca6e62`
- Parent PR: `#351`
- Parent merge commit: `a6b54ddfb24055552d634757f01dc03bd6ca6e62`
- Source edit authority: no

Boundary note: this report is an authorization package for a future lane. It
does not authorize source changes in this PR, test changes in this PR, OpenSpec
proposal creation, route/OpenAPI changes, issue label changes, PM2 commands, or
PR merges.

## Authorization Decision

If G2.199 is accepted, it authorizes a later G2.200 implementation lane with a
narrow canonical service adapter provider scope.

| Future lane | Future source authority | Purpose |
|---|---|---|
| G2.200 data-quality canonical service adapter provider implementation | yes, only after G2.199 acceptance | Add injectable data-quality monitor construction for canonical service adapters while preserving default singleton compatibility |

Authorized future source paths:

| Path | Future role |
|---|---|
| `web/backend/app/services/adapters/dashboard_adapter.py` | Add injectable monitor/provider seam for `DashboardDataSourceAdapter` |
| `web/backend/app/services/adapters/data_adapter.py` | Add injectable monitor/provider seam for `DataDataSourceAdapter` |

Authorized future test paths:

| Path | Future role |
|---|---|
| `web/backend/tests/test_data_quality_canonical_service_adapter_provider.py` | New focused fake-monitor constructor/provider regression tests |
| `tests/backend/test_data_adapter_regression.py` | Existing adapter regression coverage if needed |
| `web/backend/tests/test_logging_noise_regressions.py` | Existing dashboard adapter logging/noise regression coverage if needed |

## Current Facts

| File | Class | Constructor now | Getter/import evidence |
|---|---|---|---|
| `web/backend/app/services/adapters/dashboard_adapter.py` | `DashboardDataSourceAdapter` | `def __init__(self, config: Dict[str, Any])` | import line 9, getter call line 253 |
| `web/backend/app/services/adapters/data_adapter.py` | `DataDataSourceAdapter` | `def __init__(self, config: Dict[str, Any])` | import line 10, getter call line 622 |

Factory relationship:

| File | Evidence | Future implementation constraint |
|---|---|---|
| `web/backend/app/services/data_source_factory/data_source_factory.py` | imports `DashboardDataSourceAdapter` and `DataDataSourceAdapter` through `app.services.data_adapter`; constructs them at lines 116 and 119 | Preserve construction through the compatibility facade and current config positional argument behavior |

GitNexus context notes:

| Target | Result | Decision use |
|---|---|---|
| `DashboardDataSourceAdapter` at `web/backend/app/services/adapters/dashboard_adapter.py` | exact-file context found; graph incoming refs empty | Text/factory evidence remains required for facade construction |
| `DataDataSourceAdapter` at `web/backend/app/services/adapters/data_adapter.py` | exact-file context found; graph incoming refs empty | Text/factory evidence remains required for facade construction |

## Future Implementation Shape

The future G2.200 implementation should:

- add an optional keyword-only `quality_monitor` argument to both canonical
  service adapter constructors
- preserve current `config` positional constructor compatibility
- store the injected monitor and use it in async `_trigger_quality_monitoring`
- avoid calling the global getter when a monitor is injected
- preserve default runtime behavior by falling back to `get_data_quality_monitor`
  when no monitor is injected
- preserve `app.services.data_adapter` compatibility facade behavior
- preserve `data_source_factory` construction behavior

## Future Forbidden Surfaces

G2.200 must not touch these surfaces unless a later authorization explicitly
expands scope:

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

## Future Required Checks

The future implementation lane should include:

- GitNexus impact/context before source edits on the exact target files or
  classes
- TDD red/green for injected monitor avoiding global getter calls
- focused pytest for
  `web/backend/tests/test_data_quality_canonical_service_adapter_provider.py`
- focused regression coverage for `tests/backend/test_data_adapter_regression.py`
  and `web/backend/tests/test_logging_noise_regressions.py` if touched
- ruff check on authorized source and test paths
- import smoke for canonical adapter constructors through `app.services.data_adapter`
  and `data_source_factory`
- `openspec validate migrate-backend-singletons-to-lifecycle-di --strict`
- `gitnexus_detect_changes(scope=staged)`

## Preserved Boundaries

G2.199 does not touch:

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
| Parent PR state | `#351` is `MERGED` at `a6b54ddfb24055552d634757f01dc03bd6ca6e62` |
| Candidate scan | Target files inspected for constructors, getter/import lines, factory relationship, and test surface existence |
| Source edit scope | No backend source edits in this package |
| Next-gate classification | G2.200 future implementation only after G2.199 acceptance |
| JSON parse | Passed for this authorization artifact and `steward-index.json` |
| Markdown governance | Passed, `checked_files=6`, `errors=0` |
| OpenSpec validation | `openspec validate migrate-backend-singletons-to-lifecycle-di --strict` passed |
| Diff whitespace | `git diff --check` passed |
| GitNexus staged scope | Low risk, `changed_files=9`, `changed_symbols=0`, `affected_processes=0` |
| Mainline scope gate | Passed, `changed_files=9`, `violations=0`, report `/tmp/pr352-mainline-governance-report.json` |
