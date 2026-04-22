# MyStocks 前端架构优化提案（借鉴 Fincept 模式，按现有栈增量收敛）

> 参考来源：`/opt/claude/FinceptTerminal/docs/WEB_ARCHITECTURE_REFERENCE.md`
>
> 生成日期：2026-04-22
> 状态：待评审
> 执行前提：本提案仅用于审批，不代表已获准实施。任何代码改动仍需遵循 `architecture/STANDARDS.md` 的 Proposal-First Rule。
>
> 对应 OpenSpec change:
> `openspec/changes/update-frontend-data-governance-with-fincept-patterns/`

---

## 一、提案目标

在不引入第二套前端架构、不推翻现有 `apiClient + service + PiniaStoreFactory + WebSocket/SSE` 体系的前提下，借鉴 Fincept 中适合 Web 端的五个工程优势，解决以下问题：

1. Service 层存在局部静默失败，调用方难以区分“空数据”与“请求失败”。
2. 实时流更新缺少统一的合并窗口，存在高频更新直接触发响应式刷新的风险。
3. 缓存 TTL / 轮询间隔已有集中能力，但配置入口不统一，部分页面仍靠局部硬编码维持。

本提案的核心原则：

- 只做增量收敛，不另起 DataHub、Topic Router、全局事件总线等并行体系。
- 优先复用现有真相源：`apiClient`、`dashboardService`、`PiniaStoreFactory`、现有 WebSocket/SSE composable。
- 每个阶段都必须独立可交付、可验证、可停止。

---

## 二、当前架构与问题定位

### 2.1 当前前端主链路

当前前端并非单一路径，而是两条并存但可收敛的主链路：

```text
Route View
  ├─ view-local composable
  │   └─ service (src/api/services/*.ts)
  │       └─ apiClient
  │           └─ FastAPI
  └─ PiniaStoreFactory store
      ├─ apiClient / unifiedApiClient bridge
      └─ WebSocket polling fallback / cache
```

与本提案直接相关的现状：

- `dashboardService.getTechnicalIndicators()` 仍存在 `.catch(() => {})` 静默吞错。
- `PiniaStoreFactory.createRealtimeStore()` 已具备缓存、WebSocket、轮询 fallback 的统一能力。
- 仓库已有 `useWebSocketEnhanced.ts`、`useRealtimeMarket.ts`、`useSSE.js` 等流式消费入口。
- 仓库已有 `web/frontend/src/api/types/` 目录，不宜再新建平级 `src/api/types.ts` 作为第二入口。

### 2.2 已确认的问题

| 问题 | 当前表现 | 说明 |
|------|----------|------|
| Service 静默失败 | `dashboardService.getTechnicalIndicators()` 使用 `.catch(() => {})` | 会把失败折叠成“返回空对象” |
| 错误语义不清 | 现有 service 多以 `{ data }` 直接返回 | 调用方通常要靠 `try/catch` 或空值猜测错误来源 |
| 流式更新无统一合并 | WebSocket/SSE 入口多，节流/合并策略未统一 | 高频场景可能导致不必要的 UI 刷新 |
| 缓存/轮询配置分散 | 一部分在 `PiniaStoreFactory` store 配置，一部分散落在页面逻辑 | 还未形成单点治理 |

### 2.3 非目标

以下 Fincept 模式不纳入本提案：

| 模式 | 不纳入原因 |
|------|-----------|
| DataHub 主题路由 | 当前仓库已有 router truth、store truth、service truth；再引入主题总线会形成第二体系 |
| DataMapping + JSONPath 前端规范化 | 字段归一化已主要发生在后端 adapter / service 或前端 normalize helper，不需要前端再引入声明式映射平台 |
| IBroker 统一抽象 | 当前前端主问题不在多券商统一接入 |
| 自定义 ESLint 架构插件 | 成本高，且当前问题优先级低于先收敛真实运行链路 |

---

## 三、从 Fincept 提炼出的五个可移植优势

### 3.1 Scoped `ServiceResult<T>` 安全路径

**借鉴来源**：Fincept `Result<T>` 无异常错误处理。

**本仓库改造原则**：

- 不直接把所有 service 出参改成 `Promise<Result<T>>`。
- 第一阶段仅新增 scoped safe path，用于解决已确认的静默失败点。
- 保留旧返回契约，避免一次性打断现有页面。

**建议形式**：

在现有类型体系下新增一个轻量结果类型，例如放入 `web/frontend/src/api/types/common.ts` 或其扩展文件中统一导出：

```typescript
export type ServiceResult<T> =
  | { ok: true; data: T }
  | { ok: false; error: string; traceId?: string }

export function serviceOk<T>(data: T): ServiceResult<T> {
  return { ok: true, data }
}

export function serviceErr<T>(error: string, traceId?: string): ServiceResult<T> {
  return { ok: false, error, traceId }
}
```

**第一阶段建议只改一个能力点**：

- 不改整个 `dashboardService`
- 只处理 `getTechnicalIndicators()` 的静默失败问题
- 优先方式：
  - 方案 A：新增 `getTechnicalIndicatorsSafe()`
  - 方案 B：新增 view-local adapter，将旧 `{ data }` 返回包装成 `ServiceResult`

**推荐优先级**：方案 A，更清晰，也更便于渐进迁移，也更符合 OpenSpec change 中“preserve compatibility for existing callers until the pilot is verified”的约束。

**示例**：

```typescript
async function getTechnicalIndicatorsSafe(
  symbols: string[],
  indicators: string[]
): Promise<ServiceResult<Record<string, TechnicalIndicatorData[]>>> {
  const results: Record<string, TechnicalIndicatorData[]> = {}
  const errors: string[] = []

  await Promise.all(
    symbols.map((symbol) =>
      apiClient
        .get<UnifiedResponse<Record<string, TechnicalIndicatorData[]>>>(
          "/v1/technical-indicators",
          { params: { symbol, indicators: indicators.join(","), period: 14 } }
        )
        .then((res) => {
          if (res.data?.data) {
            results[symbol] = [res.data.data as unknown as TechnicalIndicatorData]
          }
        })
        .catch((error: unknown) => {
          const message =
            error instanceof Error ? error.message : "fetch failed"
          errors.push(`${symbol}: ${message}`)
        })
    )
  )

  if (Object.keys(results).length > 0) {
    return serviceOk(results)
  }

  return serviceErr(errors.join("; ") || "technical indicator request failed")
}
```

**收益**：

- 先消除静默失败，不强制一次迁移所有 service。
- 调用方可渐进接入 `ok/error` 分支。
- 与现有 `{ data }` 契约共存，不会在第一阶段制造大范围回归。

**风险评估**：中。

原因不是实现复杂，而是错误语义一旦外露，调用页面要同步决定如何展示错误态。该风险必须在提案里显式承认，不能写成“纯类型变更、零运行时影响”。

---

### 3.2 在现有实时入口之上增加 latest-only coalescing，而不是新建独立流系统

**借鉴来源**：Fincept WebSocket Coalesce。

**本仓库改造原则**：

- 不新增脱离现有体系的“全局流管理器”。
- 优先落在当前已有的实时入口上：
  - `useWebSocketEnhanced.ts`
  - `useRealtimeMarket.ts`
  - `useSSE.js`
- 如果只是通用算法，不应放进 `src/composables/`，而应作为 `utils` 级 helper，被实时 composable 调用。

**原因**：

`architecture/STANDARDS.md` 已明确：

- 非 composable 文件不得放入 `src/composables/`
- 单消费者 composable 应 colocate
- 只有存在 2+ 消费者时才提取为全局 composable

因此，本提案不建议新增全局 `src/composables/useCoalescedStream.ts`。

**更合理的落点**：

- 新增一个通用 helper，例如 `web/frontend/src/utils/streamCoalescer.ts`
- 在 `useRealtimeMarket.ts` 或 `useWebSocketEnhanced.ts` 内按频道选择性接入
- 对 SSE 场景仅在确认存在高频事件后再复用

**建议 helper 形态**：

```typescript
export function createLatestOnlyCoalescer<T>(
  emit: (value: T) => void,
  windowMs = 200
): (value: T) => void {
  let latestValue: T | null = null
  let timer: ReturnType<typeof setTimeout> | null = null

  return (value: T) => {
    latestValue = value

    if (timer) {
      return
    }

    timer = setTimeout(() => {
      if (latestValue !== null) {
        emit(latestValue)
      }
      latestValue = null
      timer = null
    }, windowMs)
  }
}
```

**接入策略**：

- 第一阶段只选一个高频频道验证，例如实时行情或市场概览。
- 默认关闭，不做全局强制。
- 仅对高频 push 通道启用，不影响普通 API 请求链路。

**收益**：

- 保留现有订阅模式，只减少高频重复刷新。
- 不引入新的生命周期管理模型。
- 更符合当前 Vue 3 代码组织规范。

**风险评估**：低到中。

主要风险在于：

- 窗口过大会让 UI 显得“慢半拍”
- 不同频道对窗口大小容忍度不同，必须按场景验证

---

### 3.3 复用 `PiniaStoreFactory` 的集中配置能力，补齐 store policy registry

**借鉴来源**：Fincept TopicPolicy 声明式缓存策略。

**本仓库改造原则**：

- 不新增与 store 配置并行的 `src/api/policies.ts`
- 不重复维护一套新的 TTL 真相源
- 只在 `PiniaStoreFactory` 现有配置模型上补充“可复用策略注册表”

**推荐方向**：

新增一个面向 store factory 的策略表，例如：

- `web/frontend/src/stores/storePolicies.ts`

用途不是替代 store config，而是提供复用模板：

```typescript
export interface StorePolicy {
  cacheTtl?: number
  updateInterval?: number
  wsChannel?: string
}

export const storePolicies: Record<string, StorePolicy> = {
  "market-quotes": { cacheTtl: 30_000, updateInterval: 10_000, wsChannel: "market-data" },
  "risk-alerts": { cacheTtl: 30_000, updateInterval: 15_000, wsChannel: "risk-alerts" },
  "technical-indicators": { cacheTtl: 300_000 },
}
```

然后由 store 声明显式引用：

```typescript
const marketQuotesPolicy = storePolicies["market-quotes"]

export const useMarketQuotesStore = PiniaStoreFactory.createRealtimeStore({
  id: "market-quotes",
  endpoint: "/api/market/quotes",
  cache: {
    enabled: true,
    key: "market-quotes",
    ttl: marketQuotesPolicy.cacheTtl,
    strategy: "memory",
  },
  wsChannel: marketQuotesPolicy.wsChannel,
  updateInterval: marketQuotesPolicy.updateInterval,
})
```

**关键点**：

- 真正的执行入口仍是 store 声明，不是策略表
- 策略表只负责减少重复数字和命名漂移
- 页面级临时定时器和局部 `setInterval` 才是后续替换目标

**收益**：

- 与现有 `PiniaStoreFactory` 对齐
- 不会引入第二套缓存系统
- 便于后续审计 TTL / 轮询配置

**风险评估**：低。

---

### 3.4 引入“注册表先行”的轻量治理，而不是引入 DataHub

**借鉴来源**：Fincept 的 `DATAHUB_TOPICS.md` 与 TopicPolicy 注册方式。

Fincept 最值得借鉴的并不是“所有数据都必须进 DataHub”，而是它把以下信息前置成了文档化、可审计的注册表：

- 哪些数据主题存在
- 谁是 owner / producer
- TTL / 最短刷新间隔是多少
- 哪些通道是 push-only
- 哪些通道允许用户触发 force refresh

这套机制迁移到 MyStocks 时，不应照搬成 `topic registry`，而应落成更贴近 Web 前端现状的两份轻量注册表：

1. **frontend-data-capability-registry**
2. **frontend-realtime-channel-registry**

**建议新增的注册物**：

- `docs/guides/frontend/frontend-data-capability-registry.md`
- `docs/guides/frontend/frontend-realtime-channel-registry.md`

**建议注册的字段**：

| 字段 | 含义 |
|------|------|
| capability / channel | 能力名或实时频道名 |
| owner | 对应 service / store / composable |
| source of truth | `service` / `store` / `route-local composable` |
| endpoint / channel | API 路径或 WS/SSE 频道 |
| cache ttl | 缓存有效期 |
| min interval | 最短刷新间隔 |
| push only | 是否仅依赖推送 |
| force refresh | 是否允许用户强刷 |
| consumer scope | 哪些页面/模块消费 |
| request id visibility | UI 是否要求显示 trace/request id |

**为什么这比直接上 DataHub 更适合 MyStocks**：

- MyStocks 已有 OpenAPI 契约和 TypeScript 类型真相源，缺的不是“主题总线”，而是“前端消费侧能力清单”。
- 现有问题之一是策略散落和入口分散，注册表比抽象框架更能先解决治理失明。
- 注册表可以先文档化，再逐步进入代码，不会形成第二运行时系统。

**补充建议：统一 `force refresh` 语义**

Fincept 的 `request(topic, force=true)` 很值得借鉴。MyStocks 可以不复制 API，但建议统一以下语义：

- 普通刷新：尊重 TTL / `minInterval`
- 强制刷新：用户主动点击时可绕过本地间隔门
- 仍受上游限流和后端节流保护

这能减少当前各页面“各写一套 refresh 逻辑”的情况。

**收益**：

- 先建立可治理的目录和审计视角
- 为后续 store policy / realtime coalesce 提供统一挂载点
- 与现有 OpenAPI 契约、质量门禁体系相容

**风险评估**：低。

风险主要在于如果注册表只写不维护，会退化成陈旧文档；因此必须和后续门禁绑定，而不是仅靠人工约定。

---

### 3.5 引入 phased discipline gates 与 developer-mode runtime inspector

**借鉴来源**：Fincept 的分阶段 rollout、Phase 10 cleanup、`datahub-discipline` CI 检查与 DataHub Inspector。

Fincept 的强项不只是架构设计，而是把迁移工程做成了：

- 可并存
- 可回退
- 可检查
- 最后再关门清理

这对 MyStocks 同样适用，而且比新增抽象层更实际。

**可直接移植的做法**：

1. **阶段化迁移约束**
   - 新路径与旧路径先并存
   - 只有在消费者都迁完后，才进入 cleanup phase
   - 不在审批阶段承诺“一次性推广到所有 service”

2. **纪律门禁**
   - 在迁移成熟后，增加针对前端数据访问路径的 CI 检查
   - 例如：
     - 禁止 views 直接调用 `apiClient`
     - 禁止新增 `.catch(() => {})`
     - 禁止在 routed view 内新增裸 `setInterval` / `QTimer` 式轮询替代物，除非明确豁免

3. **开发者模式运行时检查器**
   - 增加一个开发者可见页面或面板，不面向普通用户默认暴露
   - 展示：
     - 当前页面使用的 store / service
     - 最近一次 fetch 时间
     - cache ttl / stale 状态
     - WebSocket/SSE 连接状态
     - 最近 request id / trace id
     - 后端 readiness 状态

**建议落点**：

- 门禁：
  - 现有 GitHub Actions / compliance scripts 增补前端数据访问治理检查
- 检查器：
  - `system` 域下的 developer mode 页面，或现有调试页扩展

**为什么这对 MyStocks 有价值**：

- 本仓库已经有很强的契约和质量门禁体系，适合继续补“前端数据访问纪律”，而不是另起架构。
- 当前前端的主要痛点之一就是“出了问题只能靠 grep 和猜”，缺运行时可见性。
- 与 `architecture/STANDARDS.md` 的 proposal-first、single source of truth、front-end closure 顺序一致。

**收益**：

- 提前发现架构回退，而不是等代码堆积后再重构
- 降低新旧路径并存期的认知成本
- 让“为什么这个页面没有刷新 / 为什么命中了旧缓存”变成可观察问题

**风险评估**：中。

风险不在技术，而在门禁过早上锁会阻碍迁移。因此建议把纪律门禁放在最后阶段，而把运行时检查器前置。

---

## 四、分阶段实施建议

### Phase 0：Governance Setup

范围：

- 不改运行时代码
- 先梳理 frontend-data-capability-registry 与 frontend-realtime-channel-registry
- 明确哪些能力走 `service`，哪些走 `store`，哪些仍是 view-local composable

建议文件：

- `docs/guides/frontend/frontend-data-capability-registry.md`
- `docs/guides/frontend/frontend-realtime-channel-registry.md`
- 本提案的任务拆解文档（如后续进入 OpenSpec）

完成标准：

- 关键能力有 owner、source of truth、TTL、refresh 语义
- 明确本轮迁移“不做什么”

风险：低

---

### Phase 1：Silent Failure Removal

范围：

- 仅处理 `dashboardService.getTechnicalIndicators()` 对应能力
- 新增 `ServiceResult<T>` 类型
- 新增 safe path，不强行替换旧契约

建议文件：

- `web/frontend/src/api/types/common.ts` 或其扩展导出
- `web/frontend/src/api/services/dashboardService.ts`
- 一个实际消费该能力的页面 / composable
- 对应单测

完成标准：

- 不再使用 `.catch(() => {})`
- 调用方能显式区分失败分支
- 旧页面未被大面积打断

风险：中

---

### Phase 2：Realtime Coalescing Pilot

范围：

- 不做全局推广
- 只选 1 个高频频道接入 latest-only coalescing
- 优先落在 `useRealtimeMarket.ts` 或 `useWebSocketEnhanced.ts`

建议文件：

- `web/frontend/src/utils/streamCoalescer.ts`
- `web/frontend/src/composables/useRealtimeMarket.ts` 或 `web/frontend/src/composables/useWebSocketEnhanced.ts`
- 1 个实际消费页面

完成标准：

- 高频更新下页面可用性不下降
- 无明显感知延迟
- 可按配置回退

风险：低到中

---

### Phase 3：Store Policy Consolidation

范围：

- 只覆盖已通过 `PiniaStoreFactory` 创建的 store
- 不处理所有历史页面
- 不引入新的 query/cache 框架

建议文件：

- `web/frontend/src/stores/storePolicies.ts`
- `web/frontend/src/stores/apiStores.ts`
- `web/frontend/src/stores/storeFactory.ts`（仅在确有必要时做最小补充）

完成标准：

- 至少 2-3 个现有 store 改为从统一策略读取
- 不再在这些 store 内手写散落的 TTL / updateInterval 常量

风险：低

---

### Phase 4：Developer Runtime Inspector

范围：

- 不做普通用户可见入口
- 只面向 developer mode / 调试模式
- 先展示一个页面的 data capability、缓存状态、实时连接状态

建议文件：

- `web/frontend/src/views/system/` 下的调试页或开发页
- 相关 store / readiness / realtime 状态读取层

完成标准：

- 可以在 UI 中看到当前页面数据通道的健康状况
- 能辅助判断“旧缓存/未刷新/连接断开/后端未就绪”

风险：低到中

---

### Phase 5：Incremental Expansion

只有在前 3 个阶段验证收益明确后，才考虑：

- 把 `ServiceResult<T>` 扩展到其他存在静默失败的 service
- 把 Coalesce 扩展到其他高频实时频道
- 把策略表推广到更多 factory-created store

不建议在审批阶段直接承诺“推广到全部 service 文件”。

---

### Phase 6：Cleanup-Stage Discipline Gates

前提：

- 只有在新路径已稳定、旧路径消费者基本迁完后才进入

范围：

- 新增前端数据访问纪律检查
- 把注册表维护纳入变更要求
- 逐步淘汰明确废弃的旧路径

建议门禁示例：

- 禁止在 routed views 中直接引入 `apiClient`
- 禁止新增 `.catch(() => {})`
- 禁止未登记 channel/capability 就新增轮询或流式消费入口

风险：中

原因在于过早执行会卡住迁移；因此必须作为收口阶段，而不是开局阶段。

---

## 五、与仓库约束的对齐

| 约束 | 对齐说明 |
|------|---------|
| Proposal-First | 本文仅为方案，未获批前不进入实现 |
| 单一真相源 | 不新建 DataHub / 第二套缓存层 / 第二套类型入口 |
| View-Local Canonical | 非通用算法不提升为全局 composable；通用算法优先 `utils` |
| 最小变更原则 | 每个阶段只动一条能力链，避免横扫式重构 |
| 垂直切片 | 每个阶段都覆盖“注册表/类型/工具 + service/store + 一个真实消费点 + 验证” |
| 契约先行 | 与现有 OpenAPI → TS 类型生成 → CI 契约门禁单向真相源保持一致 |

---

## 六、审批建议

建议按以下口径审批，而不是把它视为“大规模前端重构”：

1. 是否批准先建立 `frontend-data-capability-registry` 与 `frontend-realtime-channel-registry`，作为后续迁移边界文件？
2. 是否批准引入 scoped `ServiceResult<T>`，仅用于替换真实存在的静默失败点？
3. 是否批准在现有实时入口上试点 latest-only coalescing？
4. 是否批准为 `PiniaStoreFactory` 补一个 store policy registry，而不是另起一套缓存配置？
5. 是否批准增加 developer-mode runtime inspector，并将 discipline gates 留到迁移收口阶段再启用？

若以上三点获批，后续应按微批次执行，每批次单独验收。

---

## 七、结论

Fincept 可借鉴的不是其桌面端整体架构，而是五类更小但更硬的工程优势：

- 错误语义显式化
- 高频推送合并
- 声明式策略集中
- 注册表先行的治理方式
- 迁移纪律与运行时可见性

在 MyStocks 中，这些能力都应当作为对现有体系的增量收敛来实施，而不是机械搬运桌面端的 DataHub/Topic 模型。只有这样，方案才符合当前仓库的真相源、前端目录规范、OpenAPI 契约链路和最小变更原则。

---

*提案重写：Codex | 日期：2026-04-21*
