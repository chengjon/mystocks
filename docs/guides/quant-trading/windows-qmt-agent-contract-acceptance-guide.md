# Windows qmt Contract Acceptance Guide

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。
> 日期：2026-04-29
> 状态：活跃
> 适用范围：`WSL 上的 Ubuntu 24.04.4 LTS` 对独立 Windows `miniQMT` / Windows `qmt` service 的本地联调验收

## 1. 目的

本文档说明如何从 `WSL 上的 Ubuntu 24.04.4 LTS` 侧运行本仓库自带的 Windows `qmt`
contract acceptance harness。

这条脚手架的目标很窄：

- 验证远端 `/health` disclosure
- 验证 `Authorization: Bearer <TRADING_QMT_BRIDGE_TOKEN>` 和
  `X-Bridge-Contract-Version` 所对应的本地期望
- 通过仓库内既有的 `MultiSourceBridgeAdapter` 与 `MiniQMTLiveBridgeClient`
  跑一次 `qmt/submit_order -> task_id -> result` 合同 smoke

它**不**等于 production-ready 的真实交易验收。

## 2. 安全边界

默认情况下，这条 harness 只允许对 **显式宣告 `provider_mode=mock`** 的 Windows `qmt`
service 跑全链路 smoke。

原因是：

- 当前本仓库还没有被批准的真实 live provider acceptance path
- 本地 acceptance harness 不能把“合同联调”误变成“真实下单探测”

因此：

- 若 `/health` 返回的 `provider_mode` 不是 `mock`
- 且你没有显式传 `--allow-non-mock-provider-mode`

脚手架会在 execute 前 **fail closed** 并输出机器可读的失败摘要。

## 3. 运行方式

最小运行方式：

```bash
export TRADING_QMT_BRIDGE_TOKEN="your-bridge-token"
python scripts/dev/verify_windows_qmt_agent_contract.py \
  --base-url http://<windows-host>:8001
```

可选参数：

```bash
python scripts/dev/verify_windows_qmt_agent_contract.py \
  --base-url http://<windows-host>:8001 \
  --contract-version 1 \
  --expected-provider-mode mock \
  --expected-source-name qmt/windows_reference_service \
  --expected-account-scope wsl-ubuntu-phase-a-acceptance \
  --mock-outcome acknowledgement \
  --summary-output docs/reports/quality/windows-qmt-contract-acceptance/latest.json
```

也可以通过环境变量提供 base URL：

```bash
export TRADING_QMT_BRIDGE_BASE_URL="http://<windows-host>:8001"
export TRADING_QMT_BRIDGE_TOKEN="your-bridge-token"
python scripts/dev/verify_windows_qmt_agent_contract.py
```

## 4. 成功判定

成功时，脚手架会输出 JSON summary，并满足：

- `ok=true`
- `stage=completed`
- `/health` 中的 `bridge_auth_configured=true`
- `/health` 中的 `bridge_contract_version` 与本地期望一致
- `/health` 中的 `provider_mode=mock`，或经过显式 override
- normalized receipt 至少通过：
  - `task_id`
  - `receipt_timestamp`
  - `source_name`
  - `bridge_contract_version`
- normalized result 至少通过：
  - `occurred_at`
  - `source_name`
  - `account_scope`
  - `event_id`
  - `bridge_contract_version`
  - `broker_event_type`

若传入 `--summary-output <path>`，同一份 summary 也会落盘为 JSON artifact，便于后续联调审核、回传与归档。

## 5. 失败分层

当前失败会分成这些阶段：

- `configuration_invalid`
- `health_probe_failed`
- `blocked_before_execute`
- `receipt_validation_failed`
- `result_validation_failed`

其中：

- `blocked_before_execute` 代表本地 safety gate 主动阻止了 execute smoke
- 这通常是好事，说明 harness 没把不安全的对端直接当成可跑路径

## 6. 当前推荐用法

当前更推荐把它用于两类场景：

1. 对独立 Windows `miniQMT` 项目交付的 mock-mode service 做 Phase A 合同联调
2. 在本仓库内对 repo-owned Windows `qmt` reference service 做本地回归确认

当前**不推荐**把它当作：

- 真实 live trading proof
- production readiness verdict
- Tongdaxin 自动补路验收

## 7. 相关入口

- [Broker Execution Truth Registry](./broker-execution-truth-registry.md)
- [Windows qmt Agent / Live Contract 审核稿](./windows-qmt-agent-live-contract-requirements-review.md)
- [miniQMT 项目对齐问卷](./miniqmt-project-alignment-questionnaire.md)
- [miniQMT 项目审核反馈](./miniqmt-project-feedback-response.md)
