# 数据源优化 V2 - 快速参考指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**版本**: V2.0 Phase 1-2（当前仓库实现对齐）
**最后更新**: 2026-05-02

---

## 概述

数据源优化 V2 当前在仓库里已落地五个核心组件，用于提升系统性能、可靠性和数据质量：

1. **SmartCache** - 智能缓存 (TTL + 预刷新 + 软过期)
2. **CircuitBreaker** - 熔断器 (保护系统免受级联故障)
3. **DataQualityValidator** - 数据质量验证 (多层验证)
4. **SmartRouter** - 智能路由 (性能/成本/负载/地域多维度评分)
5. **BatchProcessor** - 治理层批量抓取并发执行 (分组 + timeout fail-fast + 异常隔离)

> **Repo-truth（2026-05-02）**:
> - `src/core/data_source/router.py:get_best_endpoint()` 当前已经会懒加载 `SmartRouter` 并通过 `smart_router.route(...)` 做选择。
> - 当前接入保留了原有 `config` 嵌套结构，同时把 `config` 字段平铺到顶层，兼容 downstream handler 对 `source_type` 等顶层字段的读取。
> - `src/governance/core/fetcher_bridge.py:GovernanceDataFetcher` 当前多 symbol 批量路径已经接入 `src/core/data_source/batch_processor.py:BatchProcessor`，但单 symbol 仍保留串行抓取。
> - `BatchProcessor` 当前已在 K 线批量链路里使用 `concurrent.futures.as_completed(..., timeout=...)` 轮询已完成任务，并结合 per-request 经过时间做 timeout fail-fast。
> - 本指南仅覆盖当前代码里已经落地的路由接线与批量抓取主链路；A/B 测试、灰度部署与正式性能验收不在本页声称完成。

---

## 快速开始

### 启用优化 (默认启用)

```python
from src.core.data_source import DataSourceManagerV2

# 使用 SmartCache (默认)
manager = DataSourceManagerV2()

# 禁用 SmartCache (使用传统 LRUCache)
manager = DataSourceManagerV2(use_smart_cache=False)
```

---

## SmartCache 使用

### 基本用法

```python
from src.core.data_source.smart_cache import SmartCache

# 创建缓存
cache = SmartCache(
    maxsize=100,              # 最大缓存条目数
    default_ttl=3600,         # 默认 TTL (1 小时)
    refresh_threshold=0.8,    # 80% TTL 时预刷新
    soft_expiry=True,         # 启用软过期
)

# 设置缓存
cache.set("key1", "value1")

# 获取缓存
value = cache.get("key1")

# 设置自定义 TTL 和刷新函数
cache.set("key2", "value2", ttl=1800, refresh_func=lambda: fetch_new_data())

# 使缓存失效
cache.invalidate("key1")

# 清空缓存
cache.clear()

# 获取统计信息
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
```

### 配置选项

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `maxsize` | 100 | 最大缓存条目数 |
| `default_ttl` | 3600 | 默认 TTL (秒) |
| `refresh_threshold` | 0.8 | 预刷新阈值 (0.0-1.0) |
| `soft_expiry` | True | 启用软过期 |
| `max_refresh_workers` | 5 | 最大后台刷新线程数 |

### 统计信息

```python
stats = cache.get_stats()
# {
#     "size": 当前缓存条目数,
#     "maxsize": 最大缓存条目数,
#     "hits": 缓存命中次数,
#     "misses": 缓存未命中次数,
#     "hit_rate": 缓存命中率,
#     "refreshes": 刷新成功次数,
#     "refresh_failures": 刷新失败次数,
#     "refreshing_count": 正在刷新的 key 数量,
# }
```

---

## CircuitBreaker 使用

### 基本用法

```python
from src.core.data_source.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError

# 创建熔断器
cb = CircuitBreaker(
    failure_threshold=5,      # 连续失败 5 次触发熔断
    recovery_timeout=60,      # 60 秒后尝试恢复
    name="my_endpoint",
)

# 使用熔断器保护函数调用
try:
    result = cb.call(risky_function, arg1, arg2)
    print("Call succeeded")
except CircuitBreakerOpenError as e:
    print(f"Circuit breaker is open: {e}")
    # 使用降级逻辑
    result = get_fallback_data()
except Exception as e:
    print(f"Call failed: {e}")

# 获取状态
state = cb.get_state()
print(f"Circuit breaker state: {state.value}")

# 手动重置
cb.reset()

# 获取统计信息
stats = cb.get_stats()
```

### 熔断器状态

| 状态 | 说明 | 行为 |
|------|------|------|
| `CLOSED` | 正常状态 | 允许所有请求通过 |
| `OPEN` | 熔断状态 | 拒绝所有请求 |
| `HALF_OPEN` | 半开状态 | 允许试探请求 |

### 配置选项

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `failure_threshold` | 5 | 连续失败次数阈值 |
| `recovery_timeout` | 60 | 恢复超时时间 (秒) |
| `expected_exception` | `Exception` | 预期的异常类型 |
| `name` | "default" | 熔断器名称 |

### 统计信息

```python
stats = cb.get_stats()
# {
#     "name": 熔断器名称,
#     "state": 当前状态,
#     "failure_count": 当前连续失败次数,
#     "success_count": 半开状态连续成功次数,
#     "total_calls": 总调用次数,
#     "total_successes": 总成功次数,
#     "total_failures": 总失败次数,
#     "success_rate": 成功率,
#     "failure_threshold": 失败阈值,
#     "recovery_timeout": 恢复超时时间,
#     "last_failure_time": 最后失败时间,
#     "opened_at": 熔断器开启时间,
#     "remaining_time": 剩余恢复时间 (秒),
# }
```

---

## DataQualityValidator 使用

### 基本用法

```python
from src.core.data_source.data_quality_validator import DataQualityValidator

# 创建验证器
validator = DataQualityValidator(
    enable_logic_check=True,         # 启用逻辑检查
    enable_business_check=True,      # 启用业务规则检查
    enable_statistical_check=True,   # 启用统计异常检测
    enable_cross_source_check=False, # 禁用跨源验证
)

# 验证数据
summary = validator.validate(data, data_source="akshare")

# 检查验证结果
if summary.passed:
    print(f"✅ Validation passed! Quality score: {summary.quality_score:.1f}")
else:
    print(f"❌ Validation failed! {summary.failed_checks}/{summary.total_checks} checks failed")

# 查看详细结果
for result in summary.results:
    status = "✅" if result.passed else "❌"
    print(f"{status} {result.check_type}: {result.message}")
    if result.details:
        print(f"   Details: {result.details}")
```

### 验证类型

| 检查类型 | 说明 | 检查项 |
|----------|------|--------|
| `logic_check` | 基础逻辑验证 | OHLC 逻辑、成交量 >= 0 |
| `business_check` | 业务规则验证 | 极端价格、异常成交量、停牌数据 |
| `statistical_check` | 统计异常检测 | 3-sigma 离群值 |
| `cross_source_check` | 跨源验证 | 价格/成交量一致性 |

### 质量评分

质量评分范围: **0-100 分**

评分规则:
- 基础分: 100 分
- 逻辑检查失败: -40 分
- 业务规则检查失败: -30 分
- 统计异常检测失败: -10 分
- 跨源验证失败: -20 分

### 跨源验证示例

```python
# 启用跨源验证
validator = DataQualityValidator(enable_cross_source_check=True)

# 提供参考数据 (来自另一个数据源)
summary = validator.validate(
    data1,
    data_source="akshare",
    reference_data=data2,  # 来自 tushare 的数据
)

if summary.passed:
    print("✅ Cross-source validation passed")
else:
    print("❌ Cross-source validation failed")
    print(f"Price diff: {summary.results[3].details['price_diff']:.2%}")
```

---

## SmartRouter 使用

### 当前接入方式

```python
from src.core.data_source import DataSourceManagerV2

manager = DataSourceManagerV2()
best_endpoint = manager.get_best_endpoint("DAILY_KLINE")

if best_endpoint is None:
    print("No healthy endpoint available")
else:
    print(best_endpoint["endpoint_name"])
    print(best_endpoint["config"]["source_name"])
```

### 当前路由链路

1. `find_endpoints()` 先按 `data_category`、`source_name`、`target_db`、`health_status` 过滤候选端点。
2. `get_best_endpoint()` 在第一次调用时懒加载 `SmartRouter()`。
3. 候选端点会从 `{endpoint_name, config}` 扩展为“保留 `config` 嵌套 + 平铺运行字段”的兼容形态。
4. `SmartRouter.route(...)` 按综合评分返回最佳端点；如果 route 返回空值，则回退到候选列表第一个端点。

### 默认评分权重

| 维度 | 默认权重 | 说明 |
|------|----------|------|
| `performance_weight` | `0.4` | 历史延迟与成功率 |
| `cost_weight` | `0.3` | 免费源 / 免费额度优先 |
| `load_weight` | `0.2` | 当前并发负载 |
| `location_weight` | `0.1` | 调用方地域亲和度 |

### 手动注入自定义 SmartRouter

```python
from src.core.data_source import DataSourceManagerV2
from src.core.data_source.smart_router import SmartRouter

manager = DataSourceManagerV2()
manager.smart_router = SmartRouter(
    performance_weight=0.5,
    cost_weight=0.2,
    load_weight=0.2,
    location_weight=0.1,
)
```

### Endpoint 形态注意事项

当前 `SmartRouter` 接到的是兼容 shape：

```python
{
    "endpoint_name": "akshare.daily",
    "config": {...},
    "source_name": "...",        # 从 config 平铺
    "source_type": "...",        # 从 config 平铺
    "data_category": "...",      # 从 config 平铺
    "cost": {...},               # 若 config 中存在
}
```

这样做的原因是：
- `SmartRouter` 评分逻辑需要直接读取 `source_type`、`cost`、`location` 等运行字段
- 下游 `handler.py` 仍依赖顶层字段，而不是只读嵌套 `config`

### 当前边界

- 当前已实现的是“候选端点选择接线”，不是完整的线上性能闭环。
- `caller_location` 当前来自 `_identify_caller()` 的 best-effort 推断；拿不到时回退为 `default`。
- `SmartRouter` 已接入主选择链路，但 `5.11 A/B 测试`、正式性能验收和灰度部署仍需独立完成。

---

## BatchProcessor 使用

### 当前接入方式

```python
from src.governance.core.fetcher_bridge import GovernanceDataFetcher, RoutePolicy

fetcher = GovernanceDataFetcher()
results = fetcher.fetch_batch_kline(
    symbols=["000001", "000002", "600000"],
    start_date="20240101",
    end_date="20240131",
    policy=RoutePolicy.SMART_ROUTING,
)

for symbol, df in results.items():
    print(symbol, len(df))

fetcher.shutdown()
```

### 当前批量链路

1. `GovernanceDataFetcher.__init__()` 持有 `BatchProcessor()`。
2. `fetch_batch_kline()` 在多 symbol 场景下委托给 `batch_processor.fetch_batch_kline(...)`。
3. `BatchProcessor` 通过 `GovernanceDataFetcher.resolve_endpoint(...)` 按 `data_category / policy / source_id` 解析当前端点。
4. 请求按 `endpoint_name` 分组后，用 `executor.submit(...)` 并发执行。
5. 已完成任务通过 `as_completed(..., timeout=...)` 轮询收集；超时任务会被标成失败，不阻塞已完成结果返回。
6. `GovernanceDataFetcher.fetch_batch_kline()` 最终仍返回 `Dict[symbol, DataFrame]`，不把内部批处理 envelope 暴露给上游。

### 当前已验证的行为

- `tests/integration/test_batch_processing.py`
  - `100` symbol 并发抓取
  - 单请求 timeout fail-fast
  - 部分失败异常隔离
  - `shutdown(wait=False)` 优雅关闭
  - 本地 stub workload 吞吐量对比（batch 相对串行基线至少 `2x`）
- `src/governance/tests/test_fetcher_bridge.py`
  - `GovernanceDataFetcher` 走 `BatchProcessor` 主路径时仍保持原有公共返回形状
  - `shutdown()` 正确委托到底层批处理器
  - 共享 `DataSourceManagerV2` 实例下，每个 symbol 的 endpoint 解析与 `_call_endpoint()` 返回不串线

### 当前边界

- 当前多 symbol 路径已并发化，但单 symbol 仍走原有串行 `_fetch_single_symbol(...)`。
- 当前实现既保留 per-request timeout fail-fast，又把已完成任务的收集统一到 `as_completed(..., timeout=...)`。
- 当前吞吐量对比证据来自本地 synthetic / stub workload，不等同于生产验收吞吐量。
- `8.x` 灰度/生产验收仍需独立完成。

---

## 最佳实践

### SmartCache

✅ **推荐做法**:
- 根据数据特性设置合理的 TTL
- 为热点数据配置刷新函数
- 监控缓存命中率和刷新失败率
- 使用软过期提高可用性

❌ **避免**:
- TTL 设置过短 (< 5 分钟) 导致频繁刷新
- 忽略刷新失败导致数据过时
- 线程池设置过大导致资源耗尽

### CircuitBreaker

✅ **推荐做法**:
- 免费数据源使用较低阈值 (3 次)
- 付费数据源使用较高阈值 (10 次)
- 监控熔断器状态转换
- 实现降级逻辑处理熔断

❌ **避免**:
- 阈值设置过高导致无法熔断
- 忽视熔断器异常直接失败
- 多进程环境使用进程内熔断器

### DataQualityValidator

✅ **推荐做法**:
- 根据数据质量要求选择验证级别
- 仅在必要时启用跨源验证
- 定期审查验证规则和阈值
- 结合业务场景调整阈值

❌ **避免**:
- 所有数据启用所有验证 (性能开销大)
- 忽视质量评分盲目信任数据
- 硬编码阈值不适应业务变化

---

## 故障排查

### SmartCache 问题

**问题**: 缓存命中率低

**排查**:
```python
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
print(f"Size: {stats['size']}/{stats['maxsize']}")

# 检查 TTL 是否过短
# 检查 maxsize 是否过小
# 检查是否有大量并发刷新失败
```

**解决方案**:
- 增大 TTL 或 maxsize
- 优化刷新函数避免失败
- 检查缓存键设计

### CircuitBreaker 问题

**问题**: 熔断器频繁开启

**排查**:
```python
stats = cb.get_stats()
print(f"State: {stats['state']}")
print(f"Failures: {stats['failure_count']}/{stats['failure_threshold']}")
print(f"Success rate: {stats['success_rate']:.2%}")
```

**解决方案**:
- 检查后端服务健康状况
- 调整 failure_threshold
- 检查网络连接

### DataQualityValidator 问题

**问题**: 验证频繁失败

**排查**:
```python
summary = validator.validate(data, data_source="test")
for result in summary.results:
    if not result.passed:
        print(f"{result.check_type}: {result.message}")
        print(f"Details: {result.details}")
```

**解决方案**:
- 检查数据源质量
- 调整验证阈值
- 禁用不合适的验证类型

---

## 性能调优

### TTL 设置建议

| 数据类型 | 推荐 TTL | 说明 |
|----------|---------|------|
| 实时数据 | 30 秒 | 秒级更新 |
| 分钟数据 | 5 分钟 | 高频更新 |
| 日线数据 | 1 小时 | 日频更新 |
| 参考数据 | 24 小时 | 低频更新 |

### 熔断器阈值建议

| 数据源类型 | 推荐阈值 | 恢复时间 |
|------------|---------|---------|
| 免费数据源 | 3 次 | 60 秒 |
| 付费数据源 | 10 次 | 60 秒 |
| 内部服务 | 5 次 | 30 秒 |

### 线程池大小建议

| 场景 | max_workers | 说明 |
|------|-------------|------|
| 低并发 | 3 | 保守配置 |
| 中等并发 | 5 | 默认配置 |
| 高并发 | 10 | 激进配置 |

---

## 进阶用法

### 自定义刷新逻辑

```python
def smart_refresh_func():
    """智能刷新逻辑: 先检查数据版本,仅在必要时更新"""
    current_version = get_data_version()
    cached_version = get_cached_version()

    if current_version > cached_version:
        return fetch_new_data()
    else:
        return None  # 返回 None 表示不需要更新

cache.set("key1", "value1", refresh_func=smart_refresh_func)
```

### 熔断器降级策略

```python
def call_with_fallback(cb, func, fallback_func, *args, **kwargs):
    """带降级的熔断器调用"""
    try:
        return cb.call(func, *args, **kwargs)
    except CircuitBreakerOpenError:
        logger.warning("Circuit breaker open, using fallback")
        return fallback_func(*args, **kwargs)

# 使用
result = call_with_fallback(
    cb,
    fetch_from_remote,
    fetch_from_cache,
    symbol="000001",
)
```

### 多层验证策略

```python
def validate_with_strategy(data, strategy="strict"):
    """根据策略选择验证级别"""
    if strategy == "strict":
        validator = DataQualityValidator(
            enable_logic_check=True,
            enable_business_check=True,
            enable_statistical_check=True,
            enable_cross_source_check=True,
        )
    elif strategy == "normal":
        validator = DataQualityValidator(
            enable_logic_check=True,
            enable_business_check=True,
            enable_statistical_check=False,
            enable_cross_source_check=False,
        )
    elif strategy == "loose":
        validator = DataQualityValidator(
            enable_logic_check=True,
            enable_business_check=False,
            enable_statistical_check=False,
            enable_cross_source_check=False,
        )

    return validator.validate(data)

# 使用
summary = validate_with_strategy(data, strategy="normal")
```

---

## 相关文档

- [完整实现报告](./reports/DATA_SOURCE_OPTIMIZATION_PHASE1_COMPLETION_REPORT.md)
- [提案文档](../openspec/changes/optimize-data-source-v2/proposal.md)
- [设计文档](../openspec/changes/optimize-data-source-v2/design.md)
- [任务清单](../openspec/changes/optimize-data-source-v2/tasks.md)

---

**文档版本**: 1.0
**最后更新**: 2026-01-09
**维护者**: Claude Code
