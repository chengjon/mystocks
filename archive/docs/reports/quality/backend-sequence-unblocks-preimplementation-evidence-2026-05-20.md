# Backend Sequence Unblocks Pre-Implementation Evidence

> **历史状态说明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

Status: Evidence recorded; no source changes authorized
Date: 2026-05-20
Branch: `wip/root-dirty-20260403`
HEAD: `7b097fffd Record miniQMT authoritative-ready evidence alignment`
OpenSpec change: `sequence-backend-architecture-unblocks`

2026-05-21 freshness note: runtime blocker details in this pre-implementation
report are historical. Later runtime-unblock evidence and
`docs/reports/quality/codebase-map-task-completion-validity-2026-05-21.md`
show current dirty-worktree import, collect-only, and OpenAPI smoke passing.
Use this report for Task 1.x provenance, schema consumer history, and singleton
freshness inputs, not as the current runtime blocker.

## Scope

This report records OpenSpec Task 1.x pre-implementation evidence for
`sequence-backend-architecture-unblocks`.

It does not authorize backend source edits, GitHub issue state changes, OpenSpec
publication, OpenSpec implementation beyond the evidence tasks, Core Batch 2, or
schema directory retirement.

## Runtime Import Evidence

Command:

```bash
PYTHONPATH=web/backend python -c "from app.main import app; print(len(app.routes))"
```

Result: failed.

Current failure chain:

```text
app.main
-> app.router_registry
-> app.api.data_lineage
-> app.api._data_lineage_responses
-> _AsyncpgLineageConnectionAdapter
-> @asynccontextmanager
```

Failure:

```text
NameError: name 'asynccontextmanager' is not defined
```

Interpretation: `data_lineage.py` already uses package-relative import for
`._data_lineage_responses`. The active blocker is the missing
`asynccontextmanager` import in `web/backend/app/api/_data_lineage_responses.py`.

## Collection Smoke Evidence

Command:

```bash
pytest -o addopts= web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov
```

Result: failed during collection.

Summary:

```text
ERROR collecting web/backend/tests/test_health_route_conflicts.py
E   NameError: name 'asynccontextmanager' is not defined
Interrupted: 1 error during collection
```

Interpretation: this is a collection blocker, not a clean `0 tests collected`
result.

## Schema Consumer Evidence

Root checkout scan excluded `.worktrees/` and looked for:

- `from app.schema`
- `import app.schema`
- dynamic import patterns for `app.schema`

Current root checkout result:

| Pattern | Count |
|---|---:|
| `from app.schema` | 3 |
| `import app.schema` | 0 |
| dynamic `app.schema` import | 0 |

Current consumers:

| File | Line | Import |
|---|---:|---|
| `web/backend/app/api/technical_analysis.py` | 17 | `from app.schema import StockSymbolModel, TechnicalIndicatorQueryModel` |
| `web/backend/app/api/stock_search/stock_search_result.py` | 48 | `from app.schema import StockListQueryModel` |
| `web/backend/tests/test_validation_models.py` | 13 | `from app.schema.validation_models import (...)` |

Legacy validation models currently live in
`web/backend/app/schema/validation_models.py`, including:

- `StockSymbolModel`
- `DateRangeModel`
- `MarketDataQueryModel`
- `TechnicalIndicatorQueryModel`
- `PaginationModel`
- `StockListQueryModel`
- `TradeOrderModel`
- `ResponseModel`
- `ErrorResponseModel`

`web/backend/app/schemas/__init__.py` currently has no detected re-export lines.
Schema closure must therefore prove canonical exports before consumer migration
or legacy directory retirement.

## Singleton Inventory Evidence

The existing curated report
`docs/reports/quality/backend-singleton-lifecycle-routing-matrix-2026-05-19.md`
was generated at `6530c88f3`. Current HEAD `7b097fffd` differs from that report,
but `git diff --name-only 6530c88f3..HEAD` shows no changes under:

- `web/backend/app/services/`
- `web/backend/app/api/`

Therefore the curated service and singleton routing conclusions remain usable for
this pre-implementation gate unless a later service/API change invalidates them.

Current ad-hoc root scan over `web/backend/app/services/` found a broad
singleton/getter surface:

| Scan item | Count |
|---|---:|
| Python service files scanned | 152 |
| Pattern hits | 438 |
| Module global instance/cache hits | 42 |
| Getter function hits | 377 |
| `spec_from_file_location` hits | 10 |
| `singleton` word hits | 5 |
| `lru/cache` decorator hits | 4 |

This ad-hoc scan is not a replacement for the curated matrix. It does confirm the
same direction: the service surface is broad and should not be treated as having
a clean low-risk lifecycle pilot by default.

The curated matrix remains the decision source for this branch:

- no next `#79` stateless pilot was selected
- external-client wrappers stay in a separate lane
- DB/session-backed services are heavy/stateful and must not be picked directly
  as the next pilot
- cache/task-running services are stateful and not stateless pilots
- the next service lifecycle step should use classification plus
  interface/test-double strategy rather than forcing a pilot

## Task 1.x Disposition

| Task | Disposition |
|---|---|
| 1.1 Runtime blocker reconfirmed | Complete |
| 1.2 Health route collection result recorded | Complete |
| 1.3 Schema consumer scan recorded | Complete |
| 1.4 Singleton inventory and no-low-risk-pilot evidence reconciled | Complete |

## Next Gate

Do not edit backend source from this report.

Next allowed action, after human/OpenSpec approval of
`sequence-backend-architecture-unblocks`, is Runtime Unblock Task 2.x:

1. Run required GitNexus context/impact for
   `web/backend/app/api/_data_lineage_responses.py` or the relevant symbol.
2. If risk is HIGH or CRITICAL, stop and return to review.
3. If approved and low-risk, add `from contextlib import asynccontextmanager` to
   `web/backend/app/api/_data_lineage_responses.py`.
4. Re-run `app.main` import and `test_health_route_conflicts.py --collect-only`.

## Verification

- Runtime import smoke: failed on `_data_lineage_responses.py`
  `NameError: asynccontextmanager`.
- Health route collect-only smoke: failed on the same import chain.
- Schema consumer scan: root checkout has three `from app.schema` consumers.
- Service freshness check: no `web/backend/app/services/` or
  `web/backend/app/api/` changes between `6530c88f3` and `7b097fffd`.
