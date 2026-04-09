# 任务卡样例 05（对应 3.1 TTL 到期清理）

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


## 1) 基本信息
- 任务标题：执行 TTL 到期项清理与续期决策
- 任务编号：TD-RW1-CONTROL-TTL-01
- 所属阶段：Stage C (3.1)
- 优先级：P1
- 负责人（R）：模块负责人
- 审批人（A）：Tech Lead
- 协作者（C）：QA/效能
- 知会对象（I）：项目负责人
- 计划开始/截止：每周固定窗口

## 2) 背景与目标
- 背景问题：到期 suppressions/skip-xfail 若不清理会反复累积。
- 目标结果：TTL 到期清理率 100%。
- 不做范围：不处理未到期项。

## 3) 执行项
- [ ] 拉取 TTL 到期报告并确认影响范围。
- [ ] 对每条到期项执行“清理 or 续期（双签）”。
- [ ] 回填周报并关闭对应 issue。

## 4) 验收标准（DoD）
- 功能/行为验收：到期项清理完成或合法续期。
- 质量门验收：到期未处理项 = 0。
- 基线/实测口径记录：
  - 基线来源：`reports/analysis/tech-debt-baseline.json`
  - 当前实测：`reports/analysis/tech-debt-current.json`
  - 漂移结论：`reports/analysis/tech-debt-baseline-drift-report.json`
- 证据命令：
  - `python scripts/dev/quality_gate/collect_tech_debt_baseline.py --output reports/analysis/tech-debt-current.json`
  - `python scripts/dev/quality_gate/tech_debt_governance_gate.py ttl-gate --input reports/analysis/tech-debt-current.json`
  - `python scripts/dev/quality_gate/tech_debt_governance_gate.py baseline-drift-report --baseline reports/analysis/tech-debt-baseline.json --current reports/analysis/tech-debt-current.json --output reports/analysis/tech-debt-baseline-drift-report.json --only-drifted`
  - `python scripts/dev/quality_gate/tech_debt_governance_gate.py weekly-report --baseline reports/analysis/tech-debt-baseline.json --current reports/analysis/tech-debt-current.json --output reports/analysis/tech-debt-weekly-report.md`

## 5) 风险与应对
- 主要风险：误续期导致债务延期。
- 触发条件：连续两周同一项续期。
- 应对方案：强制复盘并要求拆分修复任务。
- 回滚条件：TTL 机制导致大面积阻塞。

## 6) 依赖与阻塞
- 前置依赖：current snapshot 可用。
- 外部阻塞：无。
- 解除阻塞负责人：模块负责人。

## 7) 例外与审批
- 是否申请 debt-exception：按需
- 续期必须满足双签并更新 TTL。

## 8) 复盘记录
- 实际完成时间：待补
- 偏差说明：待补
- 复盘结论：待补
