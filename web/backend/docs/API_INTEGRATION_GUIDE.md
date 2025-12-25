# API-Web 对齐集成指南

## 📚 概述

本文档提供前后端集成的完整指南，包括统一响应格式、CSRF 保护、类型生成和最佳实践。

**版本**: v2.0.0
**日期**: 2025-12-24
**状态**: 生产就绪

---

## 🎯 统一响应格式 (UnifiedResponse v2.0.0)

### 响应结构

所有 API 端点返回统一的响应格式：

```typescript
interface UnifiedResponse<T = any> {
  success: boolean           // 操作是否成功
  code: number              // 业务状态码
  message: string           // 响应消息
  data?: T                  // 响应数据
  timestamp: string         // 时间戳
  request_id: string        // 请求ID
  errors?: ErrorDetail[]    // 错误详情（验证失败时）
}

interface ErrorDetail {
  field?: string            // 字段名
  code: string              // 错误码
  message: string           // 错误消息
}
```

### 业务状态码

| 代码 | 说明 | HTTP 状态码 |
|------|------|------------|
| 200 | 成功 | 200 |
| 400 | 错误请求 | 400 |
| 401 | 未授权 | 401 |
| 403 | 禁止访问 | 403 |
| 404 | 资源未找到 | 404 |
| 422 | 验证失败 | 422 |
| 429 | 请求过多 | 429 |
| 500 | 内部错误 | 500 |
| 502 | 网关错误 | 502 |
| 503 | 服务不可用 | 503 |

### 使用示例

**成功响应**:
```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "symbol": "600519",
    "name": "贵州茅台",
    "price": 1850.00
  },
  "timestamp": "2025-12-24T12:00:00Z",
  "request_id": "req_abc123"
}
```

**错误响应**:
```json
{
  "success": false,
  "code": 422,
  "message": "验证失败",
  "data": null,
  "timestamp": "2025-12-24T12:00:00Z",
  "request_id": "req_def456",
  "errors": [
    {
      "field": "symbol",
      "code": "INVALID_FORMAT",
      "message": "股票代码格式无效"
    }
  ]
}
```

---

## 🔒 CSRF 保护

### 前端集成

CSRF token 自动管理已在 `src/utils/request.ts` 中实现：

```typescript
import { getCSRFToken } from '@/utils/request'

// CSRF token 自动获取和刷新
// 1小时自动刷新
// 请求失败自动重试
```

### 使用方法

**方式 1: 使用 axios 实例** (推荐):
```typescript
import api from '@/api/market'

// CSRF token 自动添加到请求头
const response = await api.getMarketOverview()
```

**方式 2: 手动获取 token**:
```typescript
import { getCSRFToken } from '@/utils/request'

const token = await getCSRFToken()
fetch('/api/protected', {
  headers: {
    'X-CSRF-Token': token
  }
})
```

### 后端配置

CSRF 中间件已在 `app/middleware/csrf.py` 中实现：

- 公开端点自动豁免 (`/health`, `/docs`, `/api/csrf-token`)
- POST/PUT/DELETE 请求自动验证
- Token 过期时间: 1 小时

### 豁免端点配置

在 `app/middleware/csrf.py` 中添加豁免模式：

```python
CSRF_EXEMPT_PATTERNS = [
    r"^/api/public/",
    r"^/api/webhook/",
]
```

---

## 📝 TypeScript 类型生成

### 自动生成

从 Pydantic 模型自动生成 TypeScript 类型：

```bash
# 生成类型
python scripts/generate_frontend_types.py

# 输出文件
web/frontend/src/api/types/generated-types.ts
```

### 使用生成的类型

```typescript
import type { MarketOverviewResponse, RealTimeQuoteResponse } from '@/api/types/generated-types'

// 类型安全的 API 调用
const overview: MarketOverviewResponse = await api.getMarketOverview()
```

### 类型映射规则

| Pydantic | TypeScript |
|----------|------------|
| `str` | `string` |
| `int` | `number` |
| `float` | `number` |
| `bool` | `boolean` |
| `List[T]` | `T[]` |
| `Dict[K, V]` | `Record<K, V>` |
| `Optional[T]` | `T \| null` |
| `datetime` | `string` (ISO 8601) |
| `Field(default=...)` | 可选属性 |
| `Field(...)` | 必需属性 |

---

## 🔄 实时更新 (SSE)

### SSE 服务

Server-Sent Events 服务位于 `src/utils/sse.ts`：

```typescript
import { SSEClient } from '@/utils/sse'

const client = new SSEClient({
  url: '/api/market/realtime',
  filters: [
    { type: 'quote', channel: 'sh.600519' }
  ]
})

client.connect()
client.on('quote', (event) => {
  console.log('实时行情:', event.data)
})
```

### 特性

- ✅ 自动重连 (指数退避)
- ✅ 事件过滤和路由
- ✅ 心跳检测 (30s)
- ✅ 熔断器模式
- ✅ 连接池管理

### 后端 SSE 端点

```python
from fastapi import Response
from sse_starlette.sse import EventSourceResponse

@router.get("/market/realtime")
async def market_realtime():
    return EventSourceResponse(market_stream())
```

---

## 💾 智能缓存

### LRU 缓存

位于 `src/utils/cache.ts`：

```typescript
import { LRUCache } from '@/utils/cache'

const cache = new LRUCache({
  ttl: '5m',              // 5分钟过期
  maxSize: 100,           // 最多100条
  persistToStorage: true,  // 持久化到 LocalStorage
  refreshAhead: true      // 预刷新
})

// 设置缓存
await cache.set('market:overview', data, { ttl: '1h' })

// 获取缓存
const data = await cache.get('market:overview')

// 删除缓存
await cache.delete('market:overview')
```

### 缓存装饰器

```typescript
import { cached } from '@/utils/cache'

class MarketService {
  @cached({ ttl: '5m', key: 'market:overview' })
  async getOverview() {
    return await api.getMarketOverview()
  }
}
```

### 缓存统计

```typescript
const stats = cache.getStats()
console.log('命中率:', stats.hitRate)  // 0.95 = 95%
console.log('大小:', stats.size)
```

---

## ⚡ 性能优化

### 懒加载组件

```typescript
import { lazyLoad } from '@/utils/performance'

const HeavyComponent = lazyLoad(() => import('./Heavy.vue'), {
  loadingComponent: LoadingSpinner,
  errorComponent: ErrorDisplay,
  timeout: 5000
})
```

### 性能监控

```typescript
import { PerformanceMonitor } from '@/utils/performance'

const monitor = PerformanceMonitor.getInstance()

// 记录组件加载时间
monitor.recordComponentLoad('MarketDashboard', {
  loadTime: 150,
  bundleSize: 102400
})

// 获取性能指标
const metrics = monitor.getMetrics('MarketDashboard')
```

---

## 🛡️ 错误处理

### Error Boundary

```vue
<script setup lang="ts">
import { ErrorBoundary } from '@/utils/error-boundary'

const handleError = (error, info) => {
  console.error('组件错误:', error)
  // 上报错误
  errorReportingService.report(error, info)
}
</script>

<template>
  <ErrorBoundary :on-error="handleError">
    <YourComponent />
  </ErrorBoundary>
</template>
```

### 错误报告服务

```typescript
import { ErrorReportingService } from '@/utils/error-boundary'

const service = ErrorReportingService.getInstance()

// 报告错误
service.report(error, {
  componentName: 'MarketDashboard',
  severity: 'high',
  context: { userId: '123' }
})

// 获取错误统计
const reports = service.getErrorReports()
```

---

## 📡 API 调用示例

### 市场数据 API

```typescript
import api from '@/api/market'

// 获取市场概览
const overview = await api.getMarketOverview()

// 获取实时行情
const quote = await api.getRealTimeQuote('600519')

// 获取资金流向
const fundFlow = await api.getFundFlow({
  symbol: '600519',
  timeframe: '1d'
})
```

### 策略 API

```typescript
import api from '@/api/strategy'

// 运行策略
const result = await api.runStrategy({
  strategy_code: 'volume_surge',
  symbol: '600519'
})

// 获取策略结果
const results = await api.getStrategyResults({
  strategy_code: 'volume_surge',
  limit: 100
})
```

### 交易 API

```typescript
import api from '@/api/trade'

// 获取账户信息
const account = await api.getAccount()

// 获取持仓
const positions = await api.getPositions()

// 下单
const order = await api.placeOrder({
  symbol: '600519',
  side: 'buy',
  quantity: 100,
  price: 1850.00
})
```

---

## 🧪 测试指南

### 单元测试

```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MarketOverview from '@/views/MarketOverview.vue'

describe('MarketOverview', () => {
  it('renders market data', async () => {
    const wrapper = mount(MarketOverview)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.market-index').exists()).toBe(true)
  })
})
```

### 集成测试

```python
def test_market_overview():
    response = client.get("/api/market/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "data" in data
    assert "marketStats" in data["data"]
```

---

## 📊 监控和调试

### 请求追踪

每个请求都有 `request_id`，可用于追踪：

```typescript
try {
  const response = await api.getMarketOverview()
  console.log('Request ID:', response.request_id)
} catch (error) {
  console.error('Request ID:', error.request_id)
  // 使用 request_id 查找服务器日志
}
```

### 性能监控

响应头包含处理时间：

```typescript
const response = await api.getMarketOverview()
console.log('Process Time:', response.headers['x-process-time'])
// Output: "Process Time: 45.236ms"
```

### 健康检查

```bash
# 后端健康检查
curl http://localhost:8000/health

# API 健康检查
curl http://localhost:8000/api/market/health
curl http://localhost:8000/api/strategy/health
```

---

## 🚀 部署检查清单

### 后端

- [x] UnifiedResponse v2.0.0 实现完成
- [x] CSRF 保护中间件启用
- [x] 所有 API 端点使用统一格式
- [x] 测试覆盖率 > 80%
- [x] 文档更新完成

### 前端

- [x] Request infrastructure 配置
- [x] CSRF token 自动管理
- [x] TypeScript 类型生成
- [x] SSE 实时更新实现
- [x] 智能缓存配置
- [x] 性能优化实现
- [x] 错误处理集成

---

## 📚 相关文档

- [API 迁移指南](./API_MIGRATION_GUIDE.md)
- [测试指南](./E2E_TESTING_GUIDE.md)
- [密钥轮换指南](../../docs/guides/PHASE0_CREDENTIAL_ROTATION_GUIDE.md)

---

## 🆘 故障排除

### CSRF Token 错误

**问题**: `CSRF token validation failed`

**解决**:
1. 检查 `/api/csrf-token` 端点是否可访问
2. 清除 LocalStorage 中的旧 token
3. 确保请求头包含 `X-CSRF-Token`

### 响应格式错误

**问题**: `Cannot read property 'success' of undefined`

**解决**:
1. 检查后端是否使用 `create_unified_success_response`
2. 确认 ResponseFormatMiddleware 已启用
3. 查看浏览器控制台的完整错误

### SSE 连接失败

**问题**: SSE 连接频繁断开

**解决**:
1. 检查网络连接
2. 确认后端 SSE 端点正常
3. 查看客户端重连日志

---

**文档版本**: v2.0.0
**最后更新**: 2025-12-24
**维护者**: Backend Team
