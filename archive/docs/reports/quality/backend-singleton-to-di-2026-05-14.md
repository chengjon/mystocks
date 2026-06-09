# MyStocks Singleton → DI 重构路径

> **历史文档说明**:
> 本文件是 Singleton → DI 架构治理草案，不是当前后端依赖注入实施指令。
> 若需确认当前共享规则、审批门禁和实现状态，请优先以 `architecture/STANDARDS.md`、`openspec/AGENTS.md`、当前代码与最近一次验证结果为准。

> **来源**: `docs/reports/quality/backend-audit-2026-05-14.md` §五.1 深化
> **审计日期**: 2026-05-14
> **复核日期**: 2026-05-17
> **执行门禁**: 本文涉及 DI lifecycle、服务初始化方式、测试 override 和跨模块依赖模式，实施前必须创建并通过 OpenSpec proposal/design/tasks 审批。

---

## 一、Singleton 全景清单

2026-05-17 复核扫描 `web/backend/app/`，发现当前仍存在大量 module-level lazy singleton / getter / Depends 混用形态：

| 扫描项 | 当前数量 | 说明 |
|--------|----------|------|
| 顶层 `_xxx = None` 或 `_xxx: ... = None` | 108 | 多数是 lazy singleton、缓存、服务实例、连接或运行时状态 |
| `def get_xxx(...)` 函数 | 200 | 混合了 FastAPI dependency、factory、普通 getter 和 legacy singleton accessor |
| `Depends(...)` 代码近似命中 | 314 | 已剔除注释和字符串后统计，说明仓库已部分使用 FastAPI DI，不能按“从 0 迁移”理解 |
| `app.state` / `request.app.state` 引用 | 9 | 已存在少量 lifespan/app state 模式 |
| lifespan / shutdown / on_event 相关代码命中 | 19 | 已存在生命周期初始化点和关闭钩子，但尚未形成统一治理口径 |

结论：问题不是“没有 DI”，而是 singleton、getter、FastAPI Depends、factory、lifespan 和 app.state 多种生命周期模型并存。后续治理必须先分类，不得机械把所有 getter 改成请求级 `Depends()`。

### 1.1 按层分布

| 层 | 单例数量 | 典型模式 |
|----|----------|----------|
| `services/` | 12 | `get_xxx_service()` → `global _xxx` → lazy init |
| `core/` | 8 | `get_xxx()` → `global _xxx` → lazy init + reset |
| `adapters/` | 5 | `get_xxx_adapter()` → `global _xxx` → lazy init |
| `tasks/` | 2 | `_get_xxx()` → `global _xxx` → lazy init |
| `utils/` | 1 | `get_monitoring_db()` |
| `services/signals/` | 1 | `get_strategy_registry()` |
| `services/market_data_service/` | 1 | `get_market_data_service()` |

### 1.2 历史清单（需按当前代码重扫）

下表是 2026-05-14 的审计样本，保留用于说明问题分布。它不是当前完整清单，也不能作为迁移实施列表。进入代码改造前，必须重新生成当前清单，并为每个对象补生命周期分类。

| 生命周期类型 | 典型对象 | 推荐处理 |
|--------------|----------|----------|
| 轻量无状态 helper | 纯计算、配置读取、无连接资源 | 可以函数化或使用轻量 dependency |
| 重型服务 | 聚合服务、回测、外部客户端、需要 warmup 的对象 | lifespan 初始化，依赖函数从 `app.state` 或专用 container 读取 |
| Adapter / factory | 多数据源 adapter、按 source_type 分发的对象 | 保留 factory 统一管理，测试用 dependency override 注入 mock factory |
| Cache / DB / connection-backed | DB pool、cache manager、scheduler、streaming bridge | 禁止请求级重复创建；必须有 close / teardown 策略 |
| 兼容 getter | 为旧 import 面保留的 `get_xxx` | 默认先保留为薄 wrapper，退役需 OpenSpec 与消费者扫描 |

| # | 文件 | 单例名 | 类/职能 |
|---|------|--------|---------|
| 1 | `core/cache_manager.py` | `_manager` | `CacheManager` |
| 2 | `core/cache_manager.py` | `_async_manager` | `AsyncCacheManager` |
| 3 | `core/cache_eviction.py` | `_eviction_strategy` | `TimeWindowEvictionStrategy` |
| 4 | `core/cache_eviction.py` | `_eviction_scheduler` | `EvictionScheduler` |
| 5 | `core/cache_integration.py` | `_cache_integration` | `CacheIntegration` |
| 6 | `core/cache_prewarming.py` | `_cache_monitor` | `CacheMonitor` |
| 7 | `core/cache_prewarming.py` | `_prewarming_strategy` | `CachePrewarmingStrategy` |
| 8 | `core/circuit_breaker_manager.py` | `_circuit_breaker_manager` | `CircuitBreakerManager` |
| 9 | `core/database.py` | `_db_service` | `DatabaseService` |
| 10 | `core/database_performance.py` | `_performance_manager` | `DatabasePerformanceManager` |
| 11 | `core/database_connection_pool.py` | `_pool_optimizer` | `DatabaseConnectionPoolOptimizer` |
| 12 | `core/database_metrics.py` | `_global_metrics_collectors` | `Dict[str, DatabaseMetricsCollector]` |
| 13 | `core/database_metrics.py` | `_global_performance_loggers` | `Dict[str, QueryPerformanceLogger]` |
| 14 | `core/connection_lifecycle.py` | `_lifecycle_manager` | `ConnectionLifecycleManager` |
| 15 | `core/encryption.py` | `_encryption_manager` | `EncryptionManager` |
| 16 | `adapters/cninfo_adapter.py` | `_cninfo_adapter` | `CninfoAdapter` |
| 17 | `adapters/eastmoney_adapter.py` | `_eastmoney_adapter` | `EastMoneyAdapter` |
| 18 | `adapters/eastmoney_enhanced.py` | `_eastmoney_enhanced_adapter` | `EastMoneyEnhancedAdapter` |
| 19 | `adapters/akshare_extension.py` | `_akshare_extension` | `AkshareExtension` |
| 20 | `adapters/tqlex_adapter.py` | `_tqlex_adapter` | `TqlexDataSource` |
| 21 | `services/market_data_service_v2.py` | `_market_data_service_v2` | `MarketDataServiceV2` |
| 22 | `services/email_notification_service.py` | `_email_service` | `EmailNotificationService` |
| 23 | `services/unified_data_service.py` | `_unified_data_service` | `UnifiedDataService` |
| 24 | `services/subscription_storage.py` | `_storage` | `SubscriptionStorage` |
| 25 | `services/multi_source_manager.py` | `_multi_source_manager` | `MultiSourceManager` |
| 26 | `services/aggregation_streaming_bridge.py` | `_bridge` | `AggregationStreamingBridge` |
| 27 | `services/backtest_engine.py` | `_backtest_engine` | `BacktestEngine` |
| 28 | `services/realtime_streaming_service.py` | `_streaming_service` | `RealtimeStreamingService` |
| 29 | `services/indicator_calculator.py` | `_indicator_calculator` | `IndicatorCalculator` |
| 30 | `services/indicator_registry.py` | `_indicator_registry` | `IndicatorRegistry` |
| 31 | `services/tdx_service.py` | `_tdx_service_instance` | `TdxService` |
| 32 | `services/announcement_service.py` | `_announcement_service` | `AnnouncementService` |
| 33 | `services/email_service.py` | `_email_service` | `EmailService` |
| 34 | `services/filter_service.py` | `_filter_evaluator` | `FilterEvaluator` |
| 35 | `services/filter_service.py` | `_alert_dispatcher` | `AlertDispatcher` |
| 36 | `services/room_socketio_adapter.py` | `_adapter` | `RoomSocketIOAdapter` |
| 37 | `services/signals/strategies/registry.py` | `_strategy_registry_instance` | `StrategyRegistry` |
| 38 | `services/market_data_service/get_market_data_service.py` | `_market_data_service` | `MarketDataService` |
| 39 | `utils/risk_utils.py` | `_monitoring_db` | MonitoringDatabase |
| 40 | `tasks/data_sync.py` | `_unified_manager` | `MyStocksUnifiedManager` |
| 41 | `tasks/data_sync.py` | `_data_sources` | `dict` |

---

## 二、当前问题

### 2.1 测试不可替换

每个 singleton 依赖 `global` 变量，测试时必须：

```python
# 测试文件中的 workaround
from app.services.backtest_engine import reset_backtest_engine
reset_backtest_engine()  # 必须在每个测试前调用
```

而非标准的 FastAPI 依赖覆盖：

```python
# FastAPI 原生方式
app.dependency_overrides[get_backtest_engine] = lambda: mock_engine
```

### 2.2 隐式依赖链

`CacheIntegration` 内部依赖 `CacheManager` 单例，`CacheEviction` 又依赖 `CacheIntegration` — 形成隐式单例依赖图，无法通过构造函数显式注入。

### 2.3 生命周期不可控

Singleton 在首次 `get_xxx()` 时初始化，无法控制初始化时机（如数据库连接池应在 app startup 而非首次请求时创建）。

---

## 三、目标架构口径

### 3.1 `Depends()` 只覆盖依赖入口，不自动决定生命周期

```python
# services/backtest_engine.py — 改造后

class BacktestEngine:
    def __init__(self, db_service: DatabaseService, cache: CacheManager):
        self.db = db_service
        self.cache = cache

# 依赖函数作为 FastAPI Depends 入口
def get_backtest_engine(
    db: DatabaseService = Depends(get_db_service),
    cache: CacheManager = Depends(get_cache_manager),
) -> BacktestEngine:
    return BacktestEngine(db_service=db, cache=cache)
```

上例只适用于轻量或已被上游生命周期管理的对象。若 `BacktestEngine` 构造昂贵、持有连接、启动任务或缓存状态，它不应在每次请求依赖解析时重新创建。

### 3.2 应用级生命周期管理

```python
# lifespan sketch
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await create_db_pool()
    app.state.cache = await create_cache()
    try:
        yield
    finally:
        await app.state.cache.close()
        await app.state.db_pool.close()
```

实际实施必须先核对当前 `main.py` / `app_factory.py` 的 lifespan、startup hook 和 `app.state` 使用方式，避免新增第二套生命周期真相源。

---

## 四、提案前分流路线（不直接实施）

### Step 1: 重新生成当前清单

先重新扫描 `web/backend/app/`，把现有对象分成四类：轻量 helper、重型 service、adapter / factory、cache / connection-backed service。只有清单与生命周期分类稳定后，才谈改造顺序。

### Step 2: 先挑选样本，不挑选“5 个试点”口号

不要直接把某 5 个“看起来轻量”的对象当作试点。先选择 2 到 3 个代表样本，验证分类口径是否可执行：

| 样本类型 | 进入条件 | 不进入条件 |
|----------|----------|------------|
| Stateless helper | 无 DB / cache / client / scheduler / thread / warmup | 内部持有连接、线程、定时器、队列或长期状态 |
| Heavy service | 需要 warmup、连接池或昂贵构造 | 不能请求级重复创建 |
| Adapter factory | 按 source_type 分发或复用外部客户端 | 不能把多个 adapter 拆成并行 truth source |
| Cache / connection-backed | 有明确 close / teardown | 不能只改成请求级 `Depends()` |

### Step 3: OpenSpec 设计项

DI 变化属于架构模式变化。proposal/design/tasks 至少要说明：

| 设计项 | 必填内容 |
|--------|----------|
| canonical lifecycle | 哪些对象走 request、app.state、factory、lifespan 或 wrapper |
| 兼容 import 面 | 旧 `get_xxx` 是否保留为薄 wrapper，何时退役 |
| teardown | DB/cache/client/scheduler 如何关闭 |
| 测试策略 | `dependency_overrides`、unit smoke、import smoke 和回滚触发 |
| 性能约束 | 避免请求级重复创建重型服务 |

### Step 4: 批次按生命周期分流

审批通过后，才把对象按生命周期分批，不按文件名硬切：

| 批次 | 候选范围 | 验证 |
|------|----------|------|
| A | 轻量无状态 helper | unit + dependency override |
| B | adapter factory wrapper | import smoke + mock factory override |
| C | heavy service app.state | lifespan startup/shutdown smoke |
| D | cache / DB / connection-backed | teardown smoke + no per-request recreation proof |

---

## 五、迁移模式模板

不要把每个 singleton 都机械迁移成“每次依赖解析都新建实例”或“全部改成 Depends()”。迁移前必须先按生命周期分类：

| 类型 | 推荐方式 |
|------|----------|
| Stateless helper | 可以函数化，或用 `Depends()` 包一层薄依赖 |
| Heavy service | 在 FastAPI lifespan 初始化，依赖函数从 `app.state` 读取 |
| Adapter factory | 由 factory 管理实例，测试用 `dependency_overrides` 注入 mock factory |
| Cache / connection-backed service | 显式 close 或 lifespan teardown，禁止请求级重复创建连接 |

轻量 singleton 从 `global` 模式迁移到 `Depends` 模式的参考步骤：

```python
# === 迁移前 ===
_service: Optional[MyService] = None

def get_my_service() -> MyService:
    global _service
    if _service is None:
        _service = MyService()
    return _service

def reset_my_service():
    global _service
    _service = None


# === 迁移后（仅适用于轻量无状态服务）===
class MyService:
    def __init__(self, dep1: Dep1, dep2: Dep2):
        self.dep1 = dep1
        self.dep2 = dep2

def get_my_service(
    dep1: Dep1 = Depends(get_dep1),
    dep2: Dep2 = Depends(get_dep2),
) -> MyService:
    return MyService(dep1=dep1, dep2=dep2)
```

测试覆盖：

```python
# 测试中干净替换
def test_with_mock():
    app.dependency_overrides[get_dep1] = lambda: MockDep1()
    # 无需 reset_xxx() 清理
```

---

## 六、验收标准

| Phase | 验收条件 |
|-------|----------|
| 1 | 轻量 helper 的生命周期分类完成，且不把请求级 `Depends()` 误用到重型对象 |
| 2 | 重型服务有 lifespan 或 app.state 方案，`dependency_overrides` 可覆盖 |
| 3 | adapter factory / legacy getter 的兼容面已分类，`get_xxx_adapter()` 退役有条件 |
| 4 | cache / DB / connection-backed 对象有 close / teardown 方案 |
| 全部 | `global`、`Depends`、factory、app.state 的责任边界已写入 OpenSpec 并通过 validate |

---

*前置文档: `docs/reports/quality/backend-audit-2026-05-14.md` §五.1*
