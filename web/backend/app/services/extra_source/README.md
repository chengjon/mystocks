# ExtraSource Adapter Registry

> **Scope**: `web/backend/app/services/extra_source/` — consumer-side (mystocks_spec)
> auxiliary data sources that fill **permanently uncovered** gaps in the
> OpenStock data gateway.
>
> **Authoritative contract**:
> [`openspec/changes/add-extra-source-adapter-contract/`](../../../../openspec/changes/add-extra-source-adapter-contract/)
> — README is a developer cheatsheet, not a contract.

## 何时该用 ExtraSource

✅ **Use ExtraSource** when **all** of these are true:

1. The category you need is **not** in
   [`OPENSTOCK_STATIC_CATEGORIES`](registry.py) (the 70-category snapshot
   sourced from OpenStock `DATA_CAPABILITY_SCOPE.md`).
2. OpenStock has **no roadmap plan** to add this category.
3. The data is consumer-specific (mystocks_spec-only) rather than
   a common market primitive that every consumer needs.

→ Register as **常规 ExtraSource** (`expires_on=None`).

✅ **Use TEMP_OVERRIDE ExtraSource** when:

1. The category is **not** in OpenStock static inventory.
2. OpenStock has **a roadmap plan but no implementation yet**
   (e.g. `MARKET_BIG_DEAL` as of 2026-07-02).
3. You have a concrete `expires_on` date (max 90 days from now if
   OpenStock has no firm release date).

→ Register with `expires_on="YYYY-MM-DD"`. Must open dual-repo issues
(see `design.md` §4 — 双仓 follow-up 跟踪).

## 何时不该用 ExtraSource

❌ **Do NOT use ExtraSource** when:

- **The category IS in `OPENSTOCK_STATIC_CATEGORIES`** (FUND_FLOW,
  KLINES, NORTHBOUND_FLOW, etc.). Call `OpenStockClient` directly.
  Layer 1 statically rejects your registration at startup — there is
  no escape hatch.

- **OpenStock's provider is temporarily down** for a category it
  already owns. This is **Layer 2** (OpenStock-internal fallback),
  which this proposal explicitly excludes. Consumer-side fallback for
  OpenStock-owned categories was rejected in Round 2 D (see
  `design.md` §1 决策时间线).

- **You want to provide a "backup version"** of a category OpenStock
  already serves. Same reason — violates Layer 3
  (故障处理分工, see `design.md` §3 Layer 3).

- **The data is a common market primitive** that other OpenStock
  consumers would benefit from (e.g. a new index). Propose it in
  the OpenStock repo instead. ExtraSource is for
  mystocks-specific gaps.

## 如何注册

### Step 1 — Implement the adapter

```python
# web/backend/app/services/extra_source_adapters/my_adapter.py
from typing import Any
from app.services.extra_source import ExtraSourceMeta, ExtraSourceResult


class MyAdapter:
    """Fetch <category> from <provider>."""

    def __init__(self) -> None:
        self._meta = ExtraSourceMeta(
            name="my-adapter",                # kebab-case, globally unique
            category="MY_CATEGORY",            # UPPER_SNAKE_CASE, globally unique,
                                               # MUST NOT be in OPENSTOCK_STATIC_CATEGORIES
            expires_on=None,                   # or "2026-09-30" for TEMP_OVERRIDE
        )

    def get_meta(self) -> ExtraSourceMeta:
        return self._meta

    def fetch(self, params: dict[str, Any]) -> ExtraSourceResult:
        # ... your fetch logic ...
        return ExtraSourceResult(
            data={"rows": [...]},
            provider_used="my-adapter",
        )
```

### Step 2 — Wire via settings

In `.env` (or CI/production env):

```
EXTRA_SOURCE_ADAPTERS=app.services.extra_source_adapters.my_adapter.MyAdapter,app.services.extra_source_adapters.other.OtherAdapter
```

Comma-separated import paths. FastAPI lifespan (see
[`app/main.py`](../../main.py)) will:

1. `importlib.import_module` each path
2. Instantiate the class with no args
3. Call `register_extra_source(instance)` — static checks reject
   category/name conflicts with OpenStock static inventory
4. Dump `.extra-source-snapshot.json` (read by Phase 3 CI check)
5. On shutdown: `clear_registered()`

If any registration fails, **startup fails** (fail fast).

## 如何调用

Route handlers do **not** call adapters directly. They go through
`ExtraSourceRouter`:

```python
from app.services.extra_source import default_router, UnsupportedCategoryError

try:
    result = default_router.fetch("MY_CATEGORY", {"date": "2026-07-02"})
    # result.data, result.provider_used
except UnsupportedCategoryError as e:
    # category is OpenStock-owned or unknown — map to UNSUPPORTED_CATEGORY envelope
    ...
# Adapter-side exceptions are wrapped as ExtraSourceFetchError
# (map to DATA_GATEWAY_UNAVAILABLE).
```

The router checks `OPENSTOCK_STATIC_CATEGORIES` first — if the
category belongs to OpenStock, it raises `UnsupportedCategoryError`
(programmer error: should have called `OpenStockClient`).

## 模块布局

```
web/backend/app/services/extra_source/
├── __init__.py         Public symbols (ExtraSourceAdapter, register_extra_source, etc.)
├── contract.py         ExtraSourceMeta / ExtraSourceResult / Protocol / exceptions
├── registry.py         OPENSTOCK_STATIC_CATEGORIES + register_extra_source + snapshot dump
├── router.py           ExtraSourceRouter + UnsupportedCategoryError / ExtraSourceFetchError
├── _test_stubs/        Stub adapters used by integration tests (do not import in prod)
└── README.md           This file
```

## 相关文档

| 文档 | 用途 |
|---|---|
| `openspec/changes/add-extra-source-adapter-contract/proposal.md` | Why & What (契约动机与变更范围) |
| `openspec/changes/add-extra-source-adapter-contract/design.md` | 决策时间线 / 三层契约 / Wave 2/3 归属附录 |
| `openspec/changes/add-extra-source-adapter-contract/tasks.md` | 实施清单 |
| `architecture/STANDARDS.md` | 工程红线(本模块不例外) |
| OpenStock `docs/DATA_CAPABILITY_SCOPE.md` | 70 静态 category 来源 |

## 故障排查

| 症状 | 检查点 |
|---|---|
| 启动 fail with `ExtraSourceCategoryConflictError` | adapter category 与 OPENSTOCK_STATIC_CATEGORIES 重叠 → 改 category 名,或调用 OpenStockClient |
| 启动 fail with `ExtraSourceNameConflictError` | adapter name 已被注册 → 改 name |
| 启动 fail with `ValueError "EXTRA_SOURCE_ADAPTERS 条目格式错误"` | .env 中路径缺少 `.` 分隔 module 与 class,或为空 |
| `ExtraSourceFetchError` at runtime | adapter.fetch() 抛异常,看 `__cause__` 取原始 traceback |
| CI `temp-override-expiration` step fail | TEMP_OVERRIDE adapter 过期,需决策:删除 / 转常规 / 延期(见 design.md §3) |
