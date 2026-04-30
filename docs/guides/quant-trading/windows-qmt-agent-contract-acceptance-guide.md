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
  --summary-output docs/reports/quality/windows-qmt-contract-acceptance/manual.json \
  --compare-with docs/reports/quality/windows-qmt-contract-acceptance/latest.json \
  --comparison-markdown-output docs/reports/quality/windows-qmt-contract-acceptance/comparison-summary.md
```

也可以通过环境变量提供 base URL：

```bash
export TRADING_QMT_BRIDGE_BASE_URL="http://<windows-host>:8001"
export TRADING_QMT_BRIDGE_TOKEN="your-bridge-token"
python scripts/dev/verify_windows_qmt_agent_contract.py
```

若希望采用仓库内标准报告目录结构，更推荐：

```bash
python scripts/dev/verify_windows_qmt_agent_contract.py \
  --base-url http://<windows-host>:8001 \
  --report-dir docs/reports/quality/windows-qmt-contract-acceptance
```

这会同时生成：

- 一个时间戳报告：`YYYYMMDDTHHMMSSZ-windows-qmt-contract-acceptance.json`
- 一个覆盖式指针：`latest.json`

## 4. 成功判定

成功时，脚手架会输出 JSON summary，并满足：

- `ok=true`
- `stage=completed`
- `summary_schema_version=1`
- `runtime_environment=wsl-ubuntu-24.04.4-lts`
- `generated_at` 为 UTC 时间戳
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

若传入 `--summary-output <path>`，同一份 summary 会落盘为指定 JSON artifact，且 artifact 本身也会带 `artifacts` 索引字段。

若传入 `--report-dir <dir>`，脚手架还会在标准报告目录下同时生成：

- 一份时间戳历史报告
- 一份 `latest.json`

这样后续联调审核、回传与归档就可以稳定使用同一目录。

若同时传入 `--report-dir <dir>` 与 `--compare-with <path>`，即使不额外指定
`--comparison-markdown-output`，脚手架也会自动生成标准命名的 comparison markdown：

- 一份时间戳报告：`YYYYMMDDTHHMMSSZ-windows-qmt-contract-comparison.md`
- 一份覆盖式指针：`latest-comparison.md`

若传入 `--compare-with <path>`，脚手架会把本次结果与一份既有 summary JSON 的稳定 contract 投影做比对，忽略 `task_id`、`event_id`、`generated_at` 这类天然会漂移的字段。

若还传入 `--comparison-markdown-output <path>`，脚手架会额外生成一份人类可读的 markdown 摘要，便于直接回传给 Windows `miniQMT` 项目或附到联调记录里。

当前比对关注的仍是 contract 级稳定字段，例如：

- `health.provider_mode`
- `health.bridge_contract_version`
- `receipt.contract_state`
- `result.source_name`
- `result.account_scope`
- `result.bridge_contract_version`
- `result.broker_event_type`

若比对发现 contract drift，脚手架会保持当前 run 的 `ok=true/false` 原语义不变，但会额外写入 `comparison` 段，并以退出码 `3` 返回。

## 5. 冻结 Baseline

当你已经审核过一份 `latest.json`，并希望把它作为后续 contract drift compare 的基准，可以直接冻结成标准 baseline：

```bash
python scripts/dev/freeze_windows_qmt_acceptance_baseline.py \
  --report-dir docs/reports/quality/windows-qmt-contract-acceptance
```

默认情况下，这条脚本会读取：

- `docs/reports/quality/windows-qmt-contract-acceptance/latest.json`

并生成：

- `docs/reports/quality/windows-qmt-contract-acceptance/baselines/YYYYMMDDTHHMMSSZ-windows-qmt-contract-baseline.json`
- `docs/reports/quality/windows-qmt-contract-acceptance/baselines/latest-baseline.json`

只有当 source summary 满足 `ok=true` 且 `stage=completed` 时，baseline freeze 才会通过；否则脚本会拒绝生成 baseline。

后续对比时，更推荐直接使用这个固定路径：

```bash
python scripts/dev/verify_windows_qmt_agent_contract.py \
  --base-url http://<windows-host>:8001 \
  --report-dir docs/reports/quality/windows-qmt-contract-acceptance \
  --compare-with docs/reports/quality/windows-qmt-contract-acceptance/baselines/latest-baseline.json
```

## 6. 只读状态摘要

若你已经跑过 acceptance harness，不想重复触发 `/health -> execute -> result` smoke，
可以直接读取标准报告目录中的 `latest.json` 和可选 `latest-comparison.md`：

```bash
python scripts/dev/summarize_windows_qmt_acceptance_reports.py \
  --report-dir docs/reports/quality/windows-qmt-contract-acceptance
```

若希望拿到机器可读摘要：

```bash
python scripts/dev/summarize_windows_qmt_acceptance_reports.py \
  --report-dir docs/reports/quality/windows-qmt-contract-acceptance \
  --json
```

这条只读脚本不会重新访问 Windows `qmt` service；它只基于现有 artifact 给出当前推荐状态。

当前状态标签与推荐退出码是：

- `acceptance_passed_no_baseline` -> `0`
- `acceptance_passed_with_baseline_match` -> `0`
- `acceptance_failed` -> `1`
- `report_missing` -> `2`
- `contract_drift_detected` -> `3`

若 `latest.json` 中存在 comparison 信息，文本摘要还会附带：

- `mismatch_count`
- `baseline_path`
- `comparison_markdown_path`

这样你可以先用只读摘要判断“是否需要回看详细 JSON / markdown”，而不必每次都重新跑联调。

## 7. 失败分层

当前失败会分成这些阶段：

- `configuration_invalid`
- `health_probe_failed`
- `blocked_before_execute`
- `receipt_validation_failed`
- `result_validation_failed`

其中：

- `blocked_before_execute` 代表本地 safety gate 主动阻止了 execute smoke
- 这通常是好事，说明 harness 没把不安全的对端直接当成可跑路径

退出码约定：

- `0`：acceptance 通过，且未发生 comparison drift
- `1`：acceptance 本身失败
- `2`：本地参数 / 配置无效
- `3`：acceptance 通过，但 `--compare-with` 检测到 contract drift

## 8. 当前推荐用法

当前更推荐把它用于两类场景：

1. 对独立 Windows `miniQMT` 项目交付的 mock-mode service 做 Phase A 合同联调
2. 在本仓库内对 repo-owned Windows `qmt` reference service 做本地回归确认

当前**不推荐**把它当作：

- 真实 live trading proof
- production readiness verdict
- Tongdaxin 自动补路验收

## 9. 相关入口

- [Broker Execution Truth Registry](./broker-execution-truth-registry.md)
- [Windows qmt Agent / Live Contract 审核稿](./windows-qmt-agent-live-contract-requirements-review.md)
- [miniQMT 项目对齐问卷](./miniqmt-project-alignment-questionnaire.md)
- [miniQMT 项目审核反馈](./miniqmt-project-feedback-response.md)
