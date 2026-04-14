# Backend Placeholder Inventory Baseline

> **补充规范说明**:
> 本文件用于把 `backend_placeholder_count` 基线拆解成真实治理对象。
> 规则口径以 `architecture/STANDARDS.md`、治理章程与当前代码真相为准。

**Generated:** 2026-04-12  
**Related debt item:** `TD-009`

## 1. Purpose

本文件用于：

- 解释 `backend_placeholder_count = 502` 的来源。
- 区分真实债务与合法占位。
- 为后续 P0 / P1 批次提供可执行输入。

## 2. Metric Snapshot

| metric | measured | baseline | inferred | target | source_or_command |
| --- | --- | --- | --- | --- | --- |
| `backend_placeholder_count` | `502` | `502` | `initial draft reviewed subset = 15` | `<=502` | `reports/analysis/tech-debt-baseline.json` + repo grep |

## 3. Inventory Schema

| path | placeholder_type | context | runtime_role | verdict | owner | next_action |
| --- | --- | --- | --- | --- | --- | --- |

字段约束：

- `placeholder_type`: `TODO-like placeholder` | `stub return` | `mock/demo placeholder` | `doc/example placeholder` | `config/template placeholder`
- `verdict`: `real-debt` | `accepted-fixture` | `accepted-demo` | `historical-noise`

## 4. Exclusion Notes

以下 grep 命中默认不计入本清单主表：

- SQL bind `placeholders` 变量，例如 `src/core/database.py`
- 正常测试替身 / `unittest.mock` / `dummy_calc`
- 明确属于 demo / test fixture / archive 的非 runtime 资产

## 5. Initial Inventory

| path | placeholder_type | context | runtime_role | verdict | owner | next_action |
| --- | --- | --- | --- | --- | --- | --- |
| `web/backend/app/tasks/backtest_tasks.py` | `TODO-like placeholder` | backtest task execution | active runtime path | `real-debt` | `backend` | 明确 Mock/Real/Composite 选择策略，避免任务层持续悬空 |
| `web/backend/app/api/alternative_data.py` | `TODO-like placeholder` | alternative data API | active runtime path | `real-debt` | `backend` | 传入真实 database manager 或显式降级 |
| `web/backend/app/api/monitoring.py` | `TODO-like placeholder` | monitoring API batch mark | active runtime path | `real-debt` | `backend` | 实现批量标记或在契约层降级 |
| `web/backend/app/api/backtest_ws.py` | `TODO-like placeholder` | websocket cancel flow | active runtime path | `real-debt` | `backend` | 落取消逻辑或删除误导接口承诺 |
| `web/backend/app/api/signal_monitoring/get_signal_statistics.py` | `TODO-like placeholder` | signal push / gpu / active signal counters | active runtime path | `real-debt` | `backend` | 拆成实际数据接入批次，避免健康值恒定伪绿 |
| `web/backend/app/api/signal_monitoring/signal_history_response.py` | `TODO-like placeholder` | GPU utilization field | active runtime path | `real-debt` | `backend` | 接入 GPU manager 或在 schema 中显式 nullable 来源 |
| `web/backend/app/api/trade/routes.py` | `TODO-like placeholder` | trade API data source | active runtime path | `real-debt` | `backend` | 用真实数据库查询替换占位注释 |
| `web/backend/app/api/gpu_monitoring.py` | `TODO-like placeholder` | GPU monitoring service / metrics / exporter / history | active runtime path | `real-debt` | `backend` | 形成独立治理批次，不再保留多处 CLI-5 TODO |
| `web/backend/app/api/data_lineage.py` | `TODO-like placeholder` | lineage tracker DI | active runtime path | `real-debt` | `backend` | 从依赖注入容器接入真实 tracker |
| `web/backend/app/api/announcement/routes.py` | `TODO-like placeholder` | AI analysis | active runtime path | `real-debt` | `backend` | 明确是未来能力还是删除误导性注释 |
| `web/backend/app/api/technical/routes.py` | `TODO-like placeholder` | AI analysis | active runtime path | `real-debt` | `backend` | 同上，避免“接口存在但逻辑未落地” |
| `web/backend/app/services/algorithm_service.py` | `stub return` | placeholder algorithm classes | active runtime path | `real-debt` | `backend` | 标明哪些算法缺真实实现，避免 placeholder class 长期存活 |
| `web/backend/app/api/_technical_patterns_router.py` | `doc/example placeholder` | placeholder routes module | active runtime path | `real-debt` | `backend` | 决定落地真实路由还是退出注册面 |
| `web/backend/app/api/monitoring_old/__init__.py` | `doc/example placeholder` | old monitoring namespace shim | compatibility path | `historical-noise` | `main` | 作为历史兼容层登记，不纳入 runtime 主清单 |
| `web/backend/app/api/risk/stop_loss.py` | `config/template placeholder` | request default value `"placeholder"` | active runtime path | `real-debt` | `backend` | 复核默认值是否应为 `None` 或显式校验失败 |

## 6. Verdict Rules

### real-debt

适用于：

- 位于 active backend runtime path。
- 影响 API / service / governance 主链。
- 当前仍依赖 TODO、placeholder、stub 语义维持功能壳。

### accepted-fixture

适用于：

- 测试夹具、测试替身、隔离环境专用占位。
- 不进入生产链路。

### accepted-demo

适用于：

- demo / example / sample 资产。
- 已明确不属于主线真相。

### historical-noise

适用于：

- 历史归档。
- 旧兼容层。
- 当前不应进入 runtime 主治理清单。

## 7. Rollup Summary

| metric | value |
| --- | --- |
| `baseline_total` | `502` |
| `reviewed_in_draft` | `15` |
| `real_debt_count` | `14` |
| `accepted_fixture_count` | `0` |
| `accepted_demo_count` | `0` |
| `historical_noise_count` | `1` |
| `needs_followup_classification_count` | `0` |

### Top Risk Paths

| rank | path | verdict | reason | next_action |
| --- | --- | --- | --- | --- |
| 1 | `web/backend/app/api/gpu_monitoring.py` | `real-debt` | 多个 TODO 聚集在 active API | 切独立治理批次 |
| 2 | `web/backend/app/api/signal_monitoring/get_signal_statistics.py` | `real-debt` | 健康/统计值存在伪绿风险 | 接入真实状态源 |
| 3 | `web/backend/app/tasks/backtest_tasks.py` | `real-debt` | 数据源选择仍悬空 | 先补策略约束 |
| 4 | `web/backend/app/services/algorithm_service.py` | `real-debt` | placeholder classes 存在误导性 | 明确缺失实现范围 |
| 5 | `web/backend/app/api/_technical_patterns_router.py` | `real-debt` | placeholder route 仍在 active tree | 决定落地或退场 |

## 8. Verification

建议命令：

```bash
rg -n "TODO|FIXME|TBD|placeholder|stub" web/backend/app src/core src/governance src/services
```

## 9. Exit Condition

`TD-009` 视为完成，当且仅当：

- `502` 的来源可解释。
- `real-debt` 与合法占位已分离。
- 至少形成一批高优先级 backend placeholder 候选。
- 后续 P0 / P1 清理批次可直接从本清单切出。
