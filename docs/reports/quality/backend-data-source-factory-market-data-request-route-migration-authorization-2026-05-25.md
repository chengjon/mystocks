# Backend DataSourceFactory Market Data Request Route Migration Authorization - 2026-05-25

Workline: G2.70 candidate authorization packet

Current HEAD: `2670dba0661d9744372e834035027ac4de106fd0`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This document records a candidate-selection decision and its
evidence. It does not authorize backend source edits, route path changes,
OpenAPI exposure changes, response shape changes, frontend edits, PM2/runtime
operations, OpenSpec proposal publication, issue-label changes, compatibility
getter deletion, or migration of any DataSourceFactory consumer in this branch.

## Status

Ready for review.

This packet compares the remaining direct route/API `get_data_source_factory()`
consumers after G2.69 and selects one candidate for a future implementation
branch. It is authorization-only.

## Baseline Evidence

| Check | Result |
| --- | --- |
| `pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov` | 116 passed |
| `pytest -o addopts= web/backend/tests/test_data_source_factory_lifecycle_di.py -q --no-cov` | 4 passed |
| OpenAPI smoke with `PYTHONPATH=web/backend` and root `.env` loaded | 548 routes, 500 paths, 536 operation IDs, duplicate operation IDs 0 |

Current direct route/API refs: `8`.

## Candidate Matrix

| Candidate | Direct refs | Route count | Ruff | Black | GitNexus | Disposition |
| --- | ---: | ---: | --- | --- | --- | --- |
| `web/backend/app/api/market/market_data_request.py` | 2 | 11 | pass | pass | LOW/1 | Select for future G2.71 |
| `web/backend/app/api/data/kline.py` | 2 | 4 | fails E701 | would reformat | LOW/1 | Defer |
| `web/backend/app/api/data/futures.py` | 2 | 2 | pass | would reformat | CRITICAL/151 | Defer |
| `web/backend/app/api/data/stocks.py` | 2 | 5 | fails E701 | would reformat | LOW/1 | Defer |

`market_data_request.py` has the broadest route count, but the direct migration
surface is exactly two getter refs, it has no ruff/black debt at current HEAD,
and GitNexus reports LOW/1. That makes it the cleanest next implementation
candidate.

## Decision

Select `web/backend/app/api/market/market_data_request.py` for future G2.71.

Expected future direct ref movement:

| Metric | Before future G2.71 | Expected after future G2.71 |
| --- | ---: | ---: |
| Total direct route/API `get_data_source_factory()` refs | 8 | 6 |
| `web/backend/app/api/market/market_data_request.py` direct refs | 2 | 0 |

## Deferred Candidates

- `web/backend/app/api/data/kline.py`: LOW/1, but current ruff fails E701 and
  black would reformat. It needs separate style-debt handling or explicit
  same-file normalization authorization.
- `web/backend/app/api/data/futures.py`: ruff passes, but black would reformat
  and GitNexus file-level impact remains CRITICAL/151. It needs narrower symbol
  impact or separate risk review.
- `web/backend/app/api/data/stocks.py`: LOW/1, but current ruff fails E701 and
  black would reformat. It also has a larger route/file surface than `kline.py`.

## Authorized Future Scope

If this packet is accepted, a future G2.71 implementation branch may be created
with source scope limited to:

- `web/backend/app/api/market/market_data_request.py`
- a focused route dependency wiring test
- implementation evidence
- steward tree update
- mainline task card

No source edit is authorized by G2.70 itself.

## Next Gate

Human review / PR merge decision for G2.70. If accepted, create a separate
G2.71 path-limited implementation branch for
`web/backend/app/api/market/market_data_request.py`.
