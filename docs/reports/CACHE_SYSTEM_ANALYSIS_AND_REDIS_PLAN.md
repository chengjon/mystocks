# 缓存系统分析与 Redis 集成方案

**日期**: 2026-01-10
**版本**: V1.0
**状态**: 规划中

---

## 1. 现有缓存系统深度分析

### 1.1 现状架构
项目目前采用 **L1 内存 + L2 TDengine** 的混合缓存策略，核心逻辑位于 `web/backend/app/core/cache_manager.py`。

*   **L1 内存缓存**: 基于 Python 字典 (`dict`)，进程隔离，受限于单机内存。
*   **L2 持久化缓存**: 基于 TDengine 时序数据库，用于存储非实时但需持久化的数据（如 K 线、资金流向）。
*   **失效策略**: 支持 TTL (Time-To-Live) 和 LRU (Least Recently Used) 淘汰。

### 1.2 关键瓶颈 (Bottlenecks)
1.  **进程隔离 (Process Isolation)**: FastAPI/Uvicorn 多进程部署时，各进程缓存不共享。导致内存浪费（相同数据存多份）和数据不一致（进程 A 更新缓存，进程 B 仍读旧数据）。
2.  **高并发击穿**: 服务重启后，内存缓存清空。TDengine 虽然快，但相比 Redis (内存 KV) 仍有数量级的延迟差异 (ms vs µs)，高并发下可能导致数据库压力过大。
3.  **缺乏实时能力**: 现有架构无法支持 Pub/Sub (发布/订阅) 模式，难以支撑 V2 架构中的 WebSocket 实时行情推送。
4.  **分布式锁缺失**: 定时任务 (`SmartScheduler`) 在多实例部署时缺乏协调机制，容易重复执行。

### 1.3 双数据库 + GPU 支撑能力评估
*   **结论**: 无法替代 Redis。
*   **原因**:
    *   **GPU**: 负责计算而非存储。Redis 应作为 GPU 计算结果的缓冲区，避免重复计算。
    *   **TDengine**: 擅长时序聚合，不擅长高频 Key-Value 读取和分布式协调。

---

## 2. Redis 集成计划 (Redis Integration Plan)

本计划旨在引入 Redis 作为 **L2 共享缓存层**，构建 `L1(本地内存) -> L2(Redis) -> L3(TDengine) -> Source` 的多级缓存体系。

### 2.1 环境配置准备

基于项目 `.env` 和 `config.py` 的现有结构，利用以下配置：

**环境变量 (`.env`)**:
```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_USE_SSL=False

# Toggle
ENABLE_REDIS_CACHE=True
```

**配置映射 (`app/core/config.py`)**:
*   复用现有的 `Settings` 类，增加 Redis 专用字段，确保与 Celery 配置解耦（虽然 Celery 也用 Redis，但建议业务缓存用独立的 DB index）。

### 2.2 实施路线图 (Roadmap)

#### Phase 1: 基础设施建设 (Infrastructure)
*   **目标**: 建立异步 Redis 连接池，确保 FastAPI 生命周期管理。
*   **依赖**: `redis-py` (支持 asyncio).
*   **任务**:
    1.  安装依赖: `pip install redis[hiredis]`
    2.  创建 `web/backend/app/core/redis_pool.py`: 实现单例连接池。
    3.  更新 `main.py`: 在 `lifespan` 中初始化和关闭 Redis 连接。

#### Phase 2: CacheManager 重构 (Refactoring)
*   **目标**: 将 Redis 插入现有缓存逻辑。
*   **变更**:
    1.  **异步化**: 将 `fetch_from_cache` 和 `write_to_cache` 改造为 `async` 方法 (必要，因为 Redis I/O 是异步的)。
    2.  **序列化**: 实现 `JSON` 或 `MsgPack` 序列化，将 Python 对象转为 Redis String。
    3.  **逻辑升级**:
        *   *Read*: 查内存 -> (未命中) -> **查 Redis** -> (未命中) -> 查 TDengine/DB -> **回写 Redis** -> 回写内存。
        *   *Write*: 写内存 -> **写 Redis (设置 TTL)** -> 异步写 TDengine。
        *   *Delete*: 删内存 -> **删 Redis** -> 删 TDengine。

#### Phase 3: 高级功能实现 (Advanced Features)
*   **目标**: 赋能业务系统。
*   **任务**:
    1.  **分布式锁**: 为 `SmartScheduler` 实现 `RedisLock`，防止任务重入。
    2.  **实时推送**: 利用 Redis Pub/Sub 实现指标计算完成后的消息广播，WebSocket 服务订阅该频道并推送给前端。

---

## 3. 技术方案详解 (Technical Design)

### 3.1 Redis 连接池实现 (`app/core/redis_pool.py`)

```python
import redis.asyncio as redis
from app.core.config import settings

class RedisManager:
    _pool: redis.Redis = None

    @classmethod
    async def init(cls):
        if not settings.enable_cache:
            return
        cls._pool = redis.Redis(
            host=settings.redis_host, # 假设config已更新
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            encoding="utf-8",
            decode_responses=True
        )

    @classmethod
    async def get_client(cls) -> redis.Redis:
        return cls._pool

    @classmethod
    async def close(cls):
        if cls._pool:
            await cls._pool.close()
```

### 3.2 缓存键设计 (Key Naming)

采用冒号分隔的命名空间，防止冲突：

| 数据类型 | Key 格式 | 示例 | TTL |
| :--- | :--- | :--- | :--- |
| **实时行情** | `quote:{symbol}` | `quote:000001` | 5s |
| **技术指标** | `ind:{symbol}:{indicator}:{freq}` | `ind:000001:macd:1d` | 1h |
| **K线数据** | `kline:{symbol}:{freq}` | `kline:000001:15m` | 15m |
| **分布式锁** | `lock:{task_name}` | `lock:daily_calc` | 自动过期 |

### 3.3 序列化策略

为了兼顾性能和可读性，建议使用 `orjson`：

```python
import orjson

def serialize(obj):
    return orjson.dumps(obj)

def deserialize(data):
    return orjson.loads(data)
```

---

## 4. 预期收益 (Expected Benefits)

| 指标 | 引入前 | 引入 Redis 后 |
| :--- | :--- | :--- |
| **L2 缓存读取延迟** | 10ms - 50ms (TDengine) | **< 1ms** |
| **进程间数据共享** | 无 (各自为政) | **完美支持** |
| **重启缓存保留** | 0% (全丢失) | **100%** (Redis 持久化) |
| **实时推送延迟** | 轮询 (秒级延迟) | **事件驱动 (毫秒级)** |
| **系统吞吐量** | 受限于 DB 连接数 | **提升 5-10 倍** |

---

## 5. 立即执行计划 (Immediate Actions)

1.  **修改配置**: 更新 `web/backend/app/core/config.py`，加入 Redis 配置项。
2.  **安装驱动**: 添加 `redis` 到依赖列表。
3.  **编写连接池**: 实现 `RedisManager`。
4.  **改造缓存管理器**: 逐步将 `CacheManager` 升级为异步并接入 Redis。
