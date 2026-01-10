## Context

Phase 5是MyStocks项目从开发环境迈向生产环境的关键阶段。基于已完成的基础设施（Phase 1-4），需要建立完整的：
1. 性能保障体系
2. 可观测性基础设施
3. 质量保障机制

### 关键约束
- 服务器资源：8核16G（K8s节点）
- 可用性目标：99.9%（月度故障≤43分钟）
- API性能：P95响应≤300ms
- 数据保留：Tick数据3个月，分钟级1年，日线永久

## Goals / Non-Goals

### Goals
1. 建立API性能基准与监控体系
2. 实现完整的可观测性栈（指标+日志+追踪）
3. 搭建E2E测试框架并覆盖80%核心场景
4. 提供K8s生产部署配置
5. 建立SLO/SLA指标与告警机制

### Non-Goals
- 容器化改造（非本次范围，保留pm2选项）
- 数据库架构重大重构
- 前端组件重写
- 新业务功能开发

## Decisions

### 1. 性能监控架构

#### Decision: 使用FastAPI中间件实现请求级性能监控

```python
# src/core/middleware/performance.py
from fastapi import Request, Response
from prometheus_client import Histogram, Counter, Gauge
import time

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP请求延迟(秒)',
    ['method', 'endpoint', 'status_code'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

REQUEST_COUNT = Counter(
    'http_requests_total',
    'HTTP请求总数',
    ['method', 'endpoint', 'status_code']
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    '当前活跃HTTP请求数',
    ['method', 'endpoint']
)
```

**Alternative considered**: 应用级APM工具（如SkyWalking）
- **Reason for selection**: 开源+轻量+集成成本低，更适合当前规模

### 2. 缓存策略

#### Decision: 三级缓存架构

| 层级 | 组件 | TTL | 适用场景 |
|------|------|-----|---------|
| L1 | 应用内存(Cache) | 60s | 高频访问数据 |
| L2 | Redis | 300s | 跨实例共享 |
| L3 | 数据库查询缓存 | 动态 | 复杂查询结果 |

```python
# src/core/cache/multi_level.py
class MultiLevelCache:
    async def get(self, key: str) -> Optional[Any]:
        # L1: 应用内存
        if key in self._memory_cache:
            return self._memory_cache[key]

        # L2: Redis
        value = await self._redis.get(key)
        if value:
            self._memory_cache[key] = value
        return value
```

### 3. 可观测性栈

#### Decision: Prometheus + Grafana + Loki + Tempo

| 组件 | 作用 | 数据类型 |
|------|------|---------|
| Prometheus | 指标收集 | 数值型指标 |
| Grafana | 可视化 | Dashboard |
| Loki | 日志聚合 | 结构化日志 |
| Tempo | 分布式追踪 | 链路数据 |

**Alternative considered**: ELK Stack
- **Reason for selection**: Loki更轻量，与Prometheus生态集成更好

### 4. E2E测试框架

#### Decision: Playwright + pytest + Testcontainers

```python
# tests/e2e/conftest.py
import pytest
from playwright.sync_api import Page

@pytest.fixture(scope="session")
def browser_context():
    return {
        'headless': True,
        'viewport': {'width': 1280, 'height': 720}
    }

@pytest.fixture
def authenticated_page(page: Page) -> Page:
    page.goto('/login')
    page.fill('#username', 'test_user')
    page.fill('#password', 'test_password')
    page.click('#login-btn')
    return page
```

### 5. API响应格式扩展

#### Decision: 新增performance字段

```typescript
// 响应格式扩展
interface ApiResponse<T> {
    code: number;
    data: T;
    msg: string;
    performance: {
        latency_ms: number;
        trace_id: string;
        cache_hit: boolean;
    };
}
```

## Risks / Trade-offs

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 监控数据量过大 | 存储成本增加 | 采样策略+保留策略 |
| 测试不稳定 | CI门禁失效 | 重试机制+截图报告 |
| 性能开销 | 监控本身影响性能 | 生产环境采样50% |
| 告警风暴 | 噪音过大 | 聚合告警+静默规则 |

## Migration Plan

### Phase 5.1: 基础监控
1. 添加Prometheus中间件
2. 配置基础指标暴露（/metrics）
3. 部署Grafana Dashboard

### Phase 5.2: 日志与追踪
1. 结构化日志改造
2. Loki部署与配置
3. Tempo链路追踪集成

### Phase 5.3: 性能优化
1. 缓存层实现
2. 数据库查询优化
3. API性能基准测试

### Phase 5.4: E2E测试
1. Playwright框架搭建
2. 核心场景测试开发
3. CI集成

### Rollback
- 监控中间件可独立禁用
- 缓存支持旁路模式
- 测试失败不影响部署

## Open Questions

1. ~~是否需要集成APM工具？~~ → 使用轻量级方案（中间件+Prometheus）
2. ~~E2E测试数据如何管理？~~ → 使用测试工厂+数据库初始化脚本
3. 告警通知渠道选择？ → 待定（可配置）
