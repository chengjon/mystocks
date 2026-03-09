# 任务卡样例 04（对应 1.4 双签例外审计）

## 1) 基本信息
- 任务标题：执行 debt-exception 双签合规审计（周度）
- 任务编号：TD-RW1-CONTROL-EXC-01
- 所属阶段：Stage C / Rollout
- 优先级：P1
- 负责人（R）：QA/效能负责人
- 审批人（A）：Tech Lead
- 协作者（C）：模块负责人
- 知会对象（I）：项目负责人
- 计划开始/截止：每周五

## 2) 背景与目标
- 背景问题：例外机制已上线，需防止“无审批豁免”。
- 目标结果：双签合规率 >= 95%，并输出审计记录。
- 不做范围：不评估业务逻辑正确性。

## 3) 执行项
- [ ] 抽样审查本周 debt-exception PR。
- [ ] 核验 owner/issue/ttl/reason/remediation 完整性。
- [ ] 统计合规率并输出审计结论。

## 4) 验收标准（DoD）
- 功能/行为验收：周审计报告产出。
- 质量门验收：低于阈值触发整改任务。
- 证据命令：
  - `grep -RIn "debt-exception-tech-lead-approved" .github/workflows`
  - `cat reports/analysis/tech-debt-weekly-report.md`

## 5) 风险与应对
- 主要风险：审计口径不一致。
- 触发条件：同一 PR 结论分歧。
- 应对方案：按模板字段逐项判定。
- 回滚条件：审计机制不可重复执行。

## 6) 依赖与阻塞
- 前置依赖：例外模板与 workflow 已发布。
- 外部阻塞：PR 数据可见性。
- 解除阻塞负责人：QA/效能负责人。

## 7) 例外与审批
- 是否申请 debt-exception：否（本卡是审计卡）

## 8) 复盘记录
- 实际完成时间：待补
- 偏差说明：待补
- 复盘结论：待补
