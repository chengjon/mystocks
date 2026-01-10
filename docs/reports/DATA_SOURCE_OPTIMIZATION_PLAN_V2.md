# 数据源管理与数据治理模块优化方案 V2

**文档类型**: 技术优化提案 (修正版)
**创建时间**: 2026-01-09
**版本**: v2.0
**作者**: Claude Code (Data Management Expert)
**状态**: 待审批

---

## 📋 目录

1. [执行摘要](#执行摘要)
2. [关键架构调整 (V2)](#关键架构调整-v2)
3. [详细设计方案](#详细设计方案)
4. [实施路线图](#实施路线图)
5. [预期收益](#预期收益)

---

## 执行摘要

本提案是基于 V1 版本的深度优化，针对 MyStocks 现有的架构（FastAPI + Gunicorn/Uvicorn, 同步/异步混合模式）进行了技术可行性修正。

### 🎯 核心目标修正

- **稳定性**: 确保多线程/多进程环境下的线程安全 (V1 遗漏点)
- **兼容性**: 适配现有的 Prometheus 监控体系，避免端口冲突
- **实用性**: 简化缓存实现，优先保证数据一致性

---

## 关键架构调整 (V2)

| 功能模块 | V1 提案 | **V2 优化方案** | 原因 |
|:---|:---|:---|:---|
| **缓存机制** | `asyncio` 异步刷新 | **同步 TTL + 线程池预热** | 现有 `DataSourceManagerV2` 为同步代码，强行引入 async 会导致传染性改造风险。 |
| **熔断器** | 基础实现 (非线程安全) | **线程安全实现 (`threading.Lock`)** | 防止高并发下的状态竞争 (Race Condition)。 |
| **监控** | 独立 HTTP Server (9091) | **集成现有 FastAPI `/metrics`** | 避免端口冲突，统一运维入口。 |
| **批处理** | `ThreadPoolExecutor` | **`ThreadPoolExecutor` + 队列缓冲** | 保持与现有同步架构的兼容性，同时利用 I/O 并发。 |

---

## 详细设计方案

### 1. 智能缓存 (SmartCache) - 同步线程安全版

**设计变更**: 移除 `async/await`，使用 `threading.Timer` 或在读取时触发后台线程更新。

```python
from collections import OrderedDict
from datetime import datetime
import threading
from typing import Any, Optional, Dict
import logging

logger = logging.getLogger(__name__)

class SmartCache:
    """
    智能缓存 (线程安全版)
    特性：LRU + TTL + 后台预热
    """

    def __init__(self, maxsize: int = 100, ttl: int = 3600, refresh_ratio: float = 0.8):
        self.maxsize = maxsize
        self.ttl = ttl
        self.refresh_ratio = refresh_ratio
        
        self.cache = OrderedDict()
        self.metadata = {}
        self.lock = threading.RLock()  # 读写锁
        self.refreshing = set()  # 正在刷新的key集合

    def get(self, key: str, refresher: callable = None) -> Optional[Any]:
        with self.lock:
            if key not in self.cache:
                return None
            
            self.cache.move_to_end(key)
            
            # 检查 TTL
            if self._is_expired(key):
                # 如果过期，尝试触发刷新，但暂时返回旧数据（软过期）或 None（硬过期）
                # 这里采用软过期策略，并触发后台刷新
                if refresher and key not in self.refreshing:
                    self._trigger_refresh(key, refresher)
                
                logger.warning(f"Cache stale: {key}, returning stale data")
                return self.cache[key]
            
            # 检查预热
            if refresher and self._should_refresh(key) and key not in self.refreshing:
                self._trigger_refresh(key, refresher)

            return self.cache[key]

    def set(self, key: str, value: Any):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            
            self.cache[key] = value
            self.metadata[key] = {
                "created_at": datetime.now(),
                "last_accessed": datetime.now()
            }
            
            # 清理正在刷新标记
            if key in self.refreshing:
                self.refreshing.remove(key)
            
            # LRU 淘汰
            if len(self.cache) > self.maxsize:
                popped, _ = self.cache.popitem(last=False)
                if popped in self.metadata:
                    del self.metadata[popped]

    def _trigger_refresh(self, key: str, refresher: callable):
        """启动后台线程刷新缓存"""
        self.refreshing.add(key)
        threading.Thread(target=self._run_refresh, args=(key, refresher), daemon=True).start()

    def _run_refresh(self, key: str, refresher: callable):
        try:
            new_value = refresher()
            self.set(key, new_value)
        except Exception as e:
            logger.error(f"Cache refresh failed for {key}: {e}")
            with self.lock:
                if key in self.refreshing:
                    self.refreshing.remove(key)

    def _is_expired(self, key: str) -> bool:
        if key not in self.metadata: return True
        return (datetime.now() - self.metadata[key]["created_at"]).total_seconds() > self.ttl

    def _should_refresh(self, key: str) -> bool:
        if key not in self.metadata: return False
        elapsed = (datetime.now() - self.metadata[key]["created_at"]).total_seconds()
        return elapsed > (self.ttl * self.refresh_ratio)
```

### 2. 熔断器 (Circuit Breaker) - 线程安全版

**设计变更**: 增加 `threading.Lock` 保护状态转换。

```python
import threading
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.lock = threading.Lock()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = 0

    def call(self, func, *args, **kwargs):
        # 1. 检查状态 (加锁)
        with self.lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = CircuitState.HALF_OPEN
                    # 允许通过，进行试探
                else:
                    raise Exception("Circuit Breaker is OPEN")
        
        # 2. 执行调用 (释放锁，避免阻塞)
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            self._handle_failure()
            raise e
        
        # 3. 成功回调
        self._handle_success()
        return result

    def _handle_success(self):
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0

    def _handle_failure(self):
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
            elif self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
```

### 3. 监控体系 (Metrics) - 集成现有 Prometheus

**设计变更**:
- 移除 `start_http_server(9091)`。
- 使用 `prometheus_client` 的全局 Registry，或者复用应用现有的 Registry。
- 确保指标名称符合 Prometheus 命名规范 (Snake Case)。

```python
from prometheus_client import Histogram, Counter

# 定义全局指标 (单例模式)
METRICS = {
    "latency": Histogram(
        'datasource_api_latency_seconds',
        'API call latency',
        ['source', 'endpoint', 'status']
    ),
    "calls": Counter(
        'datasource_api_calls_total',
        'Total API calls',
        ['source', 'endpoint', 'status']
    )
}

# 装饰器直接引用全局指标
def track_api_call(source: str, endpoint: str):
    def decorator(func):
        # ... (同 V1，但使用全局 METRICS)
        pass
    return decorator
```

### 4. 批处理 (Batch Processing)

**设计变更**: 明确与 `DataSourceManager` 的集成方式。

- `DataSourceManager` 保持同步 API。
- `GovernanceDataFetcher` 使用 `ThreadPoolExecutor` 并发调用 `DataSourceManager.fetch`。
- 不修改 `DataSourceManager` 内部逻辑，而是在**调用层**进行并发优化。

---

## 实施路线图

### 第一阶段：核心稳定性 (1周)
1.  **SmartCache 实现**: 替换现有的简单 `LRUCache`。重点测试 TTL 和并发安全性。
2.  **CircuitBreaker 集成**: 为每个外部 API 端点包装熔断器。

### 第二阶段：可观测性 (1周)
1.  **Metrics埋点**: 在 `DataSourceManagerV2._call_endpoint` 中添加 Prometheus 埋点。
2.  **Grafana 面板**: 更新现有的 Grafana 配置，添加数据源专用面板。

### 第三阶段：吞吐量优化 (2周)
1.  **DataGovernance 批处理**: 改造 `GovernanceDataFetcher`，使用 `ThreadPoolExecutor` 并行获取多只股票数据。

---

## 预期收益

与 V1 相比，V2 方案更加务实和安全：
- **零风险**: 避免了在同步代码库中混用 Async 的死锁风险。
- **易运维**: 不需要管理额外的监控端口。
- **高可用**: 线程安全的实现保证了生产环境的稳定性。
