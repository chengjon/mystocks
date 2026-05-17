# ADR-0003: Singleton 到 FastAPI Depends 迁移路径

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **Status**: Proposed
> **Date**: 2026-05-16
> **Decision makers**: Backend team

## Context

代码库中存在 118 处 `global _xxx` singleton 模式，分布在 4 个层：

| 层 | 数量 | 代表文件 |
|----|------|----------|
| Core | 45 | `database.py`, `cache_manager.py`, `socketio_manager.py` |
| Services | 35 | `strategy_service.py`, `watchlist_service.py`, `ohlcv_storage.py` |
| Adapters | 5 | `eastmoney_adapter.py`, `tqlex_adapter.py` |
| API | 12 | `realtime_mtm_adapter.py`, `dashboard.py` |
| Others | 21 | tasks, strategies, utils |

所有 singleton 均为 **per-app** 生命周期（应用启动时初始化，运行期间不变）。

当前问题：
- 测试无法干净替换依赖（需 monkeypatch global 变量）
- 初始化顺序隐式依赖（无法从代码直接看出哪个 singleton 先初始化）
- 无法实现 per-request 生命周期变体

## Decision

**渐进式迁移**，不一次性重写所有 singleton：

**Phase 1 — 保留 `get_xxx()` 函数签名，改内部实现为 FastAPI `Depends`**:

```python
# Before
_db_service = None
def get_db_service():
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service

# After (Phase 1)
def get_db_service():
    """FastAPI dependency — per-app lifecycle."""
    return DatabaseService()

# In router:
@router.get("/data")
async def get_data(db: DatabaseService = Depends(get_db_service)):
    ...
```

**Phase 2 — 测试使用 `app.dependency_overrides`**:

```python
# test
app.dependency_overrides[get_db_service] = lambda: mock_db
```

**迁移优先级**:
1. Core 层基础设施 singleton（database, cache, redis）— 被最多模块依赖
2. Service 层业务 singleton（market_data, strategy, watchlist）
3. Adapter 层 singleton
4. API 层 singleton（改为直接注入 service）

**不迁移的例外**:
- `logging/structured.py` 的 `_global_logger` — logger 不是业务依赖
- `logging/tracing.py` 的 `_global_tracer` — 同上
- 纯数据缓存（如 `dashboard.py` 的 `_cache_manager`）— 非服务实例

## Consequences

**Positive**:
- 测试可使用 `dependency_overrides` 替换依赖
- 生命周期可配置（per-app / per-request）
- 初始化顺序显式化

**Negative**:
- 工作量大（118 处），需分批次执行
- 过渡期两种模式并存
- 部分 singleton 的初始化逻辑复杂（如需要配置参数），迁移时需仔细处理

**Estimated timeline**: 2-3 个月，按模块分批，每批 5-10 个 singleton。
