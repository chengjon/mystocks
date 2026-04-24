# WEEKLY GOVERNANCE REPORT

> **参考模板说明**:
> 本文件是模板、骨架或示例输入，不是当前共享规则、当前任务状态或当前实现结果的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md` 与对应主线模板/流程文档。
>
> 使用本模板时应结合当前任务上下文填写；模板中的占位内容、示例字段和默认值不得直接当作当前事实。


> Weekly governance template aligned with `docs/standards/technical-debt-governance-charter-v1.md`.

- Week Range: `<yyyy-mm-dd .. yyyy-mm-dd>`
- Report Owner: `<owner>`
- Generated At: `<timestamp>`

## 6.1 概览
- 本周新增债务数: `<count>`
- 本周消化债务数: `<count>`
- 当前存量债务数: `<count>`
- 过期未清理例外数: `<count>`

## 6.2 关键指标（KPI）

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| 新增 Type 错误数 | `<value>` | `<value>` | `N/A` | `<= 0` | `<command/file>` |
| 新增 suppression 数 | `<value>` | `<value>` | `N/A` | `<= 0` | `<command/file>` |
| 新增 skip/xfail 数 | `<value>` | `<value>` | `N/A` | `<= 0` | `<command/file>` |
| 例外合规率 | `<value>` | `<value or N/A>` | `N/A` | `100%` | `<source>` |
| 到期清理率 | `<value>` | `<value or N/A>` | `N/A` | `>= 90%` | `<source>` |
| PM2 runtime overall gate status | `<value>` | `<value>` | `N/A` | `PASS` | `reports/analysis/runtime-observability-baseline.json` |
| PM2 online services | `<value>` | `mystocks-backend,mystocks-frontend` | `N/A` | `mystocks-backend,mystocks-frontend` | `reports/analysis/frontend-runtime-gate/<timestamp>/frontend-runtime-gate.json` |
| Structural syntax / PM2 navigation gate | `<value>` | `<value>` | `N/A` | `all passed` | `reports/analysis/frontend-runtime-gate/<timestamp>/frontend-runtime-gate.json` |
| Regression E2E actual result | `<value>` | `<value>` | `N/A` | `failed=0` | `reports/analysis/frontend-runtime-gate/<timestamp>/frontend-runtime-gate.json` |
| Regression pytest actual result | `<value>` | `<value>` | `N/A` | `failed=0` | `reports/analysis/frontend-runtime-gate/<timestamp>/frontend-runtime-gate.json` |
| Accessibility smoke actual result | `<value>` | `<value>` | `N/A` | `failed=0` | `reports/analysis/frontend-runtime-gate/<timestamp>/frontend-runtime-gate.json` |
| Anonymous API overall P95 (ms) | `<value>` | `<value>` | `N/A` | `<= 300` | `reports/analysis/runtime-observability-baseline.json` |
| API performance drift gate pass | `<value>` | `PASS` | `N/A` | `PASS` | `reports/analysis/api-performance-baseline.json` + `scripts/dev/quality_gate/validate_api_performance_drift.py` |
| API performance drift violations | `<value>` | `0` | `N/A` | `0` | `reports/analysis/api-performance-baseline.json` + `scripts/dev/quality_gate/validate_api_performance_drift.py` |
| Monitoring auth closeout coverage | `<valid>/<expected>` | `1/1` | `N/A` | `1/1` | `reports/analysis/api-monitoring-auth-gate/<timestamp>/monitoring-auth-performance-gate-graphiti-closeout.json` |
| Monitoring auth closeout validity gate | `<value>` | `PASS` | `N/A` | `PASS` | `bash scripts/run_monitoring_auth_performance_baseline.sh` |
| Monitoring auth `alert-rules` P95 (ms) | `<value>` | `<value>` | `N/A` | `<= 300` | `reports/analysis/runtime-observability-baseline.json` |
| Docker runtime smoke status | `<value>` | `<value>` | `N/A` | `PASS/PASS/PASS` | `reports/analysis/runtime-observability-baseline.json` |
| Container deployment contract pass | `<value>` | `PASS` | `N/A` | `PASS` | `bash scripts/run_full_runtime_delivery_gate.sh` |
| Deployment env contract pass | `<value>` | `PASS` | `N/A` | `PASS` | `bash scripts/run_full_runtime_delivery_gate.sh` |
| Docker runtime service role | `<value>` | `backup_smoke` | `N/A` | `backup_smoke` | `reports/analysis/runtime-delivery-gate/<timestamp>/runtime-delivery-gate-manifest.json` |
| Canonical PM2 ports | `<value>` | `8020/3020` | `N/A` | `8020/3020` | `reports/analysis/runtime-delivery-gate/<timestamp>/runtime-quality-summary/container-deployment-contract-report.json` |
| Backup smoke ports | `<value>` | `8021/3021` | `N/A` | `8021/3021` | `reports/analysis/runtime-delivery-gate/<timestamp>/runtime-quality-summary/container-deployment-contract-report.json` |
| Docker metrics `http_requests_total` delta | `<value>` | `<value>` | `N/A` | `>= 0` | `reports/analysis/runtime-observability-baseline.json` |
| Graphiti closeout coverage | `<valid>/<expected>` | `5/5` | `N/A` | `5/5` | `reports/analysis/*/*-graphiti-closeout.json` |
| Graphiti closeout validity gate | `<value>` | `PASS` | `N/A` | `PASS` | `bash scripts/run_tech_debt_weekly_report.sh` |

可复用校验命令：`RUNTIME_QUALITY_SUMMARY_JSON=<runtime-quality-summary/summary.json> bash scripts/run_runtime_observability_drift_gate.sh`
前端 PM2 runtime 工件采集：`python scripts/dev/quality_gate/collect_frontend_runtime_gate.py --type-ceiling-log <type-ceiling.log> --pm2-gate-log <pm2-gate.log> --regression-log <regression.log> --axe-log <axe.log> --current-tech-debt-baseline <tech-debt-baseline.current.json> --output <frontend-runtime-gate.json>`
API 性能漂移命令：`python scripts/dev/quality_gate/validate_api_performance_drift.py --baseline reports/analysis/api-performance-baseline.json --current-benchmark-json <api-performance-gate/benchmark.json>`
Monitoring auth closeout：`bash scripts/run_monitoring_auth_performance_baseline.sh`
完整运行门禁入口：`bash scripts/run_full_runtime_delivery_gate.sh`
容器 smoke 入口：`POSTGRES_PASSWORD=postgres TDENGINE_PASSWORD=taosdata bash scripts/run_containerized_runtime_smoke.sh`
容器化能力口径：PM2 canonical 仍是 `8020/3020`，container backup smoke 固定为 `8021/3021`
周报 closeout 门禁默认开启；如仅需生成观察性报告可临时设置：`TECH_DEBT_WEEKLY_REQUIRE_VALID_CLOSEOUTS=0 bash scripts/run_tech_debt_weekly_report.sh`

## 6.2A Graphiti Gate Closeouts
- runtime delivery gate closeout:
  - report: `reports/analysis/runtime-delivery-gate/<timestamp>/runtime-delivery-gate-graphiti-closeout.json`
  - episode_uuid: `<uuid>`
  - group_id: `mystocks_spec_runtime_delivery_gates`
- frontend runtime gate closeout:
  - report: `reports/analysis/frontend-runtime-gate/<timestamp>/frontend-runtime-gate-graphiti-closeout.json`
  - episode_uuid: `<uuid>`
  - group_id: `mystocks_spec_quality_gates`
- API performance gate closeout:
  - report: `reports/analysis/api-performance-gate/<timestamp>/api-performance-gate-graphiti-closeout.json`
  - episode_uuid: `<uuid>`
  - group_id: `mystocks_spec_quality_gates`
- monitoring auth performance gate closeout:
  - report: `reports/analysis/api-monitoring-auth-gate/<timestamp>/monitoring-auth-performance-gate-graphiti-closeout.json`
  - episode_uuid: `<uuid>`
  - group_id: `mystocks_spec_quality_gates`
- Docker runtime smoke closeout:
  - report: `reports/analysis/docker-runtime-smoke/<timestamp>/docker-runtime-smoke-graphiti-closeout.json`
  - episode_uuid: `<uuid>`
  - group_id: `mystocks_spec_quality_gates`

## 6.3 热点与行动
- Top 10 热点文件（含路径）:
  - `<path>`
- 下周治理任务（owner + deadline）:
  - `<task>`
- 阻塞项与所需决策:
  - `<blocker>`

## 6.4 结构性技术债补充项

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| 活跃兼容层 / shim 数量 | `<value>` | `<value or N/A>` | `<value or N/A>` | `<target or N/A>` | `<source>` |
| 活跃临时入口 / `*_new.py` 数量 | `<value>` | `<value or N/A>` | `<value or N/A>` | `<target or N/A>` | `<source>` |
| 活跃机械拆分文件数量 | `<value>` | `<value or N/A>` | `<value or N/A>` | `<target or N/A>` | `<source>` |
| 活跃备份文件数量 | `<value>` | `<value or N/A>` | `<value or N/A>` | `<target or N/A>` | `<source>` |
| 已满足退出条件但尚未退役对象数量 | `<value>` | `<value or N/A>` | `<value or N/A>` | `<target or N/A>` | `<source>` |
| 本周已完成代码路径判定 / 功能树判定清理项数量 | `<value>` | `<value or N/A>` | `<value or N/A>` | `<target or N/A>` | `<source>` |

## Structural Notes
- canonical_source changes:
  - `<note or (none)>`
- cleanup / removal verdicts:
  - `<note or (none)>`
- temporary asset ledger delta:
  - `<note or (none)>`
