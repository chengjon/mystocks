# Stage 4.1 两周试点方案（技术债治理）

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


## 目标
在有限范围内验证治理门禁对交付效率与质量的影响，重点评估：
1. no-new-debt 门禁误伤率
2. 基线对比门禁稳定性
3. 例外（debt-exception）双签流程可执行性

## 试点范围
- 前端：交易主链路相关目录
  - `web/frontend/src/views/artdeco-pages/`
  - `web/frontend/src/composables/`
  - `web/frontend/src/api/adapters/`
- 后端：交易 API 相关目录
  - `web/backend/app/api/trade/`

## 试点周期
- 周期：2 周（建议 10 个工作日）
- 起止：由批准后首个工作日开始计时

## 试点门禁
1. TypeScript 基线门禁（以 `reports/analysis/tech-debt-baseline.json` 为准）
2. no-new-debt 门禁
   - 阻断新增 `@ts-ignore/@ts-expect-error/@ts-nocheck/as any`
   - 阻断裸 TODO/FIXME/HACK
3. debt-exception 双签门禁
   - PR body 必须包含：
     - `debt-exception-tech-lead-approved: yes`
     - `debt-exception-module-owner-approved: yes`

## 观测指标
- 质量类
  - `frontend_type_errors`
  - `frontend_suppressions_count`
  - `backend_todo_count`
  - `backend_placeholder_count`
  - `test_placeholder_assert_count`
- 效率类
  - PR 平均 lead time
  - CI 平均耗时
  - 因门禁失败导致的重试次数
- 稳定性类
  - 门禁误伤率（误伤/总阻断）
  - 例外审批响应时长

## 每周产出
- `reports/analysis/tech-debt-weekly-report.md`（自动）
- `reports/analysis/tech-debt-baseline-drift-report.json`（按当前治理标准补充）
- 审核记录（人工补充）
  - 误伤案例与修复结论
  - 例外审批记录（issue/owner/ttl/reason/remediation）

## 退出条件（4.1 完成标准）
满足以下全部条件后，判定 4.1 完成：
1. 连续 2 周运行门禁
2. 至少 2 轮周报产出
3. 完成误伤率统计与样例复盘
4. 形成是否进入 4.2 的评审结论

## 风险与应对
- 风险：历史存量波动导致“假回归”
  - 应对：固定基线文件版本，禁止试点期间随意更新
- 风险：例外审批响应慢影响提测
  - 应对：设定审批 SLA（工作日 24h 内）

## Week1 真实数据执行快照（2026-03-01）

> 补充口径说明：本节保留历史执行快照；若按当前治理标准复跑或复盘，需要在 `collect_tech_debt_baseline.py` 之后同时生成 `baseline-drift-report`，并明确区分 `gated drift` 与 `observed drift`，不得仅依据周报或 KPI 报告下结论。

### 执行模式确认
- `.env` 静态配置：`USE_MOCK_DATA=false`，`DATA_SOURCE_MODE=real`。
- 模式解析实测：若 `REAL_DATA_AVAILABLE` 缺失，工厂解析为 `hybrid`。
- Week1 试点命令采用显式环境覆盖：
  - `USE_MOCK_DATA=false REAL_DATA_AVAILABLE=true DATA_SOURCE_MODE=real`

### 已执行命令（证据）
- `python scripts/dev/quality_gate/collect_tech_debt_baseline.py --output reports/analysis/tech-debt-current-real-week1.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py hotspot --output reports/analysis/large-file-hotspots-week1-real.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py ttl-gate --output reports/analysis/ttl-gate-report-week1-real.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py kpi-gate --baseline reports/analysis/tech-debt-baseline.json --current reports/analysis/tech-debt-current-real-week1.json --output reports/analysis/tech-debt-kpi-report-week1-real.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py weekly-report --baseline reports/analysis/tech-debt-baseline.json --current reports/analysis/tech-debt-current-real-week1.json --output reports/analysis/tech-debt-weekly-report-week1-real.md`

### Week1 输出摘要
- 产物已落盘：
  - `reports/analysis/tech-debt-current-real-week1.json`
  - `reports/analysis/large-file-hotspots-week1-real.json`
  - `reports/analysis/ttl-gate-report-week1-real.json`
  - `reports/analysis/tech-debt-kpi-report-week1-real.json`
  - `reports/analysis/tech-debt-weekly-report-week1-real.md`
- 门禁返回码：`BASELINE_EXIT=0 HOTSPOT_EXIT=0 TTL_EXIT=1 KPI_EXIT=1 WEEKLY_EXIT=0`
- 关键观测：
  - `frontend_type_errors=213`（高于当前冻结基线）
  - `ttl-gate` 存在大量历史标记缺少 owner/issue/ttl

### Week1 结论
- 已完成“真实数据模式下第1周采集与门禁执行”
- 4.1 仍未完成：需补齐第2周连续观测、误伤率归因与复盘后，进入 4.2 评审

## Week2 Day1 进展快照（2026-03-02）

### 已执行命令（REAL 模式）
- `python scripts/dev/quality_gate/collect_tech_debt_baseline.py --output reports/analysis/tech-debt-current-real-week2-day1.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py hotspot --output reports/analysis/large-file-hotspots-week2-day1-real.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py ttl-gate --output reports/analysis/ttl-gate-report-week2-day1-real.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py kpi-gate --baseline reports/analysis/tech-debt-baseline.json --current reports/analysis/tech-debt-current-real-week2-day1.json --output reports/analysis/tech-debt-kpi-report-week2-day1-real.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py weekly-report --baseline reports/analysis/tech-debt-baseline.json --current reports/analysis/tech-debt-current-real-week2-day1.json --output reports/analysis/tech-debt-weekly-report-week2-day1-real.md`

### 输出摘要
- 门禁返回码：`BASELINE_EXIT=0 HOTSPOT_EXIT=0 TTL_EXIT=1 KPI_EXIT=1 WEEKLY_EXIT=0`
- 指标与 Week1 持平：`frontend_type_errors=213`、`backend_todo_count=54`、`backend_placeholder_count=548`
- 当前风险未变：`frontend_type_errors` 高于冻结基线、TTL 历史元数据缺失仍待治理

## Week2 Day2 进展快照（2026-03-03）

### 已执行命令（REAL 模式）
- `python scripts/dev/quality_gate/collect_tech_debt_baseline.py --output reports/analysis/tech-debt-current-real-week2-day2.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py hotspot --output reports/analysis/large-file-hotspots-week2-day2-real.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py ttl-gate --output reports/analysis/ttl-gate-report-week2-day2-real.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py kpi-gate --baseline reports/analysis/tech-debt-baseline.json --current reports/analysis/tech-debt-current-real-week2-day2.json --output reports/analysis/tech-debt-kpi-report-week2-day2-real.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py weekly-report --baseline reports/analysis/tech-debt-baseline.json --current reports/analysis/tech-debt-current-real-week2-day2.json --output reports/analysis/tech-debt-weekly-report-week2-day2-real.md`

### 输出摘要
- 门禁返回码：`BASELINE_EXIT=0 HOTSPOT_EXIT=0 TTL_EXIT=1 KPI_EXIT=0 WEEKLY_EXIT=0`
- 关键改善：`frontend_type_errors` 从 213 降至 131，已低于冻结基线 190
- 保持持平：`frontend_suppressions_count=67`、`backend_todo_count=54`、`backend_placeholder_count=548`
- 当前风险：TTL gate 仍受历史 TODO 元数据缺失影响（owner/issue/ttl）

## Week2 Day3 进展快照（2026-03-04）

### 已执行命令（REAL 模式）
- `python scripts/dev/quality_gate/collect_tech_debt_baseline.py --output reports/analysis/tech-debt-current-real-week2-day3.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py hotspot --output reports/analysis/large-file-hotspots-week2-day3-real.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py ttl-gate --output reports/analysis/ttl-gate-report-week2-day3-real.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py kpi-gate --baseline reports/analysis/tech-debt-baseline.json --current reports/analysis/tech-debt-current-real-week2-day3.json --output reports/analysis/tech-debt-kpi-report-week2-day3-real.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py weekly-report --baseline reports/analysis/tech-debt-baseline.json --current reports/analysis/tech-debt-current-real-week2-day3.json --output reports/analysis/tech-debt-weekly-report-week2-day3-real.md`

### 输出摘要
- 门禁返回码：`BASELINE_EXIT=0 HOTSPOT_EXIT=0 TTL_EXIT=1 KPI_EXIT=0 WEEKLY_EXIT=0`
- 关键状态：`frontend_type_errors=131` 持续低于冻结基线 190（Day2~Day3 连续通过 KPI gate）
- 保持持平：`frontend_suppressions_count=67`、`backend_todo_count=54`、`backend_placeholder_count=548`
- 当前风险：TTL gate 仍受历史 TODO 元数据缺失影响（owner/issue/ttl）

## Week2 Day4 进展快照（2026-03-05）

### 已执行命令（REAL 模式）
- `python scripts/dev/quality_gate/collect_tech_debt_baseline.py --output reports/analysis/tech-debt-current-real-week2-day4.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py hotspot --output reports/analysis/large-file-hotspots-week2-day4-real.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py ttl-gate --output reports/analysis/ttl-gate-report-week2-day4-real.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py kpi-gate --baseline reports/analysis/tech-debt-baseline.json --current reports/analysis/tech-debt-current-real-week2-day4.json --output reports/analysis/tech-debt-kpi-report-week2-day4-real.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py weekly-report --baseline reports/analysis/tech-debt-baseline.json --current reports/analysis/tech-debt-current-real-week2-day4.json --output reports/analysis/tech-debt-weekly-report-week2-day4-real.md`

### 输出摘要
- 门禁返回码：`BASELINE_EXIT=0 HOTSPOT_EXIT=0 TTL_EXIT=1 KPI_EXIT=0 WEEKLY_EXIT=0`
- 关键状态：`frontend_type_errors=131` 持续低于冻结基线 190（Day2~Day4 连续通过 KPI gate）
- 保持持平：`frontend_suppressions_count=67`、`backend_todo_count=54`、`backend_placeholder_count=548`
- 当前风险：TTL gate 仍受历史 TODO 元数据缺失影响（owner/issue/ttl）

## Week2 Day5 进展快照（2026-03-06）

### 已执行命令（REAL 模式）
- `python scripts/dev/quality_gate/collect_tech_debt_baseline.py --output reports/analysis/tech-debt-current-real-week2-day5.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py hotspot --output reports/analysis/large-file-hotspots-week2-day5-real.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py ttl-gate --output reports/analysis/ttl-gate-report-week2-day5-real.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py kpi-gate --baseline reports/analysis/tech-debt-baseline.json --current reports/analysis/tech-debt-current-real-week2-day5.json --output reports/analysis/tech-debt-kpi-report-week2-day5-real.json`
- `python scripts/dev/quality_gate/tech_debt_governance_gate.py weekly-report --baseline reports/analysis/tech-debt-baseline.json --current reports/analysis/tech-debt-current-real-week2-day5.json --output reports/analysis/tech-debt-weekly-report-week2-day5-real.md`

### 输出摘要
- 门禁返回码：`BASELINE_EXIT=0 HOTSPOT_EXIT=0 TTL_EXIT=1 KPI_EXIT=0 WEEKLY_EXIT=0`
- 关键状态：`frontend_type_errors=131` 持续低于冻结基线 190（Day2~Day5 连续通过 KPI gate）
- 保持持平：`frontend_suppressions_count=67`、`backend_todo_count=54`、`backend_placeholder_count=548`
- 当前风险：TTL gate 仍受历史 TODO 元数据缺失影响（owner/issue/ttl）
