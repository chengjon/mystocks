# Quant Trading Guide Family

> **导航说明**:
> 本文件是 `docs/guides/quant-trading/` 的 transition index，不是当前量化交易主线、仓库共享规则或当前实施状态的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)；若涉及当前代码实现边界，再结合根目录 `AGENTS.md` 与实际代码核对。

## Current Entry Order

这一 family 当前角色是 `supporting`，用于量化交易专题方案、阶段总结和历史实现参考，不承担仓库级 trunk。推荐阅读顺序：

1. [`algorithm_system_usage_guide.md`](./algorithm_system_usage_guide.md)
2. [`risk_management_system_plan.md`](./risk_management_system_plan.md)
3. 再按需进入 phase 完成报告与历史实现计划

## Active Supporting Guides

- [`algorithm_system_usage_guide.md`](./algorithm_system_usage_guide.md)
  - 量化交易算法系统 Phase 1-3 的整体实现说明
- [`risk_management_system_plan.md`](./risk_management_system_plan.md)
  - 轻量化风险管理系统架构方案与历史规划背景
- [`broker-execution-truth-registry.md`](./broker-execution-truth-registry.md)
  - broker-facing 执行与生命周期摄取路径的当前治理真相源
- [`windows-qmt-agent-live-contract-requirements-review.md`](./windows-qmt-agent-live-contract-requirements-review.md)
  - 面向本项目的 Windows `qmt` agent / live contract 对接审核稿，聚焦字段、状态、失败语义与升级边界
- [`windows-qmt-agent-contract-acceptance-guide.md`](./windows-qmt-agent-contract-acceptance-guide.md)
  - 从 `WSL 上的 Ubuntu 24.04.4 LTS` 侧运行的本地 acceptance harness 与 formal sequence，用于 mock-mode Windows `qmt` service 的合同联调、baseline compare、summary 和 fail-closed 验收
- [`windows-qmt-service-ready-checklist.md`](./windows-qmt-service-ready-checklist.md)
  - 面向 Windows 侧 `miniQMT` bridge/service 的 readiness 分级与打勾清单，明确区分 `XtItClient.exe` 已运行 与 Windows HTTP service 已 ready
- [`miniqmt-project-alignment-questionnaire.md`](./miniqmt-project-alignment-questionnaire.md)
  - 发给独立 Windows `miniQMT` 项目的跨项目对齐问卷，明确接口边界、必答字段与 reply template
- [`miniqmt-project-feedback-response.md`](./miniqmt-project-feedback-response.md)
  - 对 miniQMT 项目开发文档与待确认事项的审核反馈，给出本项目答复与新增要求

## Retained Historical References

- [`advanced_algorithms_usage_guide.md`](./advanced_algorithms_usage_guide.md)
  - Phase 4 高级算法完成报告
- [`neural_algorithms_usage_guide.md`](./neural_algorithms_usage_guide.md)
  - Phase 5 神经网络算法完成报告
- [`quantitative_trading_implementation.md`](./quantitative_trading_implementation.md)
  - 量化交易算法实现计划

## Retention Rule

- 该 family 当前保留为 `supporting`，不升级为新的 canonical docs trunk
- 根导航只暴露少量总览入口，阶段完成报告和历史实现计划统一通过本 index 进入
- broker execution truth、reconciliation boundary、以及相关 canonical-path 盘点可通过 `broker-execution-truth-registry.md` 进入
- Windows `qmt` agent 与 live contract 的审核要求统一通过 `windows-qmt-agent-live-contract-requirements-review.md` 进入
- Windows `qmt` service 的本地合同联调与 mock-mode acceptance，统一通过 `windows-qmt-agent-contract-acceptance-guide.md` 进入
- Windows 侧 `miniQMT` bridge/service 是否已达到可联调门槛，可先用 `windows-qmt-service-ready-checklist.md` 自检
- `miniQMT` v1 kernel 的第一次正式 Phase A readiness 联调，默认也通过同一 guide 中的 formal sequence 入口进入
- 与独立 Windows `miniQMT` 项目的跨仓接口问题，统一通过 `miniqmt-project-alignment-questionnaire.md` 发起与回收
- 对 miniQMT 项目开发文档和问题清单的正式审核反馈，统一通过 `miniqmt-project-feedback-response.md` 回传
- 若后续历史 phase 文档入链继续下降，再按 bounded batch 单独评估 archive/delete
