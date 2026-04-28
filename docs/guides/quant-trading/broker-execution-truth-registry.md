# Broker Execution Truth Registry

> **权威来源声明**:
> 本文件是量化交易 broker-facing 执行与生命周期摄取路径的最小治理真相源，用于说明“哪条链路可被视为当前 broker truth 候选面”。
> 它不是仓库共享规则的唯一事实来源；涉及审批门禁、当前实现口径与提案状态时，请同时核对 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、`openspec/changes/add-broker-acknowledgement-reconciliation-contract/` 与当前代码。

## Purpose

这份 registry 只回答一个问题：

当前仓库里，哪些交易相关路径可以被视为 broker acknowledgement / reconciliation 的候选面，哪些不能。

## Registry

| Surface | Role | Canonical Scope | External Truth Source | Current State | Classification | Reconciliation Owner | Next Action | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `src/application/trading/order_mgmt_service.py` | 本地订单生命周期控制锚点 | 当前 broker-truth 实施的 canonical anchor | 未验证；仅有本地状态与本地审计证据 | active local runtime path | `experimental` | `q2-wave3-trading-safety` | 从此处向外增加 local-to-external correlation ledger | 当前最强 repo-truth；不等于 broker truth |
| `web/backend/app/services/windows_bridge_adapter.py` (`qmt` provider) | `miniQMT` 候选桥接入口 | project-approved first primary broker-truth candidate | `qmt` provider over Windows bridge | repo-facing lifecycle ingestion verified; live broker adapter still pending | `primary-candidate` | `broker-truth-channel-topology` | 把 `qmt/*` 提交与生命周期事件继续收束到 channel-scoped submission / lifecycle ingestion 契约 | `src/application/trading/miniqmt_lifecycle_ingestion.py` 与 `OrderManagementService.ingest_miniqmt_lifecycle_payload()` 已把 Windows-bridge 风格 payload 规范化进 broker lifecycle ledger；这仍不等于已存在 verified miniQMT trading adapter |
| Tongdaxin semi-manual trading path | 补充型 operator-assisted 交易通道 | supplemental execution and reconciliation path | operator action + Tongdaxin terminal evidence | repo-facing supplemental lifecycle ingestion verified; review-first automation boundary active | `supplemental-operator-assisted` | `broker-truth-channel-topology` | 继续保持 review-first；只有未来拿到等价外部身份与序列证据后才可升级自动权限 | `src/application/trading/tdx_manual_lifecycle_ingestion.py` 已把 Tongdaxin 半手工 payload 接入 lifecycle ledger，但默认落入 `supplemental_channel_review_required`，且不会继承 primary-path 自动权限；必须与现有 `tdx` 行情/数据适配器区分 |
| `src/trading/realtime_strategy_executor.py` | 上游信号到下单编排 | upstream caller only | 无 | active orchestration caller | `experimental` | `q2-wave3-trading-safety` | 保持为上游调用面，不作为第一条 broker truth 落点 | 可表达 live-trading intent，但不是外部确认源 |
| `src/trading/live_trading_engine.py` | 实时会话与策略执行编排 | upstream orchestration only | 无 | active orchestration bridge | `experimental` | `q2-wave3-trading-safety` | 不作为第一批 broker-binding 实现面 | 当前未验证为 canonical broker-facing chain |
| `src/interfaces/api/trading_router.py` | DDD 交易 API stub | none | 无 | `501` stub | `stub` | `q2-wave3-trading-safety` | 保持非 canonical，待真正 service wire-up 后再重评 | 不能作为 broker execution truth |
| `web/backend/app/api/trading_runtime.py` | 轻量运行时可用性 API | demo/runtime status only | 无 | in-memory runtime surface | `demo` | `q2-wave3-trading-safety` | 保持与 broker truth 分离 | 用于前端 runtime availability，不是 broker acknowledgement source |
| unverified external broker adapter path | 外部柜台 / broker / counterparty 事实来源 | broker-facing acknowledgement and reconciliation | 缺失 | gap | `implementation-pending` | `broker-truth-channel-topology` | 把 primary / supplemental topology 逐步落到 channel-scoped correlation 和 lifecycle ingestion | 当前仓库仍然没有已验证的 live broker-facing adapter |

## Interpretation Rules

### 1. `OrderManagementService` 是当前唯一可扩展的本地控制锚点

如果后续要做：

- local-to-external order identity binding
- broker acknowledgement binding
- divergence classification
- replay-suppression policy gate

默认从 `src/application/trading/order_mgmt_service.py` 及其相邻本地 ledger 层开始，而不是从 demo API 或上游 orchestration 层开始。

### 2. `miniQMT` 是当前仓库里唯一显式 primary-path 候选通道

`miniQMT` 当前被登记为第一条 primary broker-truth candidate，依据是：

- 项目已批准 `miniQMT primary / Tongdaxin supplemental` 的通道拓扑
- `web/backend/app/services/windows_bridge_adapter.py` 已为 `qmt` provider 保留 bridge registry 入口
- `src/application/trading/miniqmt_lifecycle_ingestion.py` 已把 Windows-bridge 风格 `miniQMT` payload 规范化进 `BrokerLifecycleEvent`
- `OrderManagementService.ingest_miniqmt_lifecycle_payload()` 已把 channel-scoped `miniQMT` acknowledgement / reject / cancel / execution 事件接入本地 lifecycle ledger

但当前 registry 明确不把这两点夸大成：

- 已存在 verified `miniQMT` trading adapter
- 已存在 production-ready replay suppression authority
- 已存在 production-eligible live broker execution closure

### 3. Tongdaxin supplemental path 必须与现有 `tdx` 数据面严格区分

当前仓库里大量 `tdx` / 通达信代码都属于：

- 行情读取
- 本地文件导入
- 市场数据 API

它们不自动等同于 Tongdaxin semi-manual trading 的 broker truth 通道。

因此在 channel topology 线里，Tongdaxin 当前登记为：

- supplemental
- operator-assisted
- review-first by default
- repo-facing supplemental lifecycle capture already present, but not automation-equivalent to `miniQMT`

### 4. 上游 orchestration 不等于 broker truth

`RealtimeStrategyExecutor` 和 `LiveTradingEngine` 仍然是 active caller / orchestration surfaces。

但它们当前并不提供：

- verified external order identity
- broker acknowledgement source
- broker lifecycle event identity
- reconciliation authority

因此不能单独作为 broker truth registry 的 canonical source。

### 5. Stub 和 demo 面必须显式排除

下面两个面必须继续被排除为 broker truth：

- `src/interfaces/api/trading_router.py`
- `web/backend/app/api/trading_runtime.py`

原因不是它们“无价值”，而是它们当前承担的是：

- stub / future wire-up
- lightweight runtime availability / demo state

而不是 broker-facing execution closure。

## Current Non-Claims

本 registry 当前明确不宣称：

- 已存在 verified broker adapter
- 已存在 live `miniQMT` trading adapter
- 已存在 broker-confirmed continuous Tongdaxin trading bridge
- 已存在 broker-confirmed cancel / reject truth
- execution-report replay suppression 已经安全可做
- local order-state evidence 已经与外部柜台 truth 对齐
- supplemental channel 已获得 primary-path 自动权限
- 当前任一路径可升级为 `production-eligible`

## Current Outcome

对于当前 broker acknowledgement / reconciliation + channel-topology 组合工作，这份 registry 起到两个作用：

1. 先锁“从哪里开始做”：
   - `OrderManagementService` 是 canonical local anchor
2. 再锁“哪些路径不能误认为 broker truth”：
   - DDD stub API
   - runtime demo API
   - orchestration caller surfaces
3. 再明确“哪些 repo-facing 通道已经具备了最小 implementation evidence，但仍不能拔高为 production broker truth”：
   - `miniQMT` primary-candidate lifecycle ingestion
   - Tongdaxin supplemental review-first lifecycle capture
4. 再锁“哪些通道已经具备自动权限门禁，哪些没有”：
   - `miniQMT` 是当前唯一显式保留 replay-suppression / bounded auto-resolution 自动权限候选面的通道
   - Tongdaxin supplemental path 已明确不继承 primary-path 自动权限

后续若新增真实 broker-facing adapter 或 ingestion bridge，必须先更新本表，再继续更强语义实现。
