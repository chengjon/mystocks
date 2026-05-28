# Backend Data-Quality Residual Adapter Ownership Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Node: G2.198 data-quality residual adapter ownership decision
- Status: for review
- Prepared at: `2026-05-28T09:35:10+08:00`
- Base HEAD checked: `3acf90c3ab17dbb3b47150a03f1cdee1c96dc8f1`
- Parent PR: `#350`
- Parent merge commit: `3acf90c3ab17dbb3b47150a03f1cdee1c96dc8f1`
- Source edit authority: no

Boundary note: this report records an ownership decision only. It does not
authorize backend source changes, test changes, OpenSpec proposal creation,
route/OpenAPI changes, issue label changes, PM2 commands, or PR merges.

## Decision

G2.198 selects canonical service adapters as the next data-quality monitor
ownership target.

The next recommended gate is:

| Next gate | Type | Source authority | Purpose |
|---|---|---|---|
| G2.199 data-quality canonical service adapter provider authorization | authorization package | no in G2.199 itself | Define a future path-limited implementation lane for canonical service adapters |

G2.198 does not authorize implementation. If G2.199 is accepted, a later
implementation lane may be opened with explicit source paths and test scope.

## Candidate Facts

| Surface | Files | Getter calls | Getter imports | Current decision |
|---|---:|---:|---:|---|
| canonical service adapters | 2 | 2 | 2 | Select as next authorization target |
| legacy data adapters | 2 | 2 | 2 | Defer to compatibility ownership decision |
| `market_data_adapter.py` | 1 | 1 | 1 | Defer as root compatibility facade |
| singleton wrapper / canonical monitor | 2 | 2 or re-export | 1 | Retain backing API and canonical implementation |

Candidate file details:

| File | Class | Getter/import lines | Decision |
|---|---|---|---|
| `web/backend/app/services/adapters/dashboard_adapter.py` | `DashboardDataSourceAdapter` | import line 9, call line 253 | selected for future authorization |
| `web/backend/app/services/adapters/data_adapter.py` | `DataDataSourceAdapter` | import line 10, call line 622 | selected for future authorization |
| `web/backend/app/services/data_adapters/dashboard.py` | `DashboardDataSourceAdapter` | import line 10, call line 249 | defer; legacy compatibility surface |
| `web/backend/app/services/data_adapters/data_source.py` | `DataDataSourceAdapter` | import line 10, call line 608 | defer; legacy compatibility surface |
| `web/backend/app/services/market_data_adapter.py` | `MarketDataSourceAdapter` | import line 10, call line 327 | defer; root compatibility facade |
| `web/backend/app/services/_data_quality_monitor_singleton.py` | n/a | definition line 12, helper line 24 | retain backing singleton helper |
| `web/backend/app/services/data_quality_monitor.py` | `DataQualityMonitor` and rules | re-export line 714 | retain canonical implementation and public export |

Factory relationship:

| File | Evidence | Decision use |
|---|---|---|
| `web/backend/app/services/data_source_factory/data_source_factory.py` | imports `DashboardDataSourceAdapter` and `DataDataSourceAdapter` through `app.services.data_adapter`; constructs them at lines 116 and 119 | canonical service adapters are active through the compatibility facade and should be handled before legacy directory cleanup |
| `web/backend/app/services/data_source_factory/data_source_factory.py` | imports and constructs `MarketDataSourceAdapter` | `market_data_adapter.py` remains an active compatibility facade and needs separate ownership planning |

## Rationale

Canonical service adapters are the narrowest active residual surface after the
`adapter_split` closeout. They have exactly two getter calls, no constructor
`quality_monitor` parameter, and active factory reachability through the
`app.services.data_adapter` compatibility facade.

Legacy `data_adapters` modules have no direct module text consumers in the
current scan, but static non-use is not deletion authority. They may still carry
compatibility or historical import obligations and must remain deferred to a
separate compatibility decision.

`market_data_adapter.py` is larger, factory-constructed, and already belongs to a
compatibility facade / market-data ownership surface. It should not be bundled
with the canonical service adapter authorization.

The singleton wrapper and canonical monitor implementation are retained backing
APIs. This decision does not delete, rename, privatize, or move them.

## Future G2.199 Authorization Candidate

Likely future source paths:

- `web/backend/app/services/adapters/dashboard_adapter.py`
- `web/backend/app/services/adapters/data_adapter.py`

Likely future test surfaces:

- `tests/backend/test_data_adapter_regression.py`
- `web/backend/tests/test_logging_noise_regressions.py`

Future authorization must preserve:

- `app.services.data_adapter` compatibility facade behavior
- `data_source_factory` construction behavior
- async `_trigger_quality_monitoring(...)` behavior
- default runtime singleton fallback compatibility

## Preserved Boundaries

G2.198 does not touch:

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
| Parent PR state | `#350` is `MERGED` at `3acf90c3ab17dbb3b47150a03f1cdee1c96dc8f1` |
| Candidate scan | Residual files inspected for getter/import lines, constructors, factory relationships, and text consumers |
| Source edit scope | No backend source edits in this package |
| Next-gate classification | G2.199 authorization package; no direct source implementation from G2.198 |
| JSON parse | Passed for generated artifact and `steward-index.json` |
| Markdown governance | `errors=0`, `checked_files=6` |
| OpenSpec strict validate | `migrate-backend-singletons-to-lifecycle-di` valid |
| GitNexus staged detect changes | Low risk; 9 changed governance files, 0 changed symbols, 0 affected processes |
| Mainline scope gate | Passed |
