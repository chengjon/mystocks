# Phase 2 验收与 Phase 3 优化建议报告

**日期**: 2026-01-10
**验收对象**: Redis Optimization Phase 2 - SmartScheduler Distributed Locking
**状态**: ✅ 验收通过

---

## 1. Phase 2 验收总结

经过对 `web/backend/app/services/indicators/smart_scheduler.py` 的代码审查，确认 Phase 2 已按计划高质量完成。

### ✅ 核心功能验证
*   **CLCC 模式 (Check-Lock-Check-Compute)**: 逻辑实现严谨。
    *   Check 1: 本地内存检查。
    *   Check 2: Redis 分布式缓存检查。
    *   Lock: 非阻塞锁获取。
    *   Check 3: 获取锁后再次检查 (Double-Check)，有效防止了竞态条件下的重复计算。
    *   Compute: 计算并回写 Redis 和本地缓存。
*   **优雅降级**: 完善的 `try-except` 和 `REDIS_LOCK_AVAILABLE` 检查，确保无 Redis 环境下系统仍能回退到本地模式运行，未破坏现有功能。
*   **资源命名**: `indicator:calc:{node_id}:{params_hash}` 命名规范清晰，避免了锁冲突。

### 🛡️ 代码质量
*   **结构清晰**: 新增方法 (`_calculate_single_with_lock`, `_perform_calculation`) 职责单一。
*   **兼容性**: `create_scheduler` 接口保持向下兼容，现有调用方无需修改。

---

## 2. Phase 3 (全链路事件驱动) 优化建议

基于 Phase 2 的坚实基础，针对即将进行的 Phase 3，提出以下优化建议以提升系统的性能和可维护性。

### 🚀 建议 1: 事件发布限流与批量化 (Throttling & Batching)
**现状风险**: 如果对 5000 只股票的每个指标都发送 Pub/Sub 消息，可能会产生数万条瞬时消息，造成 Redis 和 WebSocket 通道拥塞。
**优化方案**:
*   **按股票聚合**: 计算完一只股票的所有指标后，发送一条 `StockIndicatorsCalculated` 事件，而不是每个指标发一条。
*   **进度限流**: 任务进度的 `publish` 频率限制在每秒 1-2 次，或者每处理 1% 发布一次，避免刷屏。

### 📏 建议 2: 标准化事件模型 (Event Schema)
**现状风险**: 使用散乱的 `dict` 作为消息体，前端难以维护类型定义。
**优化方案**:
*   定义 Pydantic 模型作为事件 Payload。
    ```python
    class TaskProgressEvent(BaseModel):
        task_id: str
        status: str
        progress: float
        message: str
    ```
*   确保所有发布的事件都经过模型验证。

### 📡 建议 3: 频道命名层级化 (Hierarchical Channels)
**优化方案**:
*   设计清晰的频道结构，支持前端按需订阅。
    *   全局任务广播: `events:tasks` (所有任务状态)
    *   特定任务详情: `events:task:{task_id}`
    *   实时行情推送: `events:market:{stock_code}`

### 🔌 建议 4: WebSocket 连接管理
**优化方案**:
*   在后端实现 WebSocket 的 **Connection Manager**，支持：
    *   按用户/Session 广播。
    *   心跳检测 (Heartbeat) 保持连接活跃。
    *   异常断开后的资源清理。

---

**下一步行动**:
建议采纳上述优化建议，并在 Phase 3 的实施计划中予以体现。
