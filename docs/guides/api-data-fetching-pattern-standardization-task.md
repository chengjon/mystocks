# 前端路由优化 - API数据获取模式标准化任务方案

## 任务概述

**任务名称**: API数据获取模式标准化和增强
**优先级**: 高
**预计时间**: 4-6小时
**风险等级**: 中等（涉及多个API文件的重构）
**依赖项**: 现有的API文件，缓存管理器，错误处理机制

## 任务背景

当前前端API调用存在以下问题：
- **不一致的缓存策略**: 部分API使用缓存，部分不使用
- **缺失的错误处理**: 没有统一的错误处理和重试机制
- **重复的代码模式**: 每个API都有类似的错误处理逻辑
- **缺乏加载状态管理**: 没有统一的loading状态管理
- **缓存策略不统一**: 不同的API使用不同的缓存时间和策略

目标：创建统一的API数据获取模式，提供一致的缓存、错误处理、加载状态和重试机制。

## 当前状态分析

### 现有API调用模式

**模式A: 带缓存的调用 (推荐)**
```javascript
async getStocksBasic(params) {
  return cacheManager.withCache(
    () => request.get('/v1/data/stocks/basic', { params }),
    'stocks_basic',
    params,
    300000 // 5分钟缓存
  )
}
```

**模式B: 直接调用 (问题多)**
```javascript
async getAlertRules() {
  return request.get('/v1/monitoring/alert-rules')
}
```

**模式C: 自定义缓存 (不一致)**
```javascript
// 各种不同的缓存实现
```

### 存在的问题

1. **缓存策略不一致**: 有些API有缓存，有些没有
2. **错误处理缺失**: 没有统一的错误处理、重试机制
3. **加载状态缺失**: 无法显示loading状态
4. **代码重复**: 每个API都要写类似的错误处理
5. **维护困难**: 修改缓存策略需要修改多个文件

## 实施步骤

### 步骤1: 创建统一的API客户端
**目标**: 创建一个统一的API客户端，提供标准化的数据获取模式
**文件位置**: `web/frontend/src/api/apiClient.ts` (新建)
**功能特性**:

```typescript
class ApiClient {
  // 统一的API调用方法
  async call<T>(
    config: {
      method: 'GET' | 'POST' | 'PUT' | 'DELETE'
      url: string
      params?: any
      data?: any
      cache?: {
        enabled: boolean
        key: string
        ttl: number
        strategy: 'memory' | 'localStorage' | 'sessionStorage'
      }
      retry?: {
        enabled: boolean
        maxAttempts: number
        delay: number
      }
      loading?: {
        enabled: boolean
        key?: string
      }
    }
  ): Promise<T>

  // 便捷方法
  get<T>(url: string, config?: Partial<ApiConfig>) => Promise<T>
  post<T>(url: string, data?: any, config?: Partial<ApiConfig>) => Promise<T>
  put<T>(url: string, data?: any, config?: Partial<ApiConfig>) => Promise<T>
  delete<T>(url: string, config?: Partial<ApiConfig>) => Promise<T>
}
```

### 步骤2: 实现缓存策略标准化
**目标**: 统一缓存策略配置
**配置标准**:

```typescript
// 数据类型缓存策略
const CACHE_STRATEGIES = {
  // 实时数据 - 短缓存，高频更新
  realtime: { ttl: 30000, strategy: 'memory' }, // 30秒

  // 频繁查询数据 - 中等缓存
  frequent: { ttl: 300000, strategy: 'memory' }, // 5分钟

  // 静态参考数据 - 长缓存
  reference: { ttl: 3600000, strategy: 'localStorage' }, // 1小时

  // 历史数据 - 超长缓存
  historical: { ttl: 86400000, strategy: 'localStorage' }, // 24小时

  // 用户数据 - 会话缓存
  user: { ttl: 1800000, strategy: 'sessionStorage' }, // 30分钟
}
```

### 步骤3: 实现统一的错误处理
**目标**: 标准化错误处理和用户反馈
**错误处理策略**:

```typescript
class ApiErrorHandler {
  static handle(error: any, context: string) {
    // 网络错误
    if (!error.response) {
      return this.handleNetworkError(error, context)
    }

    // HTTP错误
    switch (error.response.status) {
      case 400: return this.handleBadRequest(error, context)
      case 401: return this.handleUnauthorized(error, context)
      case 403: return this.handleForbidden(error, context)
      case 404: return this.handleNotFound(error, context)
      case 500: return this.handleServerError(error, context)
      default: return this.handleUnknownError(error, context)
    }
  }

  // 用户友好的错误消息
  static getUserFriendlyMessage(error: any): string {
    // 根据错误类型返回用户友好的消息
  }
}
```

### 步骤4: 实现加载状态管理
**目标**: 提供统一的加载状态管理
**实现方式**:

```typescript
// 全局加载状态store
const useLoadingStore = defineStore('loading', () => {
  const loadingStates = ref(new Map<string, boolean>())

  const isLoading = (key: string) => loadingStates.value.get(key) || false
  const setLoading = (key: string, loading: boolean) => {
    loadingStates.value.set(key, loading)
  }

  return { isLoading, setLoading }
})

// 在组件中使用
const loadingStore = useLoadingStore()
const isLoadingStocks = computed(() => loadingStore.isLoading('stocks'))
```

### 步骤5: 实现重试机制
**目标**: 为关键API提供自动重试功能
**重试策略**:

```typescript
class RetryHandler {
  static async withRetry<T>(
    operation: () => Promise<T>,
    config: {
      maxAttempts: number
      delay: number
      backoffFactor: number
      retryCondition: (error: any) => boolean
    }
  ): Promise<T> {
    // 实现指数退避重试逻辑
  }
}
```

### 步骤6: 重构现有API文件
**目标**: 将所有API调用迁移到新的标准化模式
**重构策略**:

```typescript
// 重构前
async getStocksBasic(params) {
  return cacheManager.withCache(
    () => request.get('/v1/data/stocks/basic', { params }),
    'stocks_basic',
    params,
    300000
  )
}

// 重构后
async getStocksBasic(params) {
  return apiClient.get('/v1/data/stocks/basic', {
    params,
    cache: {
      enabled: true,
      key: 'stocks_basic',
      strategy: CACHE_STRATEGIES.frequent
    },
    loading: { enabled: true, key: 'stocks-basic' },
    retry: { enabled: true, maxAttempts: 3 }
  })
}
```

### 步骤7: 更新类型定义
**目标**: 为新的API客户端提供完整的TypeScript支持
**类型定义**:

```typescript
interface ApiConfig {
  cache?: CacheConfig
  retry?: RetryConfig
  loading?: LoadingConfig
  timeout?: number
}

interface CacheConfig {
  enabled: boolean
  key: string
  ttl: number
  strategy: 'memory' | 'localStorage' | 'sessionStorage'
}

interface RetryConfig {
  enabled: boolean
  maxAttempts: number
  delay: number
  backoffFactor: number
}

interface LoadingConfig {
  enabled: boolean
  key: string
}
```

## 测试验证

### 单元测试
- [ ] ApiClient 基本功能测试
- [ ] 缓存策略正确性测试
- [ ] 错误处理测试
- [ ] 重试机制测试

### 集成测试
- [ ] 现有API功能保持不变
- [ ] 缓存行为正确
- [ ] 错误场景处理正确
- [ ] 加载状态正确更新

### 性能测试
- [ ] 缓存命中率测试
- [ ] API响应时间测试
- [ ] 内存使用测试

## 风险评估和应对

### 风险1: 重构范围过大
**影响**: 可能引入新的bug，影响现有功能
**应对**:
- 分批重构，按模块进行
- 保留原有API作为fallback
- 充分的测试覆盖

### 风险2: 缓存策略不当
**影响**: 可能导致数据不一致或性能问题
**应对**:
- 谨慎设计缓存策略
- 提供缓存失效机制
- 监控缓存命中率

### 风险3: 类型安全问题
**影响**: TypeScript类型定义可能不完整
**应对**:
- 逐步完善类型定义
- 使用严格的TypeScript配置
- 运行时类型验证

## 验收标准

### 功能验收
- [ ] 所有API调用使用统一的客户端
- [ ] 缓存策略配置正确
- [ ] 错误处理统一且用户友好
- [ ] 加载状态正确管理
- [ ] 重试机制对关键API生效

### 性能验收
- [ ] API响应时间不超过原有系统的110%
- [ ] 缓存命中率超过70%
- [ ] 内存使用控制在合理范围内

### 代码质量验收
- [ ] TypeScript类型完整
- [ ] 单元测试覆盖率超过80%
- [ ] 代码重复度低于15%

## 后续优化机会

**此任务完成后可以进行的优化**:
- 实现API响应压缩
- 添加请求取消机制
- 实现乐观更新
- 添加API监控和分析
- 实现离线支持

---

*文档创建时间*: 2026-01-12
*预计完成时间*: 2026-01-13 (6小时内)
*负责人*: Claude Code
*审查人*: 项目维护者