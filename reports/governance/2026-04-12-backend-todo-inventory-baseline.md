# Backend TODO Inventory Baseline

> **补充规范说明**:
> 本文件用于把 `backend_todo_count` 基线从单一数字展开为可审计清单。
> 它是 `TD-008` 的执行入口，不替代共享规则正文。

**Generated:** 2026-04-12  
**Related debt item:** `TD-008`

## 1. Purpose

本文件用于：

- 解释 `backend_todo_count = 50` 的来源。
- 把 TODO 命中拆成可治理对象，而不是保留为单一总数。
- 将 active runtime TODO、兼容残余 TODO、算法/研究性 TODO 区分开来。

## 2. Metric Snapshot

| metric | measured | baseline | inferred | target | source_or_command |
| --- | --- | --- | --- | --- | --- |
| `backend_todo_count` | `50` | `50` | `current raw grep hits = 44 (narrower grep scope)` | `<=50` | `reports/analysis/tech-debt-baseline.json` |
| `repo_grep_raw_hits` | `44` | `N/A` | `excludes tests, markdown, json; may undercount baseline scope` | `N/A` | `rg -n "TODO" src web/backend --glob '!**/tests/**' --glob '!**/*.md' --glob '!**/*.json'` |

说明：

- `50` 仍是当前治理基线。
- 本轮 `44` 是较窄 grep 口径下的 raw hits，不应直接覆写基线。
- 后续应补 baseline counting rule，明确 `50` 是否包含更宽目录、特定文件类型或预处理规则。

## 3. Inventory Schema

| path | todo_category | context | runtime_role | verdict | owner | next_action |
| --- | --- | --- | --- | --- | --- | --- |

字段约束：

- `todo_category`: `runtime-placeholder` | `contract-gap` | `integration-gap` | `performance-observability-gap` | `legacy-noise`
- `verdict`: `real-debt` | `needs-owner` | `historical-noise`

## 4. Initial Inventory

| path | todo_category | context | runtime_role | verdict | owner | next_action |
| --- | --- | --- | --- | --- | --- | --- |
| `web/backend/app/tasks/backtest_tasks.py` | `integration-gap` | backtest task data-source selection | active runtime path | `real-debt` | `backend` | 明确 Mock/Real/Composite 策略 |
| `web/backend/app/api/trade/routes.py` | `contract-gap` | trade API database query path | active runtime path | `real-debt` | `backend` | 用真实数据库查询替换 TODO |
| `web/backend/app/api/alternative_data.py` | `integration-gap` | alternative data database manager wiring | active runtime path | `real-debt` | `backend` | 接入真实 database manager |
| `web/backend/app/api/monitoring.py` | `contract-gap` | 批量标记功能未落地 | active runtime path | `real-debt` | `backend` | 落地功能或在契约层降级 |
| `web/backend/app/api/signal_monitoring/get_signal_statistics.py` | `performance-observability-gap` | signal push / GPU / active signal metrics | active runtime path | `real-debt` | `backend` | 接入真实状态源，消除伪绿 |
| `web/backend/app/api/signal_monitoring/signal_history_response.py` | `performance-observability-gap` | GPU utilization source missing | active runtime path | `real-debt` | `backend` | 接入真实 GPU manager |
| `web/backend/app/api/backtest_ws.py` | `contract-gap` | websocket cancel flow missing | active runtime path | `real-debt` | `backend` | 落取消逻辑或收缩接口承诺 |
| `web/backend/app/services/algorithm_service.py` | `integration-gap` | placeholder algorithm import / indentation debt | active runtime path | `real-debt` | `backend` | 明确缺失算法实现范围 |
| `web/backend/app/services/monitoring_service.py` | `performance-observability-gap` | 历史对比逻辑 / 技术指标突破检测缺失 | active runtime path | `needs-owner` | `backend` | 先判定是否属于当前主线能力 |
| `web/backend/app/api/gpu_monitoring.py` | `integration-gap` | GPU monitor / metrics / exporter / history 未接入 | active runtime path | `real-debt` | `backend` | 切独立 GPU monitoring 治理批次 |
| `web/backend/app/api/data_lineage.py` | `integration-gap` | lineage tracker DI 未落地 | active runtime path | `real-debt` | `backend` | 从容器接入真实 tracker |
| `web/backend/app/api/announcement/routes.py` | `contract-gap` | AI analysis TODO | active runtime path | `needs-owner` | `backend` | 判定是否保留为未来能力 |
| `web/backend/app/api/technical/routes.py` | `contract-gap` | AI analysis TODO | active runtime path | `needs-owner` | `backend` | 判定是否保留为未来能力 |
| `web/backend/app/app_factory.py` | `legacy-noise` | router registration TODO comment | compatibility / bootstrap path | `historical-noise` | `main` | 若已被 registry 机制替代则移除陈旧注释 |
| `web/backend/app/api/monitoring_old/routes.py` | `legacy-noise` | old monitoring namespace AI TODO | compatibility path | `historical-noise` | `main` | 与旧 monitoring shim 一起归档判断 |
| `web/backend/app/backtest/strategies/turtle.py` | `contract-gap` | account value source TODO | active runtime path | `needs-owner` | `backend` | 判定是否属于回测引擎能力缺口 |
| `web/backend/app/services/advanced_analysis_service.py` | `integration-gap` | monitoring module import TODO | active service path | `needs-owner` | `backend` | 判定模块是否仍计划接入 |
| `web/backend/app/api/trading_monitor.py` | `legacy-noise` | GPU/business method TODO via pylint disable | active but drift-prone path | `needs-owner` | `backend` | 与 `gpu_monitoring.py` 统一判定 |

## 5. Rollup Summary

| metric | value |
| --- | --- |
| `baseline_total` | `50` |
| `repo_grep_raw_hits` | `44` |
| `reviewed_in_draft` | `18` |
| `real_debt_count` | `10` |
| `needs_owner_count` | `6` |
| `historical_noise_count` | `2` |

### By Directory

| directory | count |
| --- | --- |
| `web/backend/app/api` | `10` |
| `web/backend/app/api/signal_monitoring` | `4` |
| `web/backend/app/services` | `4` |
| `src/ml_strategy/automation` | `4` |
| `web/backend/app/tasks` | `1` |

### By Category

| todo_category | count |
| --- | --- |
| `integration-gap` | `5` |
| `contract-gap` | `7` |
| `performance-observability-gap` | `3` |
| `legacy-noise` | `3` |

## 6. Initial Priority Candidates

| rank | path | reason | suggested_action |
| --- | --- | --- | --- |
| 1 | `web/backend/app/api/gpu_monitoring.py` | 多个 TODO 聚集在 active API | 切独立治理批次 |
| 2 | `web/backend/app/api/signal_monitoring/get_signal_statistics.py` | 健康与统计值伪绿风险 | 接入真实状态源 |
| 3 | `web/backend/app/tasks/backtest_tasks.py` | 数据源选择策略悬空 | 先固定 runtime policy |
| 4 | `web/backend/app/api/monitoring.py` | 契约承诺未实现 | 决定落地或收缩契约 |
| 5 | `web/backend/app/api/trade/routes.py` | 真实数据库查询缺口 | 先判定查询来源 |

## 7. Relationship To Other Debt Items

- `TD-008` 聚焦 TODO inventory 与 owner/TTL 整理。
- `TD-009` 聚焦 placeholder/stub inventory。
- `TD-003` 聚焦 static analysis 总账分桶。
- `TD-006` 聚焦 security / critical first pass。

## 8. Verification

建议命令：

```bash
rg -n "TODO" src web/backend --glob '!**/tests/**' --glob '!**/*.md' --glob '!**/*.json'
rg -n "TODO" web/backend/app src/core src/governance src/services --glob '!**/tests/**'
```

## 9. Exit Condition

`TD-008` 进入“可执行”状态，当且仅当：

- `50` 的基线来源可解释。
- 已形成 TODO inventory 初稿与优先级列表。
- 至少能区分 `real-debt`、`needs-owner`、`historical-noise`。
- 后续可以直接按候选集切微批次，而不是重新解释 TODO 含义。
