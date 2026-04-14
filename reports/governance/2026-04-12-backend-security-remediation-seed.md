# Backend Security Remediation Seed

> **补充规范说明**:
> 本文件用于把 backend security issues 从基线数字转换成首批 remediation 入口。
> 它是 `TD-006` 的执行入口，不替代正式安全规范或代码级审计报告。

**Generated:** 2026-04-12  
**Related debt item:** `TD-006`  
**Related baseline:** `reports/analysis/tech-debt-baseline.json`

## 1. Purpose

本文件用于：

- 固定 backend `security_issues = 49` 的治理起点。
- 先定义首批 review surface，而不是等待完整 issue 明细后再开始。
- 将安全治理与广义 static analysis 大盘解耦。

## 2. Metric Snapshot

| metric | measured | baseline | inferred | target | source_or_command |
| --- | --- | --- | --- | --- | --- |
| `security_issues` | `49` | `49` | `overlaps with critical_issues` | `decrease first` | `reports/analysis/tech-debt-baseline.json` |
| `critical_issues` | `49` | `49` | `security-heavy first pass` | `decrease first` | same |

说明：

- 当前仓库内未见与这 `49` 条一一对应的 checked-in analyzer 明细清单。
- 因此本文件先固定 remediation 范围和 review lane，再由后续批次补 issue-to-file 映射。

## 3. Security Review Lanes

### Lane A: Auth / Token / Session

目标范围：

- `web/backend/app/core/security.py`
- `web/backend/app/api/auth.py`
- `web/backend/app/api/v1/admin/auth.py`
- `web/backend/app/api/trading_runtime.py`

重点：

- token 验证链
- fallback 行为
- 管理员接口保护
- 会话刷新与失效处理

### Lane B: Backup / Recovery / Privileged Operations

目标范围：

- `web/backend/app/api/backup_recovery.py`
- `web/backend/app/api/backup_recovery_secure/*`

重点：

- 权限校验
- 安全日志
- 高权限操作隔离
- `/tmp` 安全日志输出路径风险

### Lane C: Router Protection / Security-Sensitive Endpoints

目标范围：

- `web/backend/app/api/data_source_config.py`
- `web/backend/app/api/strategy_mgmt.py`
- `web/backend/app/api/task_security_support.py`
- `web/backend/app/api/cache.py`

重点：

- 认证依赖一致性
- `verify_token` / `get_current_user` 使用面
- 是否存在保护绕过或兼容层漂移

## 4. Initial Candidate Set

| rank | path | lane | reason | next_action |
| --- | --- | --- | --- | --- |
| 1 | `web/backend/app/core/security.py` | `Lane A` | 整体安全链根节点 | 先做函数级 review map |
| 2 | `web/backend/app/api/auth.py` | `Lane A` | 登录、token、fallback、mock/testing 逻辑集中 | 先区分 test-only fallback 与 production path |
| 3 | `web/backend/app/api/v1/admin/auth.py` | `Lane A` | 管理员认证面 | 检查权限边界和 refresh / logout 流程 |
| 4 | `web/backend/app/api/backup_recovery.py` | `Lane B` | 高权限备份恢复接口 | 复核权限、日志、速率限制 |
| 5 | `web/backend/app/api/backup_recovery_secure/backup_security_support.py` | `Lane B` | 安全支撑逻辑与日志输出集中 | 复核 `/tmp` 日志落盘与 handler 行为 |
| 6 | `web/backend/app/api/data_source_config.py` | `Lane C` | 使用 `verify_token` 的配置路径 | 检查是否有保护不一致 |
| 7 | `web/backend/app/api/strategy_mgmt.py` | `Lane C` | 使用 `verify_token` 的策略管理路径 | 检查依赖注入一致性 |
| 8 | `web/backend/app/api/task_security_support.py` | `Lane C` | 安全支持层命名已暴露敏感职责 | 补 review note 与 call graph 范围 |

## 5. Review Questions

本轮安全治理至少回答以下问题：

1. 是否存在 test/mock fallback 误入生产路径的可能。
2. 是否存在高权限接口认证依赖不一致。
3. 是否存在 `/tmp`、本地文件、弱日志输出等低门槛敏感落盘。
4. 是否存在“兼容层仍暴露敏感能力”的情况。
5. 是否存在 security-sensitive endpoint 与 current canonical auth chain 脱钩的问题。

## 6. Relationship To TD-003

- `TD-006` 只负责 security / critical first pass。
- `TD-003` 负责 static analysis 总账分桶。
- 两者共享基线来源，但执行批次必须分开，避免安全问题被 docstring/type 大盘稀释。

## 7. Verification

建议验证命令：

```bash
python -m json.tool reports/analysis/tech-debt-baseline.json >/dev/null
rg -n 'security_issues|critical_issues' reports/analysis/tech-debt-baseline.json
rg -n 'verify_token|get_current_user|security|backup_security|HTTPBearer|OAuth2PasswordBearer' web/backend/app/core web/backend/app/api
```

## 8. Exit Condition

`TD-006` 进入“可执行”状态，当且仅当：

- 已固定首批 security review lanes。
- 已列出首批 candidate set。
- 后续可以直接开 `Lane A` / `Lane B` / `Lane C` 微批次，而不是重新解释 `49` 的意义。
