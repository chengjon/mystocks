# Governance Reports

> **补充规范说明**:
> 本文件是项目补充标准、执行细则或专题规范，不是仓库共享规则的唯一事实来源。
> 仓库级共享规则总入口仍以 `architecture/STANDARDS.md` 为准；执行流程、命令与协作约束再参考根目录 `AGENTS.md`。本文件用于补充某一专题的执行细则、约束或参考模板。
>
> 若本文件与 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 或当前已批准执行口径不一致，应优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 与当前实现；若无冲突，则按本文件的专题范围执行。


本目录用于保存治理任务、治理任务汇报和治理周报。

## Naming

- 任务文件：`YYYY-MM-DD-<topic>.TASK.md`
- 任务汇报：`YYYY-MM-DD-<topic>.TASK-REPORT.md`
- 周报：`YYYY-MM-DD-<topic>.WEEKLY.md` 或等价命名

## Templates

以下模板只用于生成或校验 `reports/governance/` 下的 Markdown 文件骨架，便于 Mongo 投影文件保持稳定格式；它们不是治理规则、任务状态或审计字段的真相源。

- 任务模板：`reports/governance/_TEMPLATE.TASK.md`
- 汇报模板：`reports/governance/_TEMPLATE.TASK-REPORT.md`
- 周报模板：`reports/governance/_TEMPLATE.WEEKLY-GOVERNANCE-REPORT.md`

## Mongo / Graphiti Truth Boundary

`reports/governance/*.TASK.md` 与 `reports/governance/*.TASK-REPORT.md` 仅用于承接 Mongo 导出 / 导入后的 Markdown 投影，不是治理规则或流程模板的唯一真相源。

- 任务状态、字段真相以 Mongo 为准
- 记忆与上下文沉淀以 Graphiti 为准
- 若需要新增治理规则、刷新流程、审计字段或口径说明，应优先落在：
  - `architecture/STANDARDS.md`
  - `docs/standards/technical-debt-governance-charter-v1.md`
  - `reports/governance/*.md` 专项治理说明
  - `reports/governance/_TEMPLATE.WEEKLY-GOVERNANCE-REPORT.md`

## Required Structural Debt Fields

当任务涉及以下任一情形时，必须按模板填写结构性技术债字段：

- 迁移收口
- 重复层 / 平行层治理
- 兼容层 / `shim` / re-export
- `*_new.py`、临时入口、实验入口
- `part1/part2/part3` 机械拆分
- `.bak` / `.backup` / 备份快照
- 清理 / 删除 / 归档
- 技术债指标、周报、基线更新

最低要求：

- 迁移类：`canonical_source`、`compatibility_surface`、`callers_or_consumers`、`verification_command`、`exit_condition`
- 清理类：`code_path_verdict`、`function_tree_verdict`、`removal_basis`、`keep_reason`
- 指标类：`measured`、`baseline`、`inferred`、`target`、`source_or_command`

## Asset Ledger Encoding

临时层 / 兼容层 / 备份文件类不要再在正文里平行发明另一套字段，统一落在 `Temporary / Compatibility Asset Ledger` 表中：

- `introduced_by` 必须写成 `issue_or_task=<...>; created_at=<...>`
- `exit_condition` 承载 `sunset_condition`
- `planned_removal_milestone` 单独成列；未知时写 `N/A`
- `target_removal_date` 填计划日期或 `N/A`
- `current_status` 使用 `active`、`planned-removal`、`retained`、`removed`

本目录下的 `*.TASK.md` / `*.TASK-REPORT.md` 若命中结构性技术债场景，会被 `python scripts/dev/quality_gate/governance_report_fields_guard.py --format json` 校验上述表头和关键字段格式。

## Source of Truth

规则正文与裁定标准不在本目录重复维护。

- 结构性技术债规则唯一事实来源：
  - `architecture/STANDARDS.md` 第“三、迁移收口与技术债治理规则”
- 门禁、基线、例外、周报执行细则：
  - `docs/standards/technical-debt-governance-charter-v1.md`

## Current Tech Debt Governance Baseline

2026Q1 技术债治理基线当前使用以下工件：

- `reports/governance/2026-04-10-tech-debt-governance-sot.md`
- `reports/governance/2026-04-10-tech-debt-spec-conflict-matrix.md`
- `reports/governance/2026-04-10-tech-debt-register.md`
- `reports/governance/2026-04-10-tech-debt-governance-execution.TASK.md`
- `reports/governance/2026-04-10-tech-debt-governance-execution.TASK-REPORT.md`

当前运行门禁 / 可观测性基线补充使用以下工件：

- `reports/analysis/runtime-observability-baseline.json`
- `scripts/run_runtime_observability_drift_gate.sh`
- `reports/analysis/api-performance-baseline.json`
- `reports/analysis/frontend-runtime-gate/<timestamp>/frontend-runtime-gate.json`
- `reports/analysis/api-monitoring-auth-gate/<timestamp>/monitoring-auth-performance-gate-graphiti-closeout.json`
- `reports/governance/2026-04-22-api-performance-baseline-governance.md`
- `scripts/dev/quality_gate/collect_frontend_runtime_gate.py`
- `scripts/dev/quality_gate/collect_api_performance_baseline.py`
- `scripts/dev/quality_gate/validate_api_performance_drift.py`
- `scripts/dev/quality_gate/collect_runtime_observability_baseline.py`
- `scripts/run_full_runtime_delivery_gate.sh`
- `scripts/run_tech_debt_weekly_report.sh`
- `.github/workflows/runtime-delivery-gate.yml`
- `.github/workflows/tech-debt-weekly-governance.yml`

当前 Graphiti gate closeout 补充工件：

- `reports/analysis/runtime-delivery-gate/<timestamp>/runtime-delivery-gate-graphiti-closeout.json`
- `reports/analysis/frontend-runtime-gate/<timestamp>/frontend-runtime-gate-graphiti-closeout.json`
- `reports/analysis/api-performance-gate/<timestamp>/api-performance-gate-graphiti-closeout.json`
- `reports/analysis/api-monitoring-auth-gate/<timestamp>/monitoring-auth-performance-gate-graphiti-closeout.json`
- `reports/analysis/docker-runtime-smoke/<timestamp>/docker-runtime-smoke-graphiti-closeout.json`
- `scripts/runtime/record_runtime_delivery_gate_closeout.py`
- `scripts/runtime/record_quality_gate_closeout.py`

推荐命令：

- 采集前端 PM2 runtime 机读工件：
  - `python scripts/dev/quality_gate/collect_frontend_runtime_gate.py --type-ceiling-log reports/analysis/frontend-runtime-gate/<timestamp>/type-ceiling.log --pm2-gate-log reports/analysis/frontend-runtime-gate/<timestamp>/pm2-gate.log --regression-log reports/analysis/frontend-runtime-gate/<timestamp>/regression.log --axe-log reports/analysis/frontend-runtime-gate/<timestamp>/axe.log --current-tech-debt-baseline reports/analysis/frontend-runtime-gate/<timestamp>/tech-debt-baseline.current.json --output reports/analysis/frontend-runtime-gate/<timestamp>/frontend-runtime-gate.json`

- 冻结 API 性能基线：
  - `python scripts/dev/quality_gate/collect_api_performance_baseline.py --benchmark-json reports/analysis/api-performance-gate/<timestamp>/benchmark.json --output reports/analysis/api-performance-baseline.json`
- 校验 API 性能漂移：
  - `python scripts/dev/quality_gate/validate_api_performance_drift.py --baseline reports/analysis/api-performance-baseline.json --current-benchmark-json reports/analysis/api-performance-gate/<timestamp>/benchmark.json`
- 完整运行门禁：
  - `bash scripts/run_full_runtime_delivery_gate.sh`
- 生成带 Graphiti closeout 引用的治理周报：
  - `bash scripts/run_tech_debt_weekly_report.sh`
  - 默认要求 closeout 全部有效；如只做观察性输出，可用 `TECH_DEBT_WEEKLY_REQUIRE_VALID_CLOSEOUTS=0`
  - 如需显式指定 closeout 工件，可设置：
    - `RUNTIME_GATE_CLOSEOUT_JSON`
    - `FRONTEND_GATE_CLOSEOUT_JSON`
    - `API_GATE_CLOSEOUT_JSON`
    - `DOCKER_GATE_CLOSEOUT_JSON`

## API Performance Baseline Refresh Audit Example

若本周发生 API 性能基线刷新或提议刷新，不要把新增字段当作 `TASK / TASK-REPORT` 模板真相扩展；应在治理说明、周报或 Mongo 对应记录中至少保留以下审计字段：

```md
### API Performance Baseline Refresh Audit

- source_benchmark_json: `reports/analysis/api-performance-gate/<timestamp>/benchmark.json`
- service_url: `http://localhost:8020`
- endpoint_set_source: `tests/performance/api_smoke_endpoints.json`
- concurrent_users: `<value>`
- iterations: `<value>`
- overall_p95_ms: `<value>`
- slowest_endpoint: `<method path> p95=<value>ms`
- refresh_reason: `<lower-baseline|freeze-again|rebaseline-with-exception>`
- verification_command: `python scripts/dev/quality_gate/validate_api_performance_drift.py --baseline reports/analysis/api-performance-baseline.json --current-benchmark-json reports/analysis/api-performance-gate/<timestamp>/benchmark.json`
- approval_or_issue: `<issue / approval / N/A>`
```

详细规则仍以 `reports/governance/2026-04-22-api-performance-baseline-governance.md` 为准。
