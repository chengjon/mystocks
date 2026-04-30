# Windows qmt Service Ready Checklist

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。
> 日期：2026-04-30
> 状态：活跃
> 适用范围：Windows 侧 `miniQMT` bridge / service readiness，自检后再与 `mystocks_spec` 在 `WSL 上的 Ubuntu 24.04.4 LTS` 侧联调

## 1. 文档目的

本文回答一个很具体的问题：

- 对 `mystocks_spec` 来说，什么时候可以说 Windows 侧的 `miniQMT` service ready 了？

这里的 `service ready` 不是单指：

- `D:\国金QMT交易端模拟\bin.x64\XtItClient.exe` 已启动

也不是单指：

- `D:\MyCode3\miniQMT` 里的代码已经写完

而是要求这两部分已经通过 bridge/service 收敛成一个**可被 `WSL 上的 Ubuntu 24.04.4 LTS` 侧稳定访问和验证的 HTTP contract**。

---

## 2. 两个 Windows 路径的角色区分

### 2.1 `D:\MyCode3\miniQMT`

这是 Windows 侧 bridge / service 项目的工作目录。

它应负责：

- HTTP service 启动
- `task/execute + task/result` contract
- 认证、版本、状态、失败语义
- task/result 持久化
- 与 `miniQMT` SDK / 柜台程序的桥接

### 2.2 `D:\国金QMT交易端模拟\bin.x64\XtItClient.exe`

这是实际运行的 `miniQMT` 客户端/柜台程序。

它应被视为：

- Windows bridge 的底层依赖
- 不是给 `mystocks_spec` 直接调用的对外服务

因此：

- `XtItClient.exe` 已启动，不等于 service ready
- 只有当 `D:\MyCode3\miniQMT` 中的 bridge/service 已经把它包装成稳定可调用 contract，才可进入本项目联调

---

## 3. Ready 分级

建议把 Windows 侧 readiness 分成 3 个等级。

### 3.1 L1: 进程就绪

这一级只表示“Windows 侧能跑起来”。

必须满足：

- [ ] `XtItClient.exe` 已启动
- [ ] `D:\MyCode3\miniQMT` 中的 bridge/service 进程已启动
- [ ] bridge/service 有固定 `base_url`
- [ ] 从 `WSL 上的 Ubuntu 24.04.4 LTS` 可以访问该 `base_url`
- [ ] `GET /health` 返回 JSON，而不是超时、空响应或错误页

若 L1 都不成立，本项目不应进入合同联调。

### 3.2 L2: 合同就绪

这一级表示“Windows service 已具备 Phase A contract ready”。

必须满足：

- [ ] `GET /health` 可用
- [ ] `POST /api/v1/task/execute` 可用
- [ ] `GET /api/v1/task/result/{task_id}` 可用
- [ ] 认证头支持：`Authorization: Bearer <TRADING_QMT_BRIDGE_TOKEN>`
- [ ] 版本头支持：`X-Bridge-Contract-Version: 1`
- [ ] execute 只接受 `provider=qmt`
- [ ] execute 只接受 `method=submit_order`
- [ ] receipt 明确表示 transport acceptance，而不是 broker acknowledgement
- [ ] `task_id` 可以稳定轮询
- [ ] result 能区分 pending / terminal
- [ ] result 能回传 identity echo
- [ ] task/result 有结构化持久化，而不是只写文件日志

### 3.3 L3: 本项目联调就绪

这一级表示“已经可以让 `mystocks_spec` 正式跑本地 formal sequence”。

必须满足：

- [ ] `TRADING_QMT_BRIDGE_TOKEN` 已配置给本项目侧
- [ ] 本项目侧已知道 `base_url`
- [ ] `/health` 返回的 `provider_mode` 与当前联调目标一致
- [ ] `/health` 返回 `bridge_contract_version`
- [ ] `/health` 返回 `bridge_auth_configured=true`
- [ ] Windows service 在 mock / live 模式下都能给出显式失败语义
- [ ] 不会伪造 `external_order_id`
- [ ] `source_name` 口径与当前 profile 一致

达到 L3 后，才适合在本项目里运行：

```bash
python scripts/dev/run_windows_qmt_contract_formal_sequence.py \
  --base-url http://<windows-host>:8001 \
  --report-dir docs/reports/quality/windows-qmt-contract-acceptance
```

---

## 4. L1 进程就绪 Checklist

### 4.1 Windows 运行环境

- [ ] Windows 机器已启动并保持稳定
- [ ] `XtItClient.exe` 已手工确认在运行
- [ ] 当前使用的是模拟环境，而不是误接生产环境
- [ ] `D:\MyCode3\miniQMT` 中的 service 可启动且无立即崩溃
- [ ] service 监听端口已确定，例如 `8001`

### 4.2 Ubuntu / WSL 可达性

- [ ] 从 `WSL 上的 Ubuntu 24.04.4 LTS` 可以访问 Windows 侧 `base_url`
- [ ] 没有本机防火墙把该端口拦掉
- [ ] 没有反向代理/隧道把路径或 header 改写掉

L1 最小证据建议：

- `XtItClient.exe` 正常运行截图或本地检查记录
- Windows service 监听端口记录
- `/health` 原始返回 JSON

---

## 5. L2 合同就绪 Checklist

### 5.1 `/health` 必须可回答

- [ ] 返回 JSON object
- [ ] 含 `status`
- [ ] 含 `provider_mode`
- [ ] 含 `bridge_contract_version`
- [ ] 含 `bridge_auth_configured`
- [ ] 含 `source_name`

建议当前 mock-mode 先达到：

- [ ] `provider_mode=mock`
- [ ] `source_name=mock`

若已进入 live 探索：

- [ ] `provider_mode=live`
- [ ] `source_name=live`

### 5.2 execute receipt 必须明确是 transport-stage

- [ ] execute 成功时返回 `task_id`
- [ ] execute 成功时返回 receipt 时间
- [ ] execute 成功时返回 `bridge_contract_version`
- [ ] execute receipt 不被写成 broker acknowledgement
- [ ] execute 失败时能显式给出失败语义

### 5.3 result polling 必须可判定

- [ ] `task_id` 可用于 result 查询
- [ ] pending 状态集合明确
- [ ] terminal 状态集合明确
- [ ] 结果体至少有：
  - [ ] `occurred_at`
  - [ ] `source_name`
  - [ ] `account_scope`
  - [ ] `event_id`
  - [ ] `bridge_contract_version`
  - [ ] `client_order_id` 或 `local_submission_id`
- [ ] `broker_event_type` 在 Phase A 允许为 `null`
- [ ] `external_order_id` 只有真实可得时才返回

### 5.4 结构化持久化

- [ ] `task_id -> result` 查询跨 service 重启仍可保留
- [ ] terminal result 至少保留 `24h`
- [ ] 推荐保留 `7d`
- [ ] 当前使用 SQLite 或等价结构化 persistence

L2 最小证据建议：

- `/health` 样例
- execute receipt 样例
- pending result 样例
- terminal result 样例
- 重启后仍可查询的证明

---

## 6. L3 本项目联调就绪 Checklist

### 6.1 本项目侧已具备的输入

- [ ] Windows `base_url` 已确定
- [ ] `TRADING_QMT_BRIDGE_TOKEN` 已准备
- [ ] 当前联调 profile 已决定
  - [ ] `kernel-phase-a`
- [ ] 当前 provider mode 已决定
  - [ ] `mock`
  - [ ] 或 `live`

### 6.2 对本项目的最低兼容性

- [ ] 对外 canonical auth 是 Bearer，而不是要求本项目用旧 API key
- [ ] 对外 canonical version 是 `X-Bridge-Contract-Version`
- [ ] `source_name` 只用 `mock` / `live`
- [ ] `account_scope` 稳定存在
- [ ] `event_id` 稳定存在
- [ ] 若无 broker lifecycle truth，不伪造 `broker_event_type`
- [ ] 若无外部订单号，不伪造 `external_order_id`
- [ ] timeout / unavailable / unsupported method / auth failure 都可显式区分

### 6.3 正式联调前最后自检

- [ ] 可以先单独访问 `/health`
- [ ] 可以先单独跑 mock-mode execute/result
- [ ] 可以解释 receipt / result 的状态含义
- [ ] 可以给出本次联调属于 mock 还是 live

L3 最小证据建议：

- 供本项目使用的 `base_url`
- 供本项目使用的 Bearer token
- 一份最新 `/health` 样例
- 一份最新 execute/result 样例

---

## 7. 推荐的 Windows 侧推进顺序

建议顺序如下：

### 阶段 A: 先做到 mock ready

- [ ] `XtItClient.exe` 运行不作为强依赖
- [ ] Windows bridge 先把 mock contract 跑通
- [ ] `/health` 返回 `provider_mode=mock`
- [ ] 本项目 formal sequence 先在 mock 模式下通过

### 阶段 B: 再做到 live-connect ready

- [ ] `XtItClient.exe` 连上模拟柜台
- [ ] Windows bridge 能调用真实 SDK
- [ ] `/health` 可切换到 `provider_mode=live`
- [ ] 本项目可以显式用 live 参数做探索性合同联调

### 阶段 C: 最后再谈更强 broker truth

- [ ] callback ingestion
- [ ] 完整 lifecycle mapping
- [ ] stronger production proof
- [ ] production-eligible 讨论

这些都不属于当前 Phase A service ready 的最低门槛。

---

## 8. 对本项目而言的“ready”一句话定义

对 `mystocks_spec` 来说，Windows 侧 `miniQMT` service ready 的最低标准不是：

- `XtItClient.exe` 在跑

而是：

- `D:\MyCode3\miniQMT` 中的 Windows bridge/service 已提供稳定的 `task/execute + task/result`
  HTTP contract
- 它能明确区分 transport receipt 与 broker-facing result
- 它能稳定回传 identity echo
- 它能被 `WSL 上的 Ubuntu 24.04.4 LTS` 侧的 formal sequence 成功验证

---

## 9. 联调命令参考

默认 mock / Phase A 合同联调：

```bash
python scripts/dev/run_windows_qmt_contract_formal_sequence.py \
  --base-url http://<windows-host>:8001 \
  --report-dir docs/reports/quality/windows-qmt-contract-acceptance
```

如果 Windows 侧已经进入 live provider mode，且你要做探索性合同联调：

```bash
python scripts/dev/run_windows_qmt_contract_formal_sequence.py \
  --base-url http://<windows-host>:8001 \
  --report-dir docs/reports/quality/windows-qmt-contract-acceptance \
  --expected-provider-mode live \
  --allow-non-mock-provider-mode
```
