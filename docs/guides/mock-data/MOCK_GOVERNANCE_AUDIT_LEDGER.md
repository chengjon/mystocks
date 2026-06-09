# MOCK 治理审计台账

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

> **用途说明**:
> 本文件用于记录当前主线下 MOCK 数据治理与页面状态对齐情况，服务于 `verified/pending` 审计与实现收口。
> 仓库共享规则仍以 [`architecture/STANDARDS.md`](../../../architecture/STANDARDS.md) 为准，页面级 API 行为仍以 [`openspec/specs/api-integration/spec.md`](../../../openspec/specs/api-integration/spec.md) 为准。

## 当前审计结论

- 当前前端 mock-routing 必须按三层理解：
  - `client layer`: `web/frontend/src/api/apiClient.ts`
  - `service layer`: `web/frontend/src/api/services/strategyService.ts`
  - `adapter layer`: `web/frontend/src/api/adapters/*`
- 允许保留的是 `client layer` 的显式 mock 模式。
- 必须收掉的是：
  - `service layer` 中以 `VITE_APP_MODE` 为依据的 dual-truth 切换
  - `adapter layer` 中“请求失败后直接返回 mock payload”的 silent fallback
- `useBackendReadiness.ts` 属于受控 fallback，不属于 silent fallback。

## 页面与路由层对齐

| 页面/能力 | 当前状态 | 主要消费者/入口 | Client Layer | Service Layer | Adapter Layer | 当前结论 | 退役/收口条件 |
|----------|----------|----------------|-------------|---------------|---------------|----------|----------------|
| `Strategy-Repo` / `Strategy-Parameters` | `verified` | `useStrategy.ts` → `ArtDecoStrategyManagement.vue` | `VITE_USE_MOCK_DATA` 显式可控 | 旧 `VITE_APP_MODE` 分支曾存在 | 详情读取曾有 silent fallback | 必须对齐 | 删除 `VITE_APP_MODE`，详情失败进入显式错误态 |
| `Strategy-Backtest` | `verified` | `useStrategy.backtest.ts` / `backtestAnalysisViewModel.ts` | `VITE_USE_MOCK_DATA` 显式可控 | 旧 `VITE_APP_MODE` 分支曾存在 | 回测适配器本身已返回 `null`，非 silent success | 基本可控 | 保持显式失败分支，不再引入 mock 成功值 |
| `Market-Technical` / `Data-FundFlow` 等市场页族 | `verified` | 市场适配器消费链 | `VITE_USE_MOCK_DATA` 显式可控 | 无独立 service dual-truth | `MarketAdapter` 曾在失败后返回 mock VM / 数组 | 必须对齐 | 失败只返回 empty-state 输入，不再返回 mock payload |
| 应用启动 readiness | 显式 mock/自动化受控降级 | `App.vue` + `useBackendReadiness.ts` | 受 `VITE_USE_MOCK_DATA` 控制 | 无 | 无 silent mock payload | 合规保留 | 保持 banner / request id / mode 可见 |

## 历史口径与文档漂移

以下内容必须视为历史口径，不应继续作为当前运行时事实：

- `VITE_APP_MODE` 是当前主切换开关
- `/api/mock/strategy` 是策略主链默认入口
- `verified` 页面请求失败后继续返回 mock 数据可视为成功

已知重点漂移文档：

- `web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md`
- 历史报告中把 `VITE_APP_MODE` 写成当前切换真相的实现报告

## 本轮收口要求

- `verified` 页面：
  - 真实接口失败时进入显式 `error / empty / request id` 路径
  - 不再在 adapter 内直接返回 mock payload
- 显式 mock 模式：
  - 仅通过 `VITE_USE_MOCK_DATA` 经共享 `apiClient` 生效
  - 文档和测试都必须表述为“mock 验收”，不是“真实主链通过”
