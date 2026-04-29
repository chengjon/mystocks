# miniQMT 项目对齐问卷与接口边界清单

> **权威来源声明**:
> 本文件是跨项目协作用的边界与问卷文档，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及本项目当前实现事实，请同时核对根目录 `AGENTS.md`、`openspec/AGENTS.md`、当前代码与相关 OpenSpec change。
> 日期：2026-04-29
> 状态：待 miniQMT 项目回复
> 适用范围：`/opt/claude/mystocks_spec` 与独立 Windows `miniQMT` 项目（当前位于 `/mnt/d/MyCode3/miniQMT`）之间的接口边界确认

## 1. 文档目的

本文不是要求 Windows `miniQMT` 项目直接遵循本仓库内部实现细节，而是明确两件事：

1. `mystocks_spec` 在 `WSL 上的 Ubuntu 24.04.4 LTS` 这一侧，已经冻结了哪些接口语义。
2. Windows `miniQMT` 项目需要向本项目确认哪些能力、字段、失败语义和部署前提。

目标是让两个项目在开发上分工清楚：

- `mystocks_spec` 只负责本项目内的交易编排、broker-truth ledger、轮询与结果回灌接口
- Windows `miniQMT` 项目负责真实 SDK adapter、Windows 侧部署、live broker evidence 与运行时服务

---

## 2. 当前分工边界

### 2.1 `mystocks_spec` 负责什么

本项目当前负责：

- 本地订单创建、提交意图与本地审计账本
- `miniQMT` primary-path submission attempt 持久化
- `bridge_task_id` 记录与 live bridge result polling
- 将 Windows 侧返回结果重新接回 shared lifecycle / divergence ledger
- 在证据不足时落 `review_required`
- 维持 `miniQMT primary / Tongdaxin supplemental` 的权限边界

当前本项目相关锚点：

- `src/application/trading/order_mgmt_service.py`
- `src/application/trading/miniqmt_primary_runtime.py`
- `src/application/trading/miniqmt_live_bridge_followup.py`
- `web/backend/app/services/windows_bridge_adapter.py`
- `web/backend/app/services/miniqmt_live_bridge.py`

### 2.2 Windows `miniQMT` 项目负责什么

Windows `miniQMT` 项目应负责：

- 与真实 `miniQMT` SDK 对接
- Windows 机器上的服务部署、进程管理、配置与可用性
- 把 SDK submit / reject / cancel / execution 等结果转换成稳定对外 contract
- 对外返回可验证的 broker-facing evidence
- 保证本项目能够拿到可轮询、可审计、可区分 transport receipt 与 broker result 的结果

### 2.3 当前明确不做什么

本项目当前**不**负责：

- 直接实现 Windows `miniQMT` SDK adapter
- 承诺当前已拥有生产级 live broker adapter
- 在没有 identity echo 的情况下猜测 broker acknowledgement
- 因 `miniQMT` 超时或 unavailable 自动 silent fallback 到 Tongdaxin

Windows `miniQMT` 项目也不应要求本项目：

- 通过 `symbol/quantity/timing` 模糊匹配订单
- 把 transport acceptance 当作 broker acknowledgement
- 吃下不完整结果再靠本地补猜 identity

---

## 3. 本项目已经冻结的接口语义

以下语义在本项目内已经固定，Windows `miniQMT` 项目若要对接，需要明确确认兼容性。

### 3.1 调用入口与请求头

- 执行入口：`POST /api/v1/task/execute`
- 结果入口：`GET /api/v1/task/result/{task_id}`
- `provider`：`qmt`
- `method`：`submit_order`
- 认证头：`Authorization: Bearer <TRADING_QMT_BRIDGE_TOKEN>`
- 版本头：`X-Bridge-Contract-Version: <TRADING_QMT_BRIDGE_CONTRACT_VERSION>`
- 当前默认 contract version：`1`

### 3.2 本项目已区分的三类 immediate outcome

本项目当前已经显式区分：

- `bridge_task_accepted`
- `broker_acknowledged`
- `submission_failed`

其中：

- `bridge_task_accepted` 只表示 Windows 侧已接受 transport task
- `broker_acknowledged` 才表示已拿到足够强的外部确认
- `submission_failed` 表示提交阶段已失败或无法形成可信受理

### 3.3 polling-first 原则

当前本项目默认以 `task_id` 为主键做 polling-first follow-up：

- 默认轮询超时：`TRADING_MINIQMT_LIVE_BRIDGE_TIMEOUT_SECONDS=15`
- 默认轮询间隔：`TRADING_MINIQMT_LIVE_BRIDGE_POLL_INTERVAL_SECONDS=1`

因此 Windows `miniQMT` 项目至少需要支持：

- receipt 阶段返回稳定 `task_id`
- 后续可通过 `task_id` 查询到 terminal result 或明确 pending 状态

### 3.4 不允许的行为

以下行为当前在本项目中被视为不兼容：

- 把 transport receipt 伪装成 broker acknowledgement
- 返回没有 `client_order_id` / `local_submission_id` 的“成功结果”
- 返回看似成功但无 `account_scope` 的结果
- 因 Windows 侧失败而让本项目 silent fallback 到 Tongdaxin
- 使用不透明状态文案，导致本项目无法判断 pending / terminal

---

## 4. 需要 miniQMT 项目明确回复的问题

请 Windows `miniQMT` 项目按下面各项给出明确答复。若某项当前做不到，请写清楚“现阶段不支持”和替代方案。

### 4.1 运行与部署形态

请确认：

- Windows 服务准备以什么形式运行：
  - 常驻 HTTP service
  - CLI + daemon wrapper
  - 任务调度器/守护进程
  - 其他
- 部署目标是单机单账户，还是单机多账户
- 进程重启后 `task_id` 查询能力是否保留
- 日志和结果证据保存在哪里
- 是否能提供 health / version 信息

请答复：

```text
1. 服务运行形态：
2. 账户模型：
3. 进程重启后的 task_id 保留策略：
4. 日志/证据落盘位置：
5. health/version 可见性：
```

### 4.2 execute contract 可行性

请确认 Windows `miniQMT` 项目是否可以稳定支持：

- `POST /api/v1/task/execute`
- `provider=qmt`
- `method=submit_order`
- Bearer token 认证
- `X-Bridge-Contract-Version` 校验

若不能完全兼容，请说明：

- 你们拟采用的路径
- 需要本项目适配的字段差异
- 是否需要 version negotiation

### 4.3 submission payload 映射

本项目当前希望提交 payload 至少可映射以下字段：

- `order_id`
- `client_order_id`
- `symbol`
- `quantity`
- `side`
- `order_type`
- `price`
- `request_id`
- `portfolio_id`
- `strategy_id`
- `actor_id`
- `source_id`

请 miniQMT 项目逐项回复：

- 哪些字段可直接接收
- 哪些字段需要重命名
- 哪些字段只是透传，不参与 SDK 下单
- 哪些字段必须新增

### 4.4 receipt 语义

请确认 execute 返回的第一阶段 receipt 是否能稳定提供：

- `task_id`
- `status`
- `timestamp` 或等价字段
- `source` 或等价字段
- `bridge_contract_version`

并请明确：

- receipt 是否只表示 transport accepted
- receipt 阶段是否绝不伪装成 broker acknowledgement
- 什么情况下会直接返回 terminal failure

### 4.5 result polling 与终态

请确认 `GET /api/v1/task/result/{task_id}` 的可行性，并明确：

- pending 状态集合
- terminal 状态集合
- `task_id` 过期策略
- 查询失败时的错误码/错误体
- 是否支持幂等重复查询

请 miniQMT 项目给出一份你们计划采用的状态枚举表。

### 4.6 identity echo 能力

这是本项目最关键的问题。请明确 Windows `miniQMT` 项目最终结果里能否稳定回传：

- `client_order_id`
- `local_submission_id`
- `account_scope`
- `broker_event_type`
- `external_order_id`
- `sequence_id`
- `event_id`
- `occurred_at`

若其中任何字段当前不稳定，请逐项说明：

- 是 SDK 无法提供
- 还是服务层尚未实现
- 还是可以提供但需要额外约束

### 4.7 failure semantics

请 miniQMT 项目明确哪些失败会被显式区分。至少需要回答是否可以稳定区分：

- auth failure
- unsupported version
- unsupported method
- provider unavailable
- SDK unavailable
- timeout
- identity mismatch
- broker reject
- network / transport error

并请说明这些失败在你们侧计划如何编码：

- HTTP status
- `reason_code`
- `reason_detail`
- 是否保留原始 SDK/柜台信息

### 4.8 live evidence 与审计

请说明 Windows `miniQMT` 项目准备向本项目暴露哪些 live evidence：

- 原始请求时间
- 原始 receipt 时间
- broker-facing 终态时间
- 原始错误文本
- SDK 侧订单号/合同号
- 原始 broker 回报片段

本项目不要求全部原样透传，但至少需要知道：

- 哪些证据你们能保留
- 哪些证据可查询
- 哪些证据只存在本地日志

### 4.9 Tongdaxin 补充通道边界

请 miniQMT 项目确认：

- 当 `miniQMT` timeout / unavailable / reject 时，Windows 侧不会自动调用 Tongdaxin
- 若未来要支持人工补单，必须显式标记为 operator handoff
- 任何 Tongdaxin continuation 都不能伪装成 `miniQMT` primary success

### 4.10 版本演进与兼容策略

请说明你们计划如何处理：

- `bridge_contract_version=1` 的兼容期
- 字段新增时是否向后兼容
- 状态枚举变更时如何通知本项目
- 是否需要单独的 `/version` 或 `/capabilities` endpoint

---

## 5. 建议 miniQMT 项目按此模板回复

建议你们直接复制下面模板回填：

```md
# miniQMT 项目对接回复

## 1. 运行形态
- 服务运行形态：
- 部署位置：
- 账户模型：
- task_id 保留策略：

## 2. execute contract
- 是否支持 POST /api/v1/task/execute：
- 是否支持 Bearer token：
- 是否支持 X-Bridge-Contract-Version：
- 不兼容点：

## 3. result contract
- 是否支持 GET /api/v1/task/result/{task_id}：
- pending 状态：
- terminal 状态：
- task_id 过期策略：

## 4. identity echo
- client_order_id：
- local_submission_id：
- account_scope：
- broker_event_type：
- external_order_id：
- sequence_id：
- event_id：
- occurred_at：

## 5. failure semantics
- auth failure：
- unsupported version：
- unsupported method：
- provider unavailable：
- SDK unavailable：
- timeout：
- broker reject：
- 其他：

## 6. evidence
- 可保留的原始证据：
- 可查询方式：
- 仅本地日志保留的证据：

## 7. Tongdaxin boundary
- 是否存在任何自动 fallback：
- 若需人工补单如何标记：

## 8. 需要 mystocks_spec 配合的事项
- 
```

---

## 6. 本项目收到回复后的处理原则

收到 Windows `miniQMT` 项目回复后，本项目会据此判断：

1. 当前 `windows_bridge_adapter` / `miniqmt_live_bridge` 是否需要字段适配。
2. 当前 `bridge_contract_version=1` 是否足够继续沿用。
3. 哪些 failure class 可以在本项目内收敛成 canonical runtime evidence。
4. 是否需要新开 OpenSpec change 来承接跨项目对接改造。

在拿到明确回复前，本项目会继续坚持以下边界：

- `miniQMT` 仍是 `primary-candidate`，不是 production-ready truth source
- Tongdaxin 仍是 `supplemental / operator-assisted / review-first`
- 没有 identity echo，就不推进 broker truth

---

## 7. 相关参考

- [`broker-execution-truth-registry.md`](./broker-execution-truth-registry.md)
- [`windows-qmt-agent-live-contract-requirements-review.md`](./windows-qmt-agent-live-contract-requirements-review.md)
- `src/application/trading/order_mgmt_service.py`
- `src/application/trading/miniqmt_primary_runtime.py`
- `src/application/trading/miniqmt_live_bridge_followup.py`
- `web/backend/app/services/windows_bridge_adapter.py`
- `web/backend/app/services/miniqmt_live_bridge.py`
