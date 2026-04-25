# Pinia API Standardization Guide

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

> **文档边界说明**:
> 本文用于说明当前仓库中 Pinia API 标准化模式的推荐用法、迁移步骤与验证要求，不是仓库共享规则或运行时事实的唯一来源。
> 执行前请同时核对 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)、[`openspec/specs/api-integration/spec.md`](/opt/claude/mystocks_spec/openspec/specs/api-integration/spec.md)、当前代码与最新验证结果。

## 1. Canonical Files

| Concern | Canonical File | Notes |
| --- | --- | --- |
| Store factory | `web/frontend/src/stores/storeFactory.ts` | 统一 `data/loading/error/lastFetch/requestCount/errorCount/lastDurationMs/averageDurationMs` |
| Shared policies | `web/frontend/src/stores/storePolicies.ts` | 统一 capability、cache TTL、refresh、realtime channel |
| Pilot stores | `web/frontend/src/stores/apiStores.ts` | `trading-signals`、`risk-alerts`、`user-watchlists`、`technical-indicators` |
| Auth migration example | `web/frontend/src/stores/auth.ts` | 表单登录通过 `request` executor 接入 factory |
| Strategy migration example | `web/frontend/src/stores/strategy.ts` | 兼容旧 outward API，同时内部改为 standardized fetch path |
| Store composition | `web/frontend/src/stores/storeComposition.ts` | 聚合多 store 的 loading/error/fetch 状态 |
| Runtime inspector | `web/frontend/src/views/system/API.vue` | 开发态检查 capability、realtime、store runtime 指标 |

## 2. Core Principles

1. 新的 API store 默认通过 `PiniaStoreFactory` 创建，不再在视图里直接拼接 `loading/error/cache` 逻辑。
2. cache TTL、refresh 间隔、realtime channel 优先放进 `frontendStorePolicies`，避免散落在页面或 service。
3. 兼容迁移允许保留旧 store outward API，但内部 fetch 路径应收敛到 factory。
4. 运行态指标必须复用真实 store 状态，不得为 inspector 单独维护一份平行数据。
5. verified 页面不得对同一路径静默回退 mock；mock 只允许走显式 mock path。

## 3. Standard Patterns

### 3.1 Basic API Store

适用于普通 `GET/POST` 数据获取：

```ts
export const useExampleStore = PiniaStoreFactory.createApiStore({
  id: 'example-capability',
  endpoint: '/api/example',
  method: 'GET',
  cache: frontendStorePolicies.example.cache,
  loading: { enabled: true, key: frontendStorePolicies.example.loadingKey },
})
```

适用场景：
- 单次拉取
- TTL 缓存
- 标准错误与耗时指标

### 3.2 Realtime Store

适用于 API + WebSocket 混合能力：

```ts
export const useTradingSignalsStore = PiniaStoreFactory.createRealtimeStore({
  id: frontendStorePolicies.tradingSignals.capability,
  endpoint: '/api/trading/signals',
  cache: frontendStorePolicies.tradingSignals.cache,
  loading: { enabled: true, key: frontendStorePolicies.tradingSignals.loadingKey },
  wsManager: tradingWebSocket,
  wsChannel: frontendStorePolicies.tradingSignals.realtime?.channel,
  updateInterval: frontendStorePolicies.tradingSignals.refresh.updateInterval,
})
```

要求：
- realtime store 必须保留 base store 的响应式状态，不能通过对象展开把 `requestCount/lastFetch` 等指标变成静态快照
- WebSocket 失败时允许 fallback 到 polling

### 3.3 Paginated Store

适用于分页拉取：

```ts
export const useTradingHistoryStore = PiniaStoreFactory.createPaginatedStore({
  id: 'trading-history',
  endpoint: '/api/trading/history',
  pageSize: 20,
  cache: { enabled: true, key: 'trading-history', ttl: 600000, strategy: 'memory' },
  loading: { enabled: true, key: 'trading-history-loading' },
})
```

要求：
- `fetchPage()` 仍然要更新统一请求指标
- 分页状态与 base store 状态必须同时保持响应式

### 3.4 Custom Request Executor

适用于登录表单、特殊 payload 或不适合直接复用统一 `GET/POST` 分支的接口：

```ts
const useLoginStore = PiniaStoreFactory.createApiStore({
  id: 'auth-login',
  endpoint: '/v1/auth/login',
  method: 'POST',
  request: (params) => authApi.login(params.username, params.password),
  transform: (payload) => payload?.data ?? payload,
})
```

要求：
- 特殊接口仍然复用统一 loading/error/metrics
- `request` 只替代 transport，不替代标准化状态管理

### 3.5 Store Composition

适用于页面同时依赖多个 pilot store：

```ts
const composition = useStoreComposition({
  signals: useTradingSignalsStore(),
  alerts: useRiskAlertsStore(),
  watchlists: useWatchlistsStore(),
})
```

可聚合：
- `isLoading`
- `hasErrors`
- `errors`
- `latestFetch`
- `refreshAll()`

## 4. Migration Steps

### 4.1 从“视图里直接调 API”迁移

1. 把 endpoint、cache TTL、refresh 频率登记到 `storePolicies.ts`
2. 用 `createApiStore/createRealtimeStore/createPaginatedStore` 创建 store
3. 视图改为消费 store 状态，不再自行维护重复的 `loading/error/lastFetch`
4. 若旧调用方较多，先保留 outward API，再把内部 fetch 逻辑切到 factory

### 4.2 从“旧 store 手写 fetch”迁移

1. 保留现有 store id 和 outward actions，先避免调用方断裂
2. 把真实请求抽到 factory store
3. 用 wrapper store 同步 `data/loading/error/lastFetch`
4. 补齐兼容测试，确认旧调用方式未回归

`auth.ts` 与 `strategy.ts` 是当前仓库的两个参考实现：
- `auth.ts`: 保持 `useAuthStore` outward API，同时把登录请求收敛到 factory
- `strategy.ts`: 保持业务 store 结构，同时把 strategy management 拉取改为 standardized path

## 5. Verification Requirements

至少覆盖三层：

1. Unit
   - `web/frontend/src/stores/__tests__/store-factory.spec.ts`
   - `web/frontend/src/stores/__tests__/store-composition.spec.ts`
2. Integration
   - `web/frontend/src/stores/__tests__/api-stores.spec.ts`
   - `web/frontend/src/stores/__tests__/strategy-store.spec.ts`
   - `web/frontend/src/stores/__tests__/auth-guard.spec.ts`
3. E2E
   - `web/frontend/tests/e2e/system-api-store-governance.spec.ts`

当前这组标准化至少应验证：
- factory store 的统一状态与指标
- custom request executor
- realtime / paginated store 的响应式指标不丢失
- wrapper store 兼容迁移
- `/system/api` inspector 能展示真实 store runtime 指标

## 6. Anti-Patterns

- 不要在页面里重复维护第二份 `loading/error/requestCount`
- 不要把 policy 值散落在多个 view/service/store 常量里
- 不要通过对象展开复制内部 Pinia store，再把响应式状态变成快照
- 不要让 verified 页面在同一路径静默回退到 mock
- 不要只勾选 OpenSpec 任务而没有测试或代码事实支撑
