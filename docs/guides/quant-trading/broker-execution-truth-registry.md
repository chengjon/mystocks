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
| `src/trading/realtime_strategy_executor.py` | 上游信号到下单编排 | upstream caller only | 无 | active orchestration caller | `experimental` | `q2-wave3-trading-safety` | 保持为上游调用面，不作为第一条 broker truth 落点 | 可表达 live-trading intent，但不是外部确认源 |
| `src/trading/live_trading_engine.py` | 实时会话与策略执行编排 | upstream orchestration only | 无 | active orchestration bridge | `experimental` | `q2-wave3-trading-safety` | 不作为第一批 broker-binding 实现面 | 当前未验证为 canonical broker-facing chain |
| `src/interfaces/api/trading_router.py` | DDD 交易 API stub | none | 无 | `501` stub | `stub` | `q2-wave3-trading-safety` | 保持非 canonical，待真正 service wire-up 后再重评 | 不能作为 broker execution truth |
| `web/backend/app/api/trading_runtime.py` | 轻量运行时可用性 API | demo/runtime status only | 无 | in-memory runtime surface | `demo` | `q2-wave3-trading-safety` | 保持与 broker truth 分离 | 用于前端 runtime availability，不是 broker acknowledgement source |
| `unverified external broker adapter path` | 外部柜台 / broker / counterparty 事实来源 | broker-facing acknowledgement and reconciliation | 缺失 | gap | `pending-classification` | `q2-wave3-trading-safety` | 在后续 batch 中明确第一条 canonical adapter 或 ingestion bridge | 当前仓库没有已验证的 canonical external adapter |

## Interpretation Rules

### 1. `OrderManagementService` 是当前唯一可扩展的本地控制锚点

如果后续要做：

- local-to-external order identity binding
- broker acknowledgement binding
- divergence classification
- replay-suppression policy gate

默认从 `src/application/trading/order_mgmt_service.py` 及其相邻本地 ledger 层开始，而不是从 demo API 或上游 orchestration 层开始。

### 2. 上游 orchestration 不等于 broker truth

`RealtimeStrategyExecutor` 和 `LiveTradingEngine` 仍然是 active caller / orchestration surfaces。

但它们当前并不提供：

- verified external order identity
- broker acknowledgement source
- broker lifecycle event identity
- reconciliation authority

因此不能单独作为 broker truth registry 的 canonical source。

### 3. Stub 和 demo 面必须显式排除

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
- 已存在 broker-confirmed cancel / reject truth
- execution-report replay suppression 已经安全可做
- local order-state evidence 已经与外部柜台 truth 对齐
- 当前任一路径可升级为 `production-eligible`

## Immediate Batch-1 Outcome

对于本轮 broker acknowledgement / reconciliation 的第一批工作，这份 registry 起到两个作用：

1. 先锁“从哪里开始做”：
   - `OrderManagementService` 是 canonical local anchor
2. 再锁“哪些路径不能误认为 broker truth”：
   - DDD stub API
   - runtime demo API
   - orchestration caller surfaces

后续若新增真实 broker-facing adapter 或 ingestion bridge，必须先更新本表，再继续更强语义实现。
