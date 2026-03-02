## 1. Stage A - Stop Bleeding（质量信号对齐）

- [x] 1.1 统一前端构建与类型检查门禁：禁止主链路以 `|| true` 放行 `vue-tsc` 失败
- [x] 1.2 建立技术债基线文件（type errors / suppressions / skip-xfail）并接入 CI 对比
- [x] 1.2.1 基线 SoT 迁移：将前端类型错误基线来源从 AGENTS 固定值迁移到 `reports/analysis/tech-debt-baseline.json` 并同步 CI 读取
- [x] 1.3 新增债务阻断：新增 `@ts-ignore/@ts-expect-error/as any`、裸 TODO/FIXME、新增长期 skip/xfail 直接失败（无豁免）
- [x] 1.4 建立例外模板（owner/issue/ttl/reason/remediation plan）与双签审批流程

## 2. Stage B - Risk Reduction（高风险存量清偿）

- [x] 2.1 前端关键路径清理第一批：交易链路相关组件/composable 的 suppressions 减量
- [x] 2.2 后端关键路径清理第一批：placeholder/mock/todo 占位替换为可执行逻辑或受控开关
- [x] 2.3 测试有效性治理第一批：替换 `assert True` 占位断言，收敛无期限 skip/xfail
- [x] 2.4 大文件热点治理：按“高频修改+高故障”优先拆分 Top N

## 3. Stage C - Institutionalization（治理机制硬化）

- [x] 3.1 TTL 到期自动失效：过期 suppressions/例外/skip-xfail 在 CI 中失败
- [x] 3.2 周报模板落地：新增债务、消化债务、存量债务、过期项、风险热点
- [x] 3.3 KPI 门禁化：no-new-debt、基线不增、例外合规率、到期清理率
- [x] 3.4 治理回顾机制：每迭代复盘并只允许“基线下降”更新

## 4. Verification & Rollout

- [ ] 4.1 在试点模块（前端交易链路 + 后端交易 API）运行两周并记录数据
  - 已完成试点方案文档：`docs/reports/technical-debt-stage4-4.1-pilot-plan-2026-03-01.md`
  - 已完成任务卡样例：`docs/reports/technical-debt-task-card-sample-01-pilot-execution-2026-03-01.md`
  - 已完成 Week1 真实数据采集与门禁执行：
    - `reports/analysis/tech-debt-current-real-week1.json`
    - `reports/analysis/ttl-gate-report-week1-real.json`
    - `reports/analysis/tech-debt-kpi-report-week1-real.json`
    - `reports/analysis/tech-debt-weekly-report-week1-real.md`
  - 已完成 Week2 Day1 真实数据采集与门禁执行：
    - `reports/analysis/tech-debt-current-real-week2-day1.json`
    - `reports/analysis/ttl-gate-report-week2-day1-real.json`
    - `reports/analysis/tech-debt-kpi-report-week2-day1-real.json`
    - `reports/analysis/tech-debt-weekly-report-week2-day1-real.md`
  - 已完成 Week2 Day2 真实数据采集与门禁执行：
    - `reports/analysis/tech-debt-current-real-week2-day2.json`
    - `reports/analysis/ttl-gate-report-week2-day2-real.json`
    - `reports/analysis/tech-debt-kpi-report-week2-day2-real.json`
    - `reports/analysis/tech-debt-weekly-report-week2-day2-real.md`
  - 已完成 Week2 Day3 真实数据采集与门禁执行：
    - `reports/analysis/tech-debt-current-real-week2-day3.json`
    - `reports/analysis/ttl-gate-report-week2-day3-real.json`
    - `reports/analysis/tech-debt-kpi-report-week2-day3-real.json`
    - `reports/analysis/tech-debt-weekly-report-week2-day3-real.md`
  - 已完成 Week2 Day4 真实数据采集与门禁执行：
    - `reports/analysis/tech-debt-current-real-week2-day4.json`
    - `reports/analysis/ttl-gate-report-week2-day4-real.json`
    - `reports/analysis/tech-debt-kpi-report-week2-day4-real.json`
    - `reports/analysis/tech-debt-weekly-report-week2-day4-real.md`
  - 已完成 Week2 Day5 真实数据采集与门禁执行：
    - `reports/analysis/tech-debt-current-real-week2-day5.json`
    - `reports/analysis/ttl-gate-report-week2-day5-real.json`
    - `reports/analysis/tech-debt-kpi-report-week2-day5-real.json`
    - `reports/analysis/tech-debt-weekly-report-week2-day5-real.md`
  - 待完成：误伤率归因复盘 + 4.2 评审输入
- [x] 4.2 出具首轮治理报告，确认门禁误伤率与交付影响
  - 已完成报告模板：`docs/reports/technical-debt-stage4-4.2-governance-report-template-2026-03-01.md`
  - 已完成评审版 v1：`docs/reports/technical-debt-stage4-4.2-governance-review-v1-2026-03-01.md`
  - 已完成第2周复审骨架：`docs/reports/technical-debt-stage4-4.2-week2-review-skeleton-2026-03-08.md`
  - 已完成任务卡样例：`docs/reports/technical-debt-task-card-sample-02-governance-review-2026-03-01.md`
  - 已完成：基于 4.1 两周真实数据填报并评审
    - 门禁效果复审：no-new-debt (1次触发，96.4%误伤率)、baseline-non-increase (1次触发，已恢复稳定)、debt-exception 双签 (3.59%合规率)
    - 交付影响复审：0 次返工、无阻塞性事故、TTL 清理率 100%
    - 误伤样本复盘：Top 3 文件共 95 个违规（缺失元数据）
- [ ] 4.3 通过评审后分阶段扩展到全仓
  - 已完成推广计划文档：`docs/reports/technical-debt-stage4-4.3-rollout-plan-2026-03-01.md`
  - 已完成治理执行主计划：`docs/reports/technical-debt-governance-master-plan-v2-2026-03-01.md`
  - 已完成防重复机制清单：`docs/reports/technical-debt-recurrence-prevention-controls-2026-03-01.md`
  - 已完成任务卡样例：
    - `docs/reports/technical-debt-task-card-sample-03-rollout-phase-a-2026-03-01.md`
    - `docs/reports/technical-debt-task-card-sample-04-exception-audit-2026-03-01.md`
    - `docs/reports/technical-debt-task-card-sample-05-ttl-cleanup-2026-03-01.md`
  - 待完成：4.2 评审通过后按 Phase A/B/C 执行
