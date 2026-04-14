# Backend Static Analysis Bucketing Plan

> **补充规范说明**:
> 本文件用于把 backend static analysis 总账从单一大数拆成可执行治理波次。
> 它是 `TD-003` 的执行入口，不替代共享规则正文。

**Generated:** 2026-04-12  
**Related debt item:** `TD-003`  
**Related inputs:** `TD-009`, `reports/analysis/tech-debt-baseline.json`

## 1. Purpose

本文件用于：

- 解释 backend static analysis `1253` 条问题的当前分类口径。
- 把总账拆成可执行治理波次，而不是直接做全量平推。
- 把高风险 runtime truth debt 与低风险格式/文档类问题分离。

## 2. Metric Snapshot

| metric | measured | baseline | inferred | target | source_or_command |
| --- | --- | --- | --- | --- | --- |
| `backend_static_total_issues` | `1253` | `1253` | `N/A` | `<=1253` | `reports/analysis/tech-debt-baseline.json` |
| `critical_issues` | `49` | `49` | `overlaps with security_issues` | `decrease first` | same |
| `warning_issues` | `1195` | `1195` | `contains multiple sub-buckets` | `batch by wave` | same |
| `suggestion_issues` | `9` | `9` | `lowest immediate risk` | `N/A` | same |
| `docstring_issues` | `619` | `619` | `mostly low runtime risk` | `phase later` | same |
| `type_annotation_issues` | `400` | `400` | `likely intersects with endpoint/pydantic issues` | `reduce on core paths first` | same |
| `pydantic_issues` | `119` | `119` | `contract-sensitive` | `prioritize active APIs` | same |
| `import_issues` | `9` | `9` | `usually narrow but break-prone` | `clear early` | same |
| `endpoint_function_issues` | `174` | `174` | `active API risk bucket` | `triage before docstring wave` | same |

## 3. Structural Debt Disclosure

| field | value |
| --- | --- |
| `canonical_source` | `reports/analysis/tech-debt-baseline.json` |
| `compatibility_surface` | 当前 runtime 不因本计划新增并行规则面 |
| `callers_or_consumers` | 技术债治理台账、后续 `TD-006`、后续 backend quality waves |
| `verification_command` | `python -m json.tool reports/analysis/tech-debt-baseline.json >/dev/null` |
| `exit_condition` | static analysis 不再只以 `1253` 单值存在，已形成至少 3 个可执行治理波次 |

## 4. Bucketing Rules

### Wave 1: Runtime Truth Debt

优先处理 active backend runtime path 上的 TODO / placeholder / stub / import-sensitive 问题。

适用特征：

- 直接位于 `web/backend/app/api/*`、`web/backend/app/services/*`、`web/backend/app/tasks/*`
- 已在 `TD-009` inventory 中被标记为 `real-debt`
- 容易与 `endpoint_function_issues`、`import_issues`、部分 `pydantic_issues` 重叠

### Wave 2: Contract-Sensitive API Debt

优先处理影响 API 契约稳定性与 schema 真值的 issues。

适用特征：

- `endpoint_function_issues`
- `pydantic_issues`
- active v1 API / auth / system settings / monitoring chains

### Wave 3: Security-Critical Issues

和 `TD-006` 并行，但单独追踪。

适用特征：

- `critical_issues`
- `security_issues`
- 鉴权、令牌、备份恢复、管理员接口、rate limit、安全日志路径

### Wave 4: Type Annotation / Import Cleanup

优先在核心路径处理 `type_annotation_issues` 与 `import_issues`。

### Wave 5: Docstring / Suggestion Tail

最后处理 `docstring_issues` 与其余低风险建议项，不让它们污染前 4 个高风险波次。

## 5. Initial Wave Map

| wave | focus | issue families | initial candidate paths | owner | note |
| --- | --- | --- | --- | --- | --- |
| `Wave 1A` | runtime placeholder debt | endpoint / import / warning | `web/backend/app/api/gpu_monitoring.py`, `web/backend/app/api/signal_monitoring/get_signal_statistics.py`, `web/backend/app/tasks/backtest_tasks.py`, `web/backend/app/services/algorithm_service.py`, `web/backend/app/api/_technical_patterns_router.py` | `backend` | 与 `TD-009` 直接衔接 |
| `Wave 1B` | runtime placeholder debt | endpoint / warning | `web/backend/app/api/alternative_data.py`, `web/backend/app/api/monitoring.py`, `web/backend/app/api/backtest_ws.py`, `web/backend/app/api/data_lineage.py`, `web/backend/app/api/trade/routes.py` | `backend` | 第二梯队 runtime truth debt |
| `Wave 2` | contract-sensitive API debt | `pydantic`, `endpoint_function` | active v1 APIs, auth/admin/system settings/monitoring chains | `backend` | 先以 active API 为范围，不做全仓平推 |
| `Wave 3` | security-critical issues | `critical`, `security` | `web/backend/app/core/security.py`, `web/backend/app/api/auth.py`, `web/backend/app/api/v1/admin/auth.py`, `web/backend/app/api/backup_recovery.py`, `web/backend/app/api/backup_recovery_secure/*` | `backend` | 与 `TD-006` 共用起始范围 |
| `Wave 4` | type/import cleanup | `type_annotation`, `import` | core backend + services + active routers | `backend` | 在前 3 波后推进 |
| `Wave 5` | documentation tail | `docstring`, `suggestion` | 全仓 backend | `backend` | 最后处理 |

## 6. Immediate Next Batch

当前建议直接从 `Wave 1A` 开始，原因：

- 已有 `TD-009` 的 runtime inventory 作为输入。
- 这批问题最可能影响 active endpoint 真值。
- 它们比 docstring/type 大盘更容易形成“问题减少 + 主线更真实”的正收益。

### Wave 1A Candidate Set

| path | reason |
| --- | --- |
| `web/backend/app/api/gpu_monitoring.py` | TODO 聚集，active API 误导风险高 |
| `web/backend/app/api/signal_monitoring/get_signal_statistics.py` | 健康值和统计值存在伪绿风险 |
| `web/backend/app/tasks/backtest_tasks.py` | 数据源选择策略仍悬空 |
| `web/backend/app/services/algorithm_service.py` | placeholder algorithm classes 暗示不真实实现 |
| `web/backend/app/api/_technical_patterns_router.py` | placeholder route 仍在 active tree |

## 7. Verification

建议验证命令：

```bash
python -m json.tool reports/analysis/tech-debt-baseline.json >/dev/null
rg -n '1253|49|619|400|119|174' reports/analysis/tech-debt-baseline.json
rg -n 'gpu_monitoring|get_signal_statistics|algorithm_service|technical_patterns_router|backtest_tasks' web/backend/app
```

## 8. Exit Condition

`TD-003` 进入“可执行”状态，当且仅当：

- static analysis 总账不再只以 `1253` 单值存在。
- 至少形成 `Wave 1A`、`Wave 2`、`Wave 3` 三个独立治理入口。
- 后续执行可以直接按 wave 切批次，而不是重新解释统计口径。
