# miniQMT 项目审核反馈与对接答复

> **权威来源声明**:
> 本文件是 `mystocks_spec` 对独立 Windows `miniQMT` 项目开发文档与待确认事项的审核反馈，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及当前 broker-truth 实现事实，请同时核对根目录 `AGENTS.md`、`openspec/AGENTS.md`、相关 OpenSpec change 与当前代码。
> 日期：2026-04-29
> 状态：可回传 miniQMT 项目
> 适用范围：`/opt/claude/mystocks_spec` 对 `/mnt/d/MyCode3/miniQMT` 下列文档的审核与反馈
>
> - `/mnt/d/MyCode3/miniQMT/DOCS/项目说明/miniQMT-Windows-qmt-agent-live-contract-开发文档.md`
> - `/mnt/d/MyCode3/miniQMT/DOCS/项目说明/miniQMT-对接反馈-待确认事项.md`

## 1. 审核结论

整体判断：**方向基本对齐，可以继续推进，但有 5 个 contract 边界需要明确收紧。**

对齐的部分包括：

- `contract first`
- `identity first`
- `failure explicit`
- `review first`
- `no silent fallback`
- `miniQMT primary / Tongdaxin supplemental`
- execute receipt 与 broker-facing result 明确分离
- 接受 Phase A / B 分阶段落地

需要收紧的部分包括：

1. 本项目对外 canonical auth contract 已冻结为 `Authorization: Bearer <TRADING_QMT_BRIDGE_TOKEN>`，不是 `X-MiniQMT-Api-Key`。
2. `account_scope` 不建议继续放到 Phase B；即使是单机单账户，也应在 v1 由服务层稳定合成。
3. `event_id` 不建议继续放空到后续阶段；它可以是服务层生成值，不要求 broker-native，但建议作为 v1 必需字段之一。
4. 文件日志本身不足以支撑本项目的 polling-first + review-first 边界；v1 需要**可跨重启保留的结构化 task/result persistence**。
5. live 模式下不能返回服务层伪造的 `external_order_id` 来冒充 broker identity；若 broker 侧尚未给出，就应为空并显式说明状态。

---

## 2. 对 miniQMT 开发文档的专项审核

### 2.1 可以接受并建议保留的设计点

以下内容与本项目当前 broker-truth 主线一致，建议 miniQMT 项目继续沿用：

- 以 `POST /api/v1/task/execute` + `GET /api/v1/task/result/{task_id}` 作为 v1 主 contract
- `provider=qmt`、`method=submit_order` 白名单固定
- `task_id` 作为 polling-first 主键
- execute receipt 不等于 broker acknowledgement
- broker-facing lifecycle 固定为 `acknowledgement / reject / cancel / execution`
- 将 `live_bridge_timeout`、`live_bridge_unavailable`、`live_bridge_invalid_result`、`live_bridge_auth_failed`、`live_bridge_unsupported_contract_version`、`live_bridge_unsupported_method` 作为独立失败类
- 明确 Tongdaxin 不得 silent fallback
- 接受“先 contract 固化，再补 callback/lifecycle 完整映射”的阶段化实施方式

### 2.2 需要 miniQMT 项目修正或补充澄清的点

#### A. 认证头口径

本项目在 `WSL 上的 Ubuntu 24.04.4 LTS` 这一侧已经冻结的 canonical contract 是：

- `Authorization: Bearer <TRADING_QMT_BRIDGE_TOKEN>`

因此：

- miniQMT 项目**可以**在内部迁移期兼容 `X-MiniQMT-Api-Key`
- 但 miniQMT 项目**不应**把旧 header 继续写成与 `mystocks_spec` 的对外 canonical contract
- 换句话说：
  - **对外 contract 文档**：应以 Bearer 为唯一主口径
  - **兼容实现策略**：可在你们内部保留双支持，直到完全切换

#### B. `account_scope`

本项目建议把 `account_scope` 提前到 v1，而不是 Phase B。

原因不是当前马上要做多账户，而是：

- broker truth 绑定不应把“当前恰好只有一个账户”当作长期隐含前提
- 单机单账户模式下，`account_scope` 仍然可以由服务层稳定合成
- 这比后续再 retrofitting 成本更低

可接受的 v1 方案：

- 由配置中的账户标识稳定合成，例如：
  - `qmt:<account_id>`
  - 或其他等价、稳定、不可歧义的字符串

#### C. `event_id` 与 `sequence_id`

本项目不要求 `event_id` / `sequence_id` 一定来自 broker-native 字段。

要求应拆开看：

- `event_id`：建议作为 **v1 必需字段**
  - 可以由 miniQMT 服务层生成
  - 目标是支持去重、审计与后续 replay 判断
- `sequence_id`：可以作为 **Phase B 可选增强**
  - 若 SDK 或服务层暂时没有稳定序列能力，可后补

也就是说，本项目的口径不是“两个都必须是柜台原生值”，而是：

- `event_id` 要有
- `sequence_id` 可以稍后补

#### D. `occurred_at` 语义

本项目接受 v1 的 `occurred_at` 先采用：

- **服务层观测到该结果的 UTC 时间**

不要求 v1 一开始就保证它是 broker-native event time。

但请 miniQMT 项目在文档里明确这一点，避免语义漂移。推荐口径：

- `occurred_at`：服务层归一化 UTC 时间
- 若未来拿到更强 broker 原生时间，可新增字段，而不是悄悄改变 `occurred_at` 含义

#### E. live 模式下禁止伪造 `external_order_id`

本项目明确要求：

- mock/preview 模式可以有模拟 `external_order_id`
- 但 live 模式下，如果 broker/SDK 尚未返回稳定外部订单号，就必须返回空值或缺省，并以状态/原因说明

不能用服务层自造的 `external_order_id` 冒充真实 broker identity。

---

## 3. 对《待确认事项》的正式答复

### 3.1 关于 2.1「认证头适配方案」

本项目答复：

- `mystocks_spec` 对外只会按 **Bearer** 口径调用
- miniQMT 项目若出于平滑迁移考虑，在 Windows 侧内部短期兼容 `X-MiniQMT-Api-Key`，这是你们的实现细节
- 但 miniQMT 项目回给本项目的对接文档，应把：
  - `Authorization: Bearer <TRADING_QMT_BRIDGE_TOKEN>`
  - `X-Bridge-Contract-Version`
  作为 v1 canonical contract

因此结论是：

- **对外 contract**：Bearer-only
- **内部过渡实现**：可双支持，但不是要本项目配合双口径

### 3.2 关于 2.2「任务持久化策略」

本项目最低要求如下：

- `task_id` 查询能力必须**跨进程重启保留**
- 至少要保留到：
  - task 进入 terminal 状态后仍可查询
  - 且 review-first 场景下不会因 agent 重启立即丢证据

本项目建议：

- v1 采用 SQLite

原因：

- 单机常驻 Windows 服务场景下，SQLite 足够轻量
- 比 JSON file 更适合状态查询、恢复与索引
- 比 Redis 更少额外依赖

关于 retention period，本项目口径是：

- **硬最低要求**：terminal task/result/evidence 至少保留 `24h`
- **推荐值**：至少保留 `7d`

单纯 file log 不足以替代结构化 persistence。

### 3.3 关于 2.3「Identity echo 可提供字段确认」

本项目建议把字段分成三层：

#### v1 硬要求

- `client_order_id` 或 `local_submission_id`
  - 二者至少其一必须稳定存在
  - 若当前没有独立 `local_submission_id`，则 `client_order_id` 必须稳定回显
- `broker_event_type`
- `account_scope`
  - 可由单账户配置稳定合成
- `occurred_at`
  - v1 允许用服务层 UTC 观测时间
- `event_id`
  - 可由服务层生成

#### 条件硬要求

- `external_order_id`
  - 当 broker/SDK 已经分配外部订单号时，必须返回
  - 若该阶段客观上尚未拿到，就不应伪造

#### Phase B 可补

- `sequence_id`
- 更强语义的 broker-native timestamp
- 更完整的 lifecycle event correlation

### 3.4 关于 2.4「xtquant SDK 实际下单能力边界」

本项目接受分阶段落地。

也就是说：

- **接受 Phase A**：先交付 transport receipt + polling result + 明确 bridge failure semantics
- **接受 Phase B**：再补 callback 驱动的 full lifecycle mapping

但要强调两点：

1. Phase A 不能只停留在“receipt 成功”
   - 它仍然必须提供：
     - `task_id`
     - 可轮询结果
     - pending / terminal 区分
     - `reason_code` / `reason_detail`
2. 本项目并不要求把第一阶段 receipt 解释成强 broker acknowledgement
   - 这点与你们文档判断一致

### 3.5 关于 2.5「审计证据存储范围」

本项目答复：

- v1 **不要求**单独做一个 evidence query API
- 但 v1 **要求**：
  - `GET /api/v1/task/result/{task_id}` 可基于持久化结果返回 task 最终状态
  - 能保留最小必要 evidence reference
  - agent 重启后这些 task/result 仍可查询

因此：

- **文件日志 alone**：不够
- **结构化任务表 + 文件日志**：可以接受

建议保留的最小 evidence：

- 请求时间
- receipt 时间
- terminal/update 时间
- `client_order_id`
- `task_id`
- `account_scope`
- `broker_event_type`
- `reason_code`
- `reason_detail`
- 原始 broker/SDK 结果片段或其引用键

### 3.6 关于 2.6「部署形态决策」

本项目接受以下 v1 默认边界：

- 单机
- 单账户
- Windows 常驻 HTTP service

这与本项目当前接口边界是兼容的，也是目前最合理的收敛方式。

如果后续你们要扩展到多账户：

- 不应复用当前“默认单账户隐含前提”
- 应以新 contract 或新能力协商方式推进

---

## 4. 本项目额外提出的具体要求

除了答复待确认事项外，本项目还希望 miniQMT 项目在开发与文档里补齐以下要求。

### 4.1 execute receipt 与 result 都必须回显 `bridge_contract_version`

不只是请求头校验。

还应在：

- execute receipt
- result payload

中明确回显 `bridge_contract_version`，避免双端难以审计“这是按哪个 contract 处理的结果”。

### 4.2 `/capabilities` 或 `/health` 需要显式暴露 contract 关键信息

建议至少返回：

- `bridge_contract_version`
- `auth_mode`
- `provider_modes`
- `task_persistence_mode`
- `single_account_mode`

不一定必须新开 `/version`，但现有 capability surface 需要能支撑排障。

### 4.3 mock / preview 不得和 live contract 混淆

本项目希望 miniQMT 项目明确区分：

- mock / preview path
- canonical live bridge path

至少应做到：

- mock 结果显式标记 `source_name=mock` 或等价字段
- 文档中不要把 preview 返回的 `acknowledgement` 当作 live broker truth 证据
- live mode unavailable 时 fail-closed，而不是偷偷降级成 mock success

### 4.4 需要冻结一份稳定的状态枚举表

请 miniQMT 项目后续给本项目一份最终状态枚举表，至少覆盖：

- pending
- terminal success/failure
- broker-facing event types
- bridge failure types

本项目不要求状态名字必须照搬某个内部实现，但要求：

- 语义稳定
- pending 与 terminal 不混淆
- bridge failure 与 broker reject 不混淆

### 4.5 `identity mismatch` 需要独立 failure path

即使 v1 先不做复杂自动绑定，本项目仍希望你们预留：

- `identity_mismatch`
- 或等价明确的 failure class

原因是：

- 一旦 result payload 带回了 `client_order_id` / `external_order_id` / `account_scope`
- 本项目需要能明确区分：
  - “无结果”
  - “结果无效”
  - “结果有了，但身份对不上”

### 4.6 时间统一使用 UTC ISO8601

本项目建议 miniQMT 项目在 v1 统一：

- UTC
- ISO8601

不要让 receipt time、service observed time、broker callback time 混入本地时区自由格式。

---

## 5. 对 miniQMT 项目当前文档的综合建议

若 miniQMT 项目要继续完善你们那两份文档，我建议这样改：

1. 在开发文档里把 “Bearer 是 canonical，旧 API key 仅内部兼容策略” 写明。
2. 在待确认事项里把 `account_scope` 从“是否可放到 Phase B”改为“v1 由服务层稳定合成”。
3. 把 `event_id` 从“当前不支持”改为“服务层生成，纳入 v1”。
4. 把 `occurred_at` 语义冻结为“服务层 UTC 观测时间”，不要悬空。
5. 把 task persistence 从“建议 SQLite”升级为“v1 要求”。
6. 加一条 live mode 要求：没有真实外部订单号时不得伪造 `external_order_id`。
7. 在 `/capabilities` 或等价文档里明确 `bridge_contract_version` 与 persistence mode。

---

## 6. 当前对接边界结论

在拿到 miniQMT 项目下一轮修订前，本项目的边界结论维持如下：

- `mystocks_spec` 只负责 `WSL 上的 Ubuntu 24.04.4 LTS` 这一侧的 contract 调用、task polling、ledger re-entry 与 review-first boundary
- miniQMT 项目负责真实 Windows SDK adapter、运行时服务、task persistence、identity echo 与 broker-facing evidence
- `miniQMT` 仍是 `primary-candidate`
- Tongdaxin 仍是 `supplemental / operator-assisted / review-first`
- 没有 identity echo，就不推进 broker truth
- 没有结构化 persistence，就不认为 polling-first contract 已真正闭环

---

## 7. 相关参考

- [`miniqmt-project-alignment-questionnaire.md`](./miniqmt-project-alignment-questionnaire.md)
- [`windows-qmt-agent-live-contract-requirements-review.md`](./windows-qmt-agent-live-contract-requirements-review.md)
- [`broker-execution-truth-registry.md`](./broker-execution-truth-registry.md)
