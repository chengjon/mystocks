# Backend Data-Quality Monitor Singleton Closeout / Residual Refresh - 2026-05-28

> **历史文档说明**: 本文件是 G2.213 执行证据快照，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Lane: G2.213 data-quality monitor singleton/backing API closeout / residual refresh
- Parent implementation: G2.212, PR `#365`
- Parent merge commit: `e7d9fe63285181f0227661628272487dc63d4e2c`
- OpenSpec change: `migrate-backend-singletons-to-lifecycle-di`
- Source authority: none
- Result: ready for review

## Purpose

G2.213 does not edit backend source. It closes the G2.212 implementation lane by:

- recording that PR `#365` was accepted
- refreshing active `get_data_quality_monitor` residuals at current HEAD
- classifying every remaining residual into retained or previously closed buckets
- deciding whether another data-quality monitor source lane is warranted

## Residual Scan

Scope:

- `web/backend/app/**/*.py`

Term:

- `get_data_quality_monitor`

Current HEAD:

- `e7d9fe63285181f0227661628272487dc63d4e2c`

Summary:

| Metric | Count |
|---|---:|
| Active files | 7 |
| Active occurrences | 29 |
| Active calls | 7 |

## Residual Classification

| Bucket | Files | Disposition |
|---|---:|---|
| Singleton/backing API seam | 2 | Closed by G2.212; retain provider/reset seam and default singleton fallback |
| Route API provider surface | 1 | Retained active FastAPI dependency/provider surface; not a direct implementation candidate in this lane |
| Closed canonical service adapter fallbacks | 2 | Closed by G2.200/G2.201; retain default fallback unless fresh current-HEAD evidence contradicts |
| Closed `market_data_adapter.py` facade fallback | 1 | Closed by G2.208/G2.209; retain compatibility facade fallback unless fresh current-HEAD evidence contradicts |
| Closed `adapter_split` base fallback | 1 | Closed by G2.196/G2.197; retain `BaseAdapter` fallback unless fresh current-HEAD evidence contradicts |

File-level evidence:

| Path | Occurrences | Calls | Imports | Classification |
|---|---:|---:|---:|---|
| `web/backend/app/services/_data_quality_monitor_singleton.py` | 2 | 2 | 0 | Singleton/backing API seam |
| `web/backend/app/services/data_quality_monitor.py` | 2 | 0 | 0 | Singleton/backing API facade exports |
| `web/backend/app/api/data_quality.py` | 17 | 1 | 1 | Route API provider surface |
| `web/backend/app/services/adapters/dashboard_adapter.py` | 2 | 1 | 1 | Closed canonical service adapter fallback |
| `web/backend/app/services/adapters/data_adapter.py` | 2 | 1 | 1 | Closed canonical service adapter fallback |
| `web/backend/app/services/market_data_adapter.py` | 2 | 1 | 1 | Closed market data adapter facade fallback |
| `web/backend/app/services/adapters_split/base_adapter.py` | 2 | 1 | 1 | Closed adapter split base fallback |

## Decision

No new data-quality monitor source lane is selected from this refresh.

Reason:

- the singleton/backing API surface now has the G2.212 provider/reset seam
- route API provider residuals remain active route contract surfaces and should stay under route/provider governance
- canonical service adapter fallbacks, `market_data_adapter.py`, and `adapter_split` base fallback were already closed by prior accepted lanes

The data-quality monitor conveyor should be treated as closed after PR `#366` review unless fresh current-HEAD evidence contradicts the accepted G2.196/G2.197, G2.200/G2.201, G2.208/G2.209, or G2.212 evidence.

## Verification Results

Because G2.213 is no-source, verification focuses on current HEAD consistency.

Focused provider seam regression:

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_quality_monitor_singleton_provider.py -q --no-cov --tb=short
```

Result:

- `3 passed`

Authorized non-large regression:

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_data_quality_monitor_singleton_provider.py web/backend/tests/test_data_quality_route_provider_regressions.py web/backend/tests/test_data_quality_canonical_service_adapter_provider.py web/backend/tests/test_adapter_split_data_quality_monitor_provider.py web/backend/tests/test_market_data_adapter_quality_monitor_provider.py web/backend/tests/test_logging_noise_regressions.py -q --no-cov --tb=short
```

Result:

- `20 passed`

OpenSpec:

```bash
openspec validate migrate-backend-singletons-to-lifecycle-di --strict
```

Result:

- `Change 'migrate-backend-singletons-to-lifecycle-di' is valid`
- PostHog connection refusal is telemetry noise only.

Governance checks:

- JSON/YAML parse: passed
- Markdown governance: `errors: 0`
- `git diff --check`: passed

## Next Gate

If PR `#366` is accepted, start G2.214 as a no-source non-strategy provider governance queue refresh / next-candidate selection.

G2.214 should not open a source lane directly. It should first decide whether any remaining non-strategy provider candidate is eligible for an authorization package.
