# Redis 优化方案 Phase 1 验收与后续实施计划

**日期**: 2026-01-10
**状态**: ✅ Phase 1 完成 | 🔵 Phase 2/3 待启动
**相关文档**: `docs/reports/REDIS_THREE_DATABASE_OPTIMIZATION_PROPOSAL.md`

---

## 1. Phase 1 (CacheManager 异步化) 验收报告

经过代码审查与测试脚本分析，确认 **CacheManager 异步化与 Redis L2 集成** 已按计划完成。

### ✅ 核心成果
1.  **异步化改造**: `fetch_from_cache`, `write_to_cache`, `invalidate_cache` 已全面升级为 `async` 方法，消除了 FastAPI 环境下的 IO 阻塞风险。
2.  **三级缓存架构**: 成功构建了 `L1 (内存)` -> `L2 (Redis)` -> `L3 (TDengine)` 的数据流转路径。
    *   **读路径**: 内存未命中 -> 查 Redis -> 命中则回填内存。
    *   **写路径**: 同步写内存 -> 异步写 Redis -> 异步写 TDengine (Write-Through)。
3.  **平滑兼容**: 提供了 `get_cache_manager_async` 工厂方法，同时保留了同步的 `get_cache_manager` (带警告) 以兼容旧代码。
4.  **容错降级**: 实现了 `REDIS_CACHE_AVAILABLE` 检测，当 Redis 模块缺失或连接失败时，自动降级为 L1+L3 模式。

### 📊 代码审查要点
*   **文件**: `web/backend/app/core/cache_manager.py`
*   **关键逻辑**:
    ```python
    # L2: Redis缓存 (异步写入，不阻塞响应)
    if self._redis_available and self.redis_cache:
        redis_ttl = ttl_days * 24 * 3600
        asyncio.create_task(self.redis_cache.set(cache_key, cache_data, ttl=redis_ttl))
    ```
    *点评*: 使用 `asyncio.create_task` 处理写操作是一个很好的非阻塞实践。

---

## 2. 下一步优化计划 (Phase 2 & 3)

基于坚实的缓存基础，接下来的重点是**解决并发冲突**和**提升系统实时性**。

### 🚀 Phase 2: SmartScheduler 分布式锁集成 (高优先级)

**目标**: 彻底解决多实例部署时，同一指标被重复计算的问题。

#### 2.1 核心任务
1.  **引入 RedisLock**: 在 `SmartScheduler` 中集成 Redis 分布式锁服务。
2.  **实现 CLCC 模式**: 实现 "Check-Lock-Check-Compute" 双重检查锁逻辑。
3.  **改造计算流**:
    *   计算前先申请锁 `lock:calc:{stock}:{indicator}`。
    *   申请失败则等待并尝试读取缓存（而不是重复计算）。

#### 2.2 实施路径
*   **修改文件**: `web/backend/app/services/indicators/smart_scheduler.py`
*   **新增依赖**: `app.services.redis.redis_lock`
*   **关键代码预演**:
    ```python
    async def _calculate_single_with_lock(self, ...):
        # 1. 查缓存
        if cached := await self.redis_cache.get(key): return cached
        
        # 2. 抢锁
        async with self.redis_lock.lock(f"lock:{key}", timeout=60):
            # 3. 再查缓存 (防止等待锁期间已被计算)
            if cached := await self.redis_cache.get(key): return cached
            
            # 4. 计算并存缓存
            result = await self._compute(...)
            await self.redis_cache.set(key, result)
            return result
    ```

---

### 📡 Phase 3: 全链路事件驱动 (中优先级)

**目标**: 让前端能实时感知后台计算进度，告别轮询。

#### 3.1 核心任务
1.  **定义事件频道**: 规范 Redis Pub/Sub 频道命名 (e.g., `channel:task:progress`, `channel:market:update`)。
2.  **埋点改造**: 在 `daily_calculation` 任务的关键节点（开始、进度、完成、错误）植入事件发布代码。
3.  **WebSocket 对接**: 确保后端 WebSocket 服务能订阅这些频道并将消息推送到前端。

#### 3.2 实施路径
*   **修改文件**: `web/backend/app/services/indicators/jobs/daily_calculation.py`
*   **新增依赖**: `app.services.redis.redis_pubsub`
*   **数据流**:
    `Job (Worker)` -> `Redis Pub/Sub` -> `FastAPI (WebSocket)` -> `Vue Client`

---

## 3. 建议执行顺序

1.  **立即执行 Phase 2**: 分布式锁直接关系到计算资源的节省和系统稳定性，建议紧接着 Phase 1 进行。
2.  **随后执行 Phase 3**: 事件驱动能显著提升用户体验，可在后端逻辑稳定后实施。
3.  **清理工作**: 在确认所有业务都迁移到异步 CacheManager 后，移除旧的同步代码。
