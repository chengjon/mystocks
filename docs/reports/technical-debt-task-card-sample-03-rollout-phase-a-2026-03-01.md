# 任务卡样例 03（对应 4.3 全仓推广 Phase A）

## 1) 基本信息
- 任务标题：执行 4.3 Phase A（核心模块）推广
- 任务编号：TD-RW1-ROLL-4.3-01
- 所属阶段：Rollout (4.3)
- 优先级：P1
- 负责人（R）：Tech Lead
- 审批人（A）：项目负责人
- 协作者（C）：前端负责人、后端负责人、QA/效能
- 知会对象（I）：全体开发
- 计划开始/截止：评审通过后第1周

## 2) 背景与目标
- 背景问题：需要在可控范围放量验证治理机制。
- 目标结果：Phase A 模块接入同一套门禁并稳定运行。
- 不做范围：不覆盖遗留低优先级模块。

## 3) 执行项
- [ ] 选择 Phase A 模块清单并公告。
- [ ] 接入 no-new-debt、baseline-non-increase、exception 双签规则。
- [ ] 运行一周并提交阶段复盘。

## 4) 验收标准（DoD）
- 功能/行为验收：Phase A 模块全量接入。
- 质量门验收：误伤率、CI 增幅、双签合规率达阈值。
- 证据命令：
  - `openspec validate refactor-technical-debt-remediation-wave1 --strict`
  - `python scripts/dev/quality_gate/collect_tech_debt_baseline.py`

## 5) 风险与应对
- 主要风险：放量后 CI 波动。
- 触发条件：CI 平均耗时增幅 > 15%。
- 应对方案：降级回试点范围。
- 回滚条件：连续 2 天门禁阻塞核心交付。

## 6) 依赖与阻塞
- 前置依赖：4.2 评审通过。
- 外部阻塞：无。
- 解除阻塞负责人：Tech Lead。

## 7) 例外与审批
- 是否申请 debt-exception：按需
- 双签审批字段必须在 PR body 中完整填写。

## 8) 复盘记录
- 实际完成时间：待补
- 偏差说明：待补
- 复盘结论：待补
