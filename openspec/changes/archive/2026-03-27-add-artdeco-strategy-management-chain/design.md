## Context

> **历史文档说明**:
> 本文件属于已归档变更留下的历史规格、设计附件或过程材料，用于补充还原当时方案与结构。
> 它不再是当前治理口径或当前实现状态的默认真相源；如与现行 specs、共享规则或代码实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际代码实现为准。


`ArtDecoStrategyManagement` 当前仅占位显示，尚未形成可执行链路。项目中已存在可复用能力（`useStrategy`、`StrategyApiService`、`StrategyAdapter`）以及多路后端策略 API，但存在接口域并行、响应结构不一致问题。设计目标是以最小改造成本打通策略管理核心路径，并满足 ArtDeco 工程红线中的可观测性与 Mock 驱动要求。

## Goals

- 在 ArtDeco 策略管理页建立可运行的端到端链路：列表、操作、状态、反馈。
- 复用既有前端策略能力，避免重复实现请求和适配逻辑。
- 对用户提供可感知的请求追踪信息（Request ID / process time）。
- 通过 REAL->MOCK 降级，保证后端异常时页面仍可验收和演示。
- 与参数、信号、回测三个策略子域保持联动一致。

## Non-Goals

- 本提案不在首阶段强制切换后端到单一策略路由域。
- 本提案不包含策略优化算法本体或回测引擎重构。
- 本提案不改动全局菜单架构与非策略域页面。

## Architecture

采用“页面编排层 + 复用能力层 + API 兼容层”三层策略：

1. 页面编排层：`ArtDecoStrategyManagement.vue`
- 负责 UI 状态机：加载、空态、错误、操作中。
- 负责操作入口：生命周期动作、CRUD、回测跳转。
- 负责 Trace 信息显化和数据源标记（REAL/MOCK）。

2. 复用能力层：`useStrategy` + `StrategyAdapter`
- `useStrategy` 作为统一业务入口，提供列表、详情、CRUD、启停控制。
- `StrategyAdapter` 负责响应字段统一，降低后端字段波动对 UI 的影响。

3. API 兼容层：`StrategyApiService`
- MVP 使用 `/api/v1/strategy`（已有代码路径，改造成本最低）。
- 后续通过 service 层切换策略，逐步兼容 `/api/strategy-mgmt`。

## Data Flow

1. 页面初始化：`useArtDecoApi.exec(fetchStrategies)` -> 成功渲染真实数据。
2. 异常或不可用 payload：触发 MOCK fallback（本地 mock factory）并标记数据源。
3. 成功但空列表：不触发 fallback，保留 REAL 空态并标记数据源为 REAL。
4. 用户操作：调用 `useStrategy` 对应方法（start/stop/pause/resume/create/update/delete）。
5. 操作结果：局部更新 + 全局提示；失败时回滚并记录错误上下文。
6. 跨 Tab 跳转：携带 `strategyId` 进入参数/信号/回测页并拉取对应数据。

## API Strategy

- **Primary (MVP):** `/api/v1/strategy/*`（与当前 `StrategyApiService` 对齐）
- **Secondary (Migration):** `/api/strategy-mgmt/*`（结构化模型更清晰，作为阶段二收敛方向）
- **Avoid as primary:** `/api/strategy/*`（mock-first，实库能力不稳定）

### MVP Endpoint Mapping (Frozen Contract)

为避免实现阶段接口分裂，MVP 先冻结当前可用端点契约，不在本阶段做路径风格重构。

| Capability | Method | MVP URL (locked) | Notes |
|---|---|---|---|
| List strategies | `GET` | `/api/v1/strategy/strategies` | 支持分页/筛选参数 |
| Strategy detail | `GET` | `/api/v1/strategy/strategies/{id}` | 详情查询 |
| Strategy config | `GET` | `/api/v1/strategy/{id}/config` | 当前 service 兼容路径 |
| Create strategy | `POST` | `/api/v1/strategy/strategies` | 新建 |
| Update strategy | `PUT` | `/api/v1/strategy/strategies/{id}` | 编辑 |
| Delete strategy | `DELETE` | `/api/v1/strategy/strategies/{id}` | 删除/失活语义以后端为准 |
| Start strategy | `POST` | `/api/v1/strategy/{id}/start` | 生命周期动作 |
| Stop strategy | `POST` | `/api/v1/strategy/{id}/stop` | 生命周期动作 |
| Pause strategy | `POST` | `/api/v1/strategy/{id}/pause` | 生命周期动作 |
| Resume strategy | `POST` | `/api/v1/strategy/{id}/resume` | 生命周期动作 |

### URL Normalization Target (Post-MVP)

MVP 完成后再统一路径风格，目标规范为资源化动作路径（示例）：`/api/v1/strategy/strategies/{id}/actions/{action}`。
本提案首期不引入该重构，避免与页面落地并行造成返工。

## Error Handling & Observability

- 所有异步请求走统一包装（`useArtDecoApi.exec`），统一处理 loading/error。
- UI 必须显示 Request Trace 元数据，字段来源按以下优先级：
  1. `request_id`：`UnifiedResponse.request_id`（通过 `useArtDecoApi.lastRequestId` 暴露）
  2. `process_time_ms`：由 `UnifiedResponse.process_time` 解析得到毫秒值；若后端已直接返回毫秒字符串则直接使用
  3. 缺失值占位：固定显示 `N/A`，不隐藏 UI 位
- 生命周期操作按钮需具备禁用态和幂等保护，避免重复触发。
- 对接口字段缺失采用 adapter 默认值，保证页面渲染稳定。

## Testing Strategy

- 单元测试：`useStrategy` 与 `StrategyAdapter` 的字段映射和异常处理。
- 组件测试：管理页加载态、空态、fallback、按钮权限状态。
- E2E：列表加载、生命周期操作、CRUD、跨 Tab 跳转、fallback 场景。
- 质量门禁：结构性语法错误 0；类型推断错误不高于基线 100；E2E 报告纳入交付。

## Rollout Plan

- Phase 1（MVP）：列表 + 生命周期动作 + REAL/MOCK + Trace。
- Phase 2（Enhancement）：CRUD 完整化 + 回测联动 + Tab 一致性。
- Phase 2.5（Optimization）：`ArtDecoStrategyOptimization` 由同一 owner 在同一契约下实现，复用 `strategyId`/参数快照/状态模型，避免跨链路重复适配。
- Phase 3（Convergence）：在 service 层完成 `/api/strategy-mgmt` 兼容切换。
