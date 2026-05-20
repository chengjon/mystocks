# Backend Schema Shim Closure Implementation Evidence

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Summary

- Date: 2026-05-20
- OpenSpec change: `sequence-backend-architecture-unblocks`
- Scope: schema shim closure, Task 3.x
- Result: internal `app.schema` consumers migrated to canonical `app.schemas`; legacy `app.schema` remains as a thin compatibility shim

This batch makes `web/backend/app/schemas/validation_models.py` the canonical
implementation for the legacy P0 validation models and keeps
`web/backend/app/schema/validation_models.py` as a compatibility re-export.

## Consumer Matrix

Fresh scan after migration:

```text
LEGACY_CONSUMERS=0
```

Pre-migration consumers were:

| Former consumer | Former import | New import |
|---|---|---|
| `web/backend/app/api/technical_analysis.py` | `from app.schema import StockSymbolModel, TechnicalIndicatorQueryModel` | `from app.schemas import StockSymbolModel, TechnicalIndicatorQueryModel` |
| `web/backend/app/api/stock_search/stock_search_result.py` | `from app.schema import StockListQueryModel` | `from app.schemas import StockListQueryModel` |
| `web/backend/tests/test_validation_models.py` | `from app.schema.validation_models import ...` | `from app.schemas.validation_models import ...` |

## Export Matrix

Verified public model availability:

```text
app.schemas StockSymbolModel,TechnicalIndicatorQueryModel,StockListQueryModel,DateRangeModel
app.schemas.validation_models StockSymbolModel,TechnicalIndicatorQueryModel,StockListQueryModel,DateRangeModel
app.schema StockSymbolModel,TechnicalIndicatorQueryModel,StockListQueryModel,DateRangeModel
app.schema.validation_models StockSymbolModel,TechnicalIndicatorQueryModel,StockListQueryModel,DateRangeModel
```

The old `app.schema` package therefore remains import-compatible while no current
in-repo Python consumer depends on it.

## Verification

Commands run from repository root:

```bash
ruff check web/backend/app/schemas/__init__.py \
  web/backend/app/schemas/validation_models.py \
  web/backend/app/schema/__init__.py \
  web/backend/app/schema/validation_models.py \
  web/backend/app/api/technical_analysis.py \
  web/backend/app/api/stock_search/stock_search_result.py \
  web/backend/tests/test_validation_models.py
```

Result:

```text
All checks passed!
```

```bash
env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_validation_models.py -q --no-cov --tb=short
```

Result:

```text
60 passed in 0.42s
```

Import smoke:

```text
technical_router True
stock_search_result_loaded True
routes 548
```

## Shim Decision

`web/backend/app/schema/` is not retired in this batch.

Decision:

- canonical implementation: `web/backend/app/schemas/validation_models.py`
- canonical package exports: `web/backend/app/schemas/__init__.py`
- compatibility shim retained: `web/backend/app/schema/validation_models.py`
- compatibility package retained: `web/backend/app/schema/__init__.py`

Retirement remains deferred because external consumers and packaged deployment
surfaces were not audited in this targeted batch. A future removal task may delete
`web/backend/app/schema/` only after proving no external or generated-code
consumer still imports `app.schema` or `app.schema.validation_models`.

## OpenSpec State Impact

This closes `sequence-backend-architecture-unblocks` Task 3.1 through 3.5.

It does not authorize unrelated schema package refactors, OpenAPI model renaming,
or deletion of the legacy shim directory.
