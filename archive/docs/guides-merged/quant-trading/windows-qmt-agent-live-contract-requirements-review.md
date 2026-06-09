# Windows qmt Agent 与 Live Contract 对接要求（审核稿）

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。
> 日期：2026-04-29
> 状态：审核稿
> 适用范围：`miniQMT` 主 broker-truth 通道，不适用于 Tongdaxin 半手工补充通道自动化升级

## 1. 文档目的

本文从 **本项目当前仓库与既有 broker-truth 主线** 的角度，整理 Windows `qmt` agent 与 live contract 对接时必须满足的具体要求。

本文回答的是：

1. Ubuntu / WSL 侧仓库希望 Windows `qmt` agent 提供什么能力。
2. Ubuntu / WSL 与 Windows 之间的 live contract 应该长什么样。
3. 哪些字段、状态和失败语义是本项目必须显式定义的。
4. 哪些行为在本项目中明确禁止。

本文**不**宣称当前仓库已经拥有 production-ready 的 `miniQMT` live trading adapter。

若真实 Windows `miniQMT` SDK adapter 由独立项目开发，请同时把 [`miniqmt-project-alignment-questionnaire.md`](./miniqmt-project-alignment-questionnaire.md) 发给对方项目回填，以便本项目据此冻结跨项目接口边界。

---

## 2. 当前项目事实边界

当前仓库已经完成的，是 repo-facing contract 和 ledger 层，而不是已验证的生产级 Windows 柜台接入：

- `OrderManagementService` 是当前交易域的 canonical local anchor。
- `miniQMT` 已被确定为第一条 `primary-candidate` broker-truth 通道。
- 当前仓库已经具备：
  - primary-path submission classification
  - `bridge_task_id` 持久化
  - polling-first live bridge result retrieval contract
  - deferred broker lifecycle re-entry
  - timeout / unavailable / identity mismatch 的 review-required evidence
  - Tongdaxin supplemental handoff 的显式边界
  - repo-owned Windows `qmt` reference service：`scripts/windows_qmt_agent/`
    - authenticated/versioned execute/result endpoints
    - in-memory `task_id` registry
    - `mock` / `miniqmt_sdk` provider mode disclosure
    - `miniqmt_sdk` unavailable 时 fail-closed
- 当前仓库**尚未证明**：
  - live `miniQMT` SDK provider 已稳定实现
  - live broker adapter 已被生产验证
  - broker callback / push ingress 已有可信认证闭环
  - `miniQMT` 路径可升级为 production-eligible

当前实现锚点：

- `web/backend/app/services/windows_bridge_adapter.py`
- `web/backend/app/services/miniqmt_live_bridge.py`
- `scripts/windows_qmt_agent/app.py`
- `scripts/windows_qmt_agent/service.py`
- `scripts/templates/windows_task_node.py`
- `src/application/trading/miniqmt_primary_runtime.py`
- `src/application/trading/miniqmt_live_bridge_followup.py`
- `src/application/trading/order_mgmt_service.py`
- `docs/guides/quant-trading/broker-execution-truth-registry.md`

---

## 2.1 当前仓库已冻结的 v1 contract 决策

截至当前仓库实现，Ubuntu / WSL 侧已经把以下 contract 决策收敛成 repo-owned 事实：

- 提交入口只允许：`provider=qmt` + `method=submit_order`
- 结果查询入口只允许：`GET /api/v1/task/result/{task_id}`
- 认证头固定为：`Authorization: Bearer <TRADING_QMT_BRIDGE_TOKEN>`
- 版本头固定为：`X-Bridge-Contract-Version: <TRADING_QMT_BRIDGE_CONTRACT_VERSION>`
- 当前默认 contract version：`1`
- 轮询超时默认值：`TRADING_MINIQMT_LIVE_BRIDGE_TIMEOUT_SECONDS=15`
- 轮询间隔默认值：`TRADING_MINIQMT_LIVE_BRIDGE_POLL_INTERVAL_SECONDS=1`
- execute/result 两条链路都必须回显：`bridge_contract_version`
- auth/version/whitelist failure 当前都只能落为 review-required runtime evidence，不能推进 broker truth

实现位置：

- `src/utils/trading_runtime_config.py`
- `web/backend/app/services/windows_bridge_adapter.py`
- `web/backend/app/services/miniqmt_live_bridge.py`
- `src/application/trading/miniqmt_live_bridge_followup.py`

---

## 3. 角色边界要求

### 3.1 Ubuntu / WSL 仓库侧职责

Ubuntu / WSL 仓库侧负责：

- 生成本地订单与本地 submission identity
- 持久化 `bridge_task_id`
- 轮询 Windows `qmt` agent 获取结果
- 将 broker-facing 结果重新接回 shared lifecycle ledger
- 在证据不足时落 divergence / review-required evidence
- 维持 `miniQMT primary / Tongdaxin supplemental` 的权限边界

Ubuntu / WSL 仓库侧**不应**负责：

- 猜测 broker acknowledgement
- 通过 symbol / quantity / timing 模糊匹配真实外部订单
- 在没有 identity echo 的情况下自动绑定 broker truth
- silent fallback 到 Tongdaxin

### 3.2 Windows qmt Agent 职责

Windows `qmt` agent 必须负责：

- 接受来自 Ubuntu / WSL 的 `qmt/submit_order` 请求
- 返回 transport-stage receipt
- 提供 `task_id -> result` 的稳定查询能力
- 在最终结果中回传足够的 identity echo
- 将 broker-facing 结果和 transport receipt 严格区分

Windows `qmt` agent **不应**：

- 把 transport acceptance 伪装成 broker acknowledgement
- 返回缺失关键 identity 的“半结果”并期待 Ubuntu / WSL 自动猜测
- 将 Tongdaxin 视为隐式 fallback

### 3.3 Tongdaxin 补充通道职责

Tongdaxin 在本项目中仍然是：

- `supplemental`
- `operator-assisted`
- `review-first`

因此：

- Tongdaxin 只能作为显式 operator escalation 后的补充路径
- 不能因为 `miniQMT` timeout 或 unavailable 就自动接管
- 不能继承 `miniQMT` 的自动 replay suppression / auto-resolution authority

---

## 4. Windows qmt Agent 的最小接口要求

### 4.1 提交接口

Windows `qmt` agent 必须提供一个可由 Ubuntu / WSL 侧调用的提交入口，当前项目假定语义为：

- 请求路径：`/api/v1/task/execute`
- provider：`qmt`
- method：`submit_order`

Ubuntu / WSL 当前期望最小提交 payload 至少包括：

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

除此之外，Ubuntu / WSL 当前已经把 remote call surface 明确限制为：

- execute 只能走 `qmt/submit_order`
- result retrieval 只能走 `provider_name=qmt`
- 任何 provider / method 越界都必须显式返回 `live_bridge_unsupported_method`

### 4.2 提交回执要求

Windows `qmt` agent 返回的 submission receipt，必须至少包含：

- `task_id`
- `status` 或等价 transport 状态
- `timestamp` 或 `receipt_timestamp`
- `source` 或 `source_name`
- `bridge_contract_version`

Ubuntu / WSL 仓库会把这类回执解释为：

- `bridge_submission_receipt`

而不是：

- broker acknowledgement
- external order identity binding

### 4.3 结果查询接口

Windows `qmt` agent 必须提供一个稳定的结果查询入口，当前项目建议标准化为：

- 请求路径：`/api/v1/task/result/{task_id}`

项目当前实现优先支持：

- polling-first

原因是：

- 仓库内已经有 `task_id`
- callback ingress 尚无现成认证闭环
- polling 更容易观察、测试和收敛

### 4.4 结果查询状态要求

Windows `qmt` agent 返回的结果查询状态必须可区分：

- pending：`accepted` / `pending` / `processing` / `queued` / `running` / `submitted`
- terminal：`completed` / `success` / `succeeded` / `failed` / `error` / `rejected` / `cancelled`

禁止返回“语义模糊但看起来像成功”的状态。

---

## 5. Live Result Payload 的强制字段要求

当 Windows `qmt` agent 返回 broker-facing 结果时，payload 必须至少支持以下字段回传：

- `task_id`
- `provider`
- `method`
- `result_status`
- `occurred_at`
- `client_order_id` 或 `local_submission_id`
- `account_scope`
- `broker_event_type`
- `external_order_id`（若已拿到 broker acknowledgement）
- `sequence_id`（若 broker 侧存在事件序列标识）

补充建议字段：

- `event_id`
- `reason_code`
- `reason_detail`
- `filled_quantity`
- `fill_price`
- `source_name`

---

## 6. Identity Echo 与绑定要求

### 6.1 最低绑定条件

Ubuntu / WSL 仓库允许 broker truth 前进的前提是：

- live result 回传了 `client_order_id` 或 `local_submission_id`
- 该 identity 与本地 recorded submission trail 明确匹配
- `account_scope` 不冲突
- 若事件为 acknowledgement，则 `external_order_id` 可被安全记录

### 6.2 明确禁止的绑定方式

以下方式在本项目中都不允许作为自动绑定依据：

- 仅按 `symbol`
- 仅按数量接近
- 仅按时间接近
- 仅按 broker 返回“像是成功”的状态文案
- 仅因同一 session 里只有一笔订单而推断匹配

### 6.3 mismatch 的处理要求

若 Windows `qmt` agent 返回的 identity 与 recorded submission trail 不匹配，Ubuntu / WSL 仓库必须：

- 记录 review-required divergence
- 保留 `bridge_task_id`
- 保留 raw result evidence
- 禁止推进 broker acknowledgement binding

---

## 7. 生命周期事件要求

Windows `qmt` agent 的 broker-facing 结果，至少应能映射到以下四类事件：

- `acknowledgement`
- `reject`
- `cancel`
- `execution`

如果 agent 使用自定义状态名，也必须能稳定映射到以上 canonical event types。

当前仓库已接受的典型映射包括：

- `accepted` -> `acknowledgement`
- `rejected` -> `reject`
- `cancelled` -> `cancel`
- `filled` / `traded` / `execution` -> `execution`

---

## 8. 失败与升级语义要求

### 8.1 timeout

若 Ubuntu / WSL 在配置时限内没有拿到安全结果，必须视为：

- `live_bridge_timeout`

而不是：

- broker reject
- broker cancel
- implicit Tongdaxin handoff

### 8.2 bridge unavailable

若 Windows `qmt` agent 无法连接、结果接口缺失或查询异常，必须视为：

- `live_bridge_unavailable`

同样不能伪造 broker-facing terminal state。

### 8.3 invalid result

若结果 payload 缺字段、格式错误或状态不受支持，必须视为：

- `live_bridge_invalid_result`

### 8.4 auth / version / whitelist failure

若 Windows `qmt` agent 在 execute 或 result retrieval 边界返回以下失败：

- 认证失败
- contract version 不匹配
- provider / method 不在白名单

Ubuntu / WSL 仓库必须分别落为：

- `live_bridge_auth_failed`
- `live_bridge_unsupported_contract_version`
- `live_bridge_unsupported_method`

这些都属于 transport / contract failure，不得被解释为：

- broker reject
- broker cancel
- broker execution

### 8.5 operator escalation

当出现 timeout / unavailable / mismatch / invalid result 时，系统下一步必须是：

- `operator_review_or_tdx_supplemental_handoff`

这里的 Tongdaxin 只能通过显式操作触发，不能 silent fallback。

---

## 9. 审计与证据保留要求

Windows `qmt` agent 对接后，Ubuntu / WSL 侧至少要能保留三类证据：

1. 本地 submission evidence
2. transport receipt evidence
3. live result / divergence evidence

因此 agent 必须确保以下信息能够被仓库保留下来：

- `task_id`
- 原始返回 payload
- broker-facing result payload
- `external_order_id`
- `sequence_id`
- `reason_code` / `reason_detail`
- 时间戳

若后续升级到 Tongdaxin supplemental path，handoff record 中还必须保留：

- prior primary submission attempt
- prior live bridge evidence
- prior `bridge_task_id`

---

## 10. 安全与认证要求

从本项目角度，Windows `qmt` agent 至少需要满足以下安全要求：

- Ubuntu / WSL 到 Windows 的调用必须有认证机制，不能裸开放内网接口
- 结果查询接口必须与提交接口共享一致的认证语义
- agent 必须限制 provider 与 method 白名单，不能接受任意远程命令
- 日志中不得泄露敏感账户凭证
- 若回传账户标识，应使用项目可接受的 `account_scope` 表达，而不是裸凭证

当前仓库已经把 Ubuntu / WSL 侧最小认证契约固定为：

- `TRADING_QMT_BRIDGE_TOKEN`
- `Authorization: Bearer <token>`
- `X-Bridge-Contract-Version: 1`

但这仍然只是 repo-owned contract，不等于 Windows agent 生产认证方案已验证。

---

## 11. 运行与可观测性要求

Windows `qmt` agent 对接后，至少需要满足以下运维要求：

- 可报告健康状态
- 可区分提交成功、结果 pending、结果 terminal、结果异常
- polling 超时预算可配置
- polling 间隔可配置
- agent 端错误需要返回可审计的 `reason_code` / `reason_detail`
- 不能让 Ubuntu / WSL 侧只能看到“任务没回来”，却完全没有失败原因

建议最小运维指标：

- 提交成功率
- 结果查询成功率
- 平均确认延迟
- timeout 数量
- mismatch 数量
- explicit supplemental handoff 数量

---

## 12. 测试与验收要求

### 12.1 Ubuntu / WSL 仓库侧最低验收

在本项目内，至少要覆盖以下场景：

- submission receipt normalization
- authenticated execute header / whitelist enforcement
- `task_id` polling result retrieval
- auth failure / contract-version mismatch / unsupported method normalization
- canonical acknowledgement re-entry
- timeout divergence persistence
- identity mismatch divergence persistence
- explicit Tongdaxin supplemental handoff with prior evidence retention

### 12.2 Windows qmt Agent 联调最低验收

建议联调必须至少证明：

1. 提交后能稳定返回 `task_id`
2. 同一 `task_id` 可稳定轮询到 terminal result
3. result payload 能回传 `client_order_id` 或 `local_submission_id`
4. acknowledgement 能稳定回传 `external_order_id`
5. 失败时能回传明确 `reason_code` / `reason_detail`
6. timeout / unavailable 不会被误记成 broker reject

---

## 13. 明确非目标

当前项目阶段，Windows `qmt` agent 与 live contract 对接**不应**顺带承担以下目标：

- 多 broker routing
- 策略编排升级
- Tongdaxin 自动化权限提升
- 无证据的 replay suppression 扩大化
- production-ready 宣称

---

## 14. 审核建议

你审核时，建议重点看 6 个问题：

1. Windows `qmt` agent 是否真的能稳定提供 `task_id -> result` 查询。
2. result payload 是否真的能稳定回传 `client_order_id/local_submission_id`。
3. `external_order_id` 与 `sequence_id` 是否可持续获得，而不是偶发字段。
4. 认证方案是否足以让 Windows agent 不成为裸露远程执行面。
5. timeout / unavailable / mismatch 是否都能被可靠地区分。
6. Tongdaxin 是否仍被严格限制在显式 handoff 的补充通道，不会被隐式自动接管。

---

## 15. 当前建议结论

从本项目当前阶段看，Windows `qmt` agent 与 live contract 对接的正确目标不是“马上宣称实盘可用”，而是先做到：

- 有稳定 receipt
- 有稳定 `task_id -> result`
- 有稳定 identity echo
- 有明确失败语义
- 有 review-first escalation 边界

只有这些都成立后，项目才有资格继续讨论：

- verified live broker adapter
- production reconciliation workflow
- production-eligible trading path
