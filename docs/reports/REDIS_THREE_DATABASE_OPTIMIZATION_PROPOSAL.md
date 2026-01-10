# Redis 三数据库架构集成与优化方案 (V1.1 优化版)

**版本**: V1.1 (Optimized)
**日期**: 2026-01-10
**状态**: 🟢 准备执行
**优先级**: P0

---

## 📋 执行摘要

MyStocks 项目已成功部署 **Redis 基础设施**（连接池、L2 缓存服务、消息总线、分布式锁）。当前的核心任务是**业务集成**，即将这些“孤岛”能力注入到核心业务流中。

本方案旨在通过**三大战役**实现架构落地：
1.  **CacheManager 异步化重构**：打通 L1(内存) -> L2(Redis) -> L3(TDengine) 的高速通路。
2.  **SmartScheduler 智能去重**：利用分布式锁彻底解决多实例重复计算问题。
3.  **全链路事件驱动**：利用 Pub/Sub 实现“计算-推送-展示”的毫秒级闭环。

---

## 🎯 优化目标与预期收益

| 模块 | 现状痛点 | 优化方案 | 核心收益 |
| :--- | :--- | :--- | :--- |
| **CacheManager** | ❌ 仅进程内缓存，重启丢失<br>❌ 同步 IO 阻塞主线程 | ✅ **引入 Redis L2 共享缓存**<br>✅ **全异步化 (Async) 改造** | **API 响应速度提升 5-10 倍**<br>缓存命中率 > 90% |
| **SmartScheduler** | ❌ 多实例重复计算同一指标<br>❌ 资源浪费严重 | ✅ **Redis 分布式锁 (Lock)**<br>✅ **计算结果 Redis 共享** | **计算资源消耗降低 70%**<br>彻底消除并发冲突 |
| **Daily Job** | ❌ “黑盒”运行，无进度反馈<br>❌ 必须轮询数据库查状态 | ✅ **Pub/Sub 实时事件流**<br>✅ **WebSocket 直连前端** | **实时可观测性**<br>用户体验质的飞跃 |

---

## 🏗️ 核心架构设计 (The "Three-Database" Pattern)

### 1. 缓存分层策略

采用 **Cache-Aside + Write-Through** 混合模式：

*   **L1 内存 (Local)**: `dict`。存活 5 分钟。存储极热数据（如最新股价），**进程独享**。
*   **L2 缓存 (Redis)**: `String/Hash`。存活 1 小时。存储计算结果、API 响应，**分布式共享**。
*   **L3 持久化 (TDengine)**: `SuperTable`。永久存储。存储历史 K 线、历史指标，**冷热分离**。

**查询路径**:
`API Request` -> `L1 (Memory)` -> `L2 (Redis)` -> `L3 (TDengine)` -> `Source (PostgreSQL)`

### 2. 键名命名规范 (Key Naming Convention)

为防止 Key 冲突，严格执行以下命名空间：

*   **行情**: `mkt:qt:{symbol}` (e.g., `mkt:qt:000001`)
*   **指标**: `ind:{symbol}:{code}:{params_hash}` (e.g., `ind:000001:MACD:a1b2c3`)
*   **锁**: `lock:calc:{symbol}:{code}` (e.g., `lock:calc:000001:MACD`)
*   **任务**: `task:{job_id}`

---

## 📝 详细实施计划

### 阶段 1: CacheManager 异步化与 Redis 集成 (P0)

**风险提示**: `CacheManager` 目前是同步的，直接接入异步 Redis 会导致性能瓶颈或死锁。必须先进行异步化改造。

**执行步骤**:
1.  **接口升级**: 将 `fetch_from_cache` 和 `write_to_cache` 改造为 `async def`。
2.  **Redis 注入**: 在 `__init__` 中注入 `RedisCacheService`。
3.  **读逻辑**:
    *   `await redis.get(key)`
    *   Hit -> 异步回填 L1
    *   Miss -> `await tdengine.read(...)` -> 异步回填 L2 + L1
4.  **写逻辑**:
    *   `await redis.set(key, val, ttl)`
    *   后台任务写入 TDengine (不阻塞 API 返回)
5.  **兼容性修复**: 修改所有调用 `CacheManager` 的 API (如 `market.py`) 为 `await cache.fetch...`。

### 阶段 2: SmartScheduler 分布式锁集成 (P0)

**核心逻辑**: "Check-Lock-Check-Compute" (CLCC)

**代码逻辑**:
```python
async def calculate_single(self, ...):
    # 1. First Check: Redis 缓存是否已有结果？
    cached = await redis_cache.get(key)
    if cached: return cached

    # 2. Lock: 获取分布式锁
    async with redis_lock.lock(lock_key, timeout=60):
        # 3. Second Check (Double-checked locking): 再次检查缓存
        # 防止在等待锁的过程中，前一个持有锁的实例已经计算完了
        cached = await redis_cache.get(key)
        if cached: return cached

        # 4. Compute: 执行昂贵的计算
        result = do_heavy_calculation()

        # 5. Save: 存入 Redis (供其他实例使用)
        await redis_cache.set(key, result, ttl=3600)
        return result
```

### 阶段 3: 事件驱动改造 (P1)

**目标**: 让 `daily_calculation` 这里的批处理任务“活”起来。

**执行步骤**:
1.  **频道定义**: 定义 `channel:task_updates` 和 `channel:indicators`。
2.  **埋点**:
    *   任务开始 -> `publish("task_updates", {"status": "start"})`
    *   每 50 个股票 -> `publish("task_updates", {"progress": 10%})`
    *   异常 -> `publish("task_updates", {"error": "..."})`
3.  **WebSocket 对接**: 确保 WebSocket 服务订阅了 Redis 频道，并能转发给前端。

---

## ⚠️ 风险控制与降级策略

1.  **Redis 宕机**:
    *   **策略**: 自动熔断。如果 Redis 连接失败，`CacheManager` 自动降级为 "L1 + L3" 模式，仅记录 Error Log，不抛出异常阻断业务。
    *   **实现**: 在 `redis_client` 中封装 `safe_call` 装饰器。

2.  **缓存雪崩**:
    *   **策略**: Redis Key 的 TTL 增加随机抖动 (e.g., `3600 + random(0, 300)` 秒)，防止同一时间大面积过期。

3.  **数据一致性**:
    *   **策略**: 采用 **"最终一致性"**。
    *   修改数据时 -> 先删 Redis -> 再更新 DB -> (下次读取时重建缓存)。

---

## ✅ 验收标准 (Definition of Done)

1.  **单元测试**: `tests/integration` 下新增针对 Redis 场景的测试用例并通过。
2.  **性能测试**: 在模拟并发下，同一指标计算任务，Redis 锁能成功拦截 90% 的重复计算。
3.  **代码覆盖**: 核心业务代码（API、调度器）完成 `async` 迁移，无同步阻塞调用。

---

**建议**: 请优先批准 **阶段 1 (CacheManager 异步化)**，这是后续所有优化的基石。