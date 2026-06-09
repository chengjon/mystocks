# Backend Route Table Duplicate Routes Review

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> 审核对象: `docs/reports/quality/backend-route-table-openapi-baseline-2026-05-18.md`  
> 关联数据: `web/backend/--output-dir/backend-audit-baseline.json`  
> 审核日期: 2026-05-18  
> 审核方法: Matt Pocock skills 视角（`to-issues` independently-grabbable / `ready-for-agent` 标准，`improve-codebase-architecture` deepening opportunity 标准，`zoom-out` 上下文校准）  
> 约束来源: `docs/agents/*.md`、`architecture/STANDARDS.md`、`openspec/AGENTS.md`、`web/backend/CONTEXT.md`

## 总体结论

Route table 扫描揭示的问题比 Phase 3 修订计划中的 P3-B/P3-C 颗粒度更严重。它不再只是“几个 flat/package 目录要收口”的问题，而是 API 路由契约缺少 single source of truth：

- `664` 个 route decorators 覆盖 `183` 个模块。
- baseline JSON 记录 `81` 个 duplicate route groups。
- route table 报告写有 `GET /health` 在 `22` 个模块中定义、`GET /status` 在 `13` 个模块中定义。
- announcement / strategy / trading / backup 等业务域存在 flat/package 或同域双入口重复。

按 Matt Pocock `to-issues` 标准，这些问题目前不应直接拆成 `ready-for-agent` 修复单。下一步应先产出 route contract decision records 和 OpenSpec proposals，再进入实现。

## 关键限定

当前扫描方法是 AST 静态扫描，报告第 8 行说明它扫描 `app/api/` 下 `.py` 文件的 `@router.get/post/put/delete/patch` 装饰器。脚本 `scripts/dev/backend_audit_baseline.py` 的 duplicate key 是本地 decorator 的 `method + path`，没有展开：

- `router_registry.py` 中的 `include_router(..., prefix=...)`
- `VERSION_MAPPING.py` 中的 version prefix
- router 自身可能带的 `APIRouter(prefix=...)`
- app-level route 和 OpenAPI 最终 path

因此，扫描能可靠证明“模块路由表面重复、治理风险高、需要 canonical 决策”，但不能单独证明“所有重复都是运行时最终 URL 冲突”。报告中“运行时只有一个生效（取决于注册顺序）”这类表述，只能用于最终 full path 也相同的 case；其他 case 应改为“存在同名局部路由/同域重复实现，需展开最终 route table 后判定运行时冲突或兼容别名”。

## Blockers

### 1. P3-B Safe Closure 需要冻结

Phase 3 修订计划仍包含 P3-B Safe Closure，但这次 route table 结果表明 P3-B 中的 route 相关任务不能再按低风险处理。

特别是：

- P3-B1 announcement 双注册不能只是“修复 bug”，它需要 route contract decision。
- P3-B6 七域 flat→package 收口不能作为一个低风险 issue；它应被拆成多个 domain route contract issues。
- P3-C7 健康端点收敛不能只看 health 数字，它需要统一 health/status 语义和兼容策略。

建议:

- 暂停创建 route 相关 `ready-for-agent` issues。
- 只允许创建 `needs-triage` 或 decision/readiness issues。
- P3-B 中凡涉及 route prefix、OpenAPI path、消费者路径、兼容 alias 的 issue，一律提升到 decision 或 OpenSpec 阶段。

### 2. `GET /health` / `GET /status` 是语义治理问题，不是简单去重问题

报告第 115-116 行写：

- `GET /health`: 22 个模块。
- `GET /status`: 13 个模块。

这些 endpoint 名称重复严重，但不能简单合并为一个 endpoint。它们至少混用了三类语义：

- 平台 liveness/readiness，例如 `/health`、`/health/ready`。
- 依赖健康检查，例如 database、adapter、source health。
- 业务域运行状态，例如 trading status、strategy status、backup job status。

如果直接删除或合并，会破坏现有前端、测试、运维探针和域内监控语义。

建议新增 P3-A decision issue：

```text
P3-A5: Define health/status route taxonomy and canonical contract
```

输出应包含：

- liveness/readiness canonical endpoints。
- service dependency health contract。
- domain status contract。
- module-local health/status 是否允许存在。
- response schema 统一或豁免规则。
- deprecated aliases 和下线条件。

这个 issue 应为 `OpenSpec required`，在批准前不允许健康/状态端点收敛进入实现。

### 3. 业务域重复路由应升级为 OpenSpec proposals

报告第 29-98 行列出了 announcement、strategy、trading、backup 的同域重复：

- announcement: flat `announcement.py` vs package `announcement/routes.py`。
- strategy: flat `strategy_mgmt.py` vs package `strategy_management/`。
- trading: `trading_runtime.py` vs `trading_monitor.py`。
- backup: `backup_recovery.py` vs `backup_recovery_secure/`。

这些不是纯机械删除。它们涉及 API contract、prefix、response shape、handler ownership、测试引用、前端消费者和兼容窗口。

建议:

- 每个域单独 OpenSpec proposal 或至少单独 decision record。
- 不要把这些域塞进一个 “flat/package 收口” parent issue 后直接执行。
- 每个域先完成：
  - current full route table。
  - OpenAPI path diff。
  - consumer scan。
  - canonical owner decision。
  - compatibility alias policy。
  - rollback and deprecation trigger。

### 4. 报告中的重复组数字需要统一

报告第 18 行写“去重路由路径（method+path 相同）约 200 组”，但 `web/backend/--output-dir/backend-audit-baseline.json` 中 `duplicates.total_duplicate_groups` 是 `81`。

这会影响 issue 优先级判断。`~200` 和 `81` 代表不同口径：

- `81` 可能是脚本 `find_duplicate_routes()` 的 duplicate groups。
- `~200` 可能是人工或另一脚本统计的 route path 去重结果。

建议:

- 在报告中明确两个指标的定义。
- 如果 `~200` 是 approximate，应替换成精确值或删除。
- 每个后续 issue 应引用一个唯一指标，例如 `duplicate_groups_by_local_decorator_path = 81`。

### 5. baseline artifact 落点不合适

当前 JSON 产物位于：

```text
web/backend/--output-dir/backend-audit-baseline.json
```

这看起来像命令参数被当成目录名写入了 active backend tree。审计产物不应长期放在 `web/backend/--output-dir/`。

建议:

- 将产物迁移或重新生成到 `docs/reports/quality/generated/` 或 `reports/analysis/`。
- 更新报告中的生成命令和 artifact path。
- 将 `web/backend/--output-dir/` 纳入清理候选，按 `architecture/STANDARDS.md` 的临时产物治理规则处理。

## 对 Phase 3 计划的影响

### 必须新增或修改的 P3-A 决策项

| Issue | 建议状态 | 原因 |
|---|---|---|
| P3-A5 health/status taxonomy | 新增，OpenSpec required | `GET /health` / `GET /status` 是跨域契约问题 |
| P3-A6 trading route ownership | 新增，OpenSpec required | `trading_runtime.py` vs `trading_monitor.py` 重复，不是 flat/package 常规迁移 |
| P3-A7 backup route ownership/security boundary | 新增，OpenSpec required | backup 与 backup_recovery_secure 同路由重复，涉及安全边界 |
| P3-A1 announcement canonical route decision | 升级 | 必须基于 full route table 和消费者证据决定 `/api/announcement` 与 `/api/v1/announcement` |
| P3-A2 strategy canonical route decision | 保持 required | 报告证明 strategy 重复更具体，需纳入 proposal 输入 |

### 必须调整的 P3-B/P3-C

| 原项 | 调整建议 |
|---|---|
| P3-B1 修复 announcement 双注册 | 依赖 P3-A1 approval；实现 issue 不得先行 |
| P3-B6 低复杂度域 flat→package 收口 | 拆为多个 domain route contract draft；不标 `ready-for-agent` |
| P3-C1 strategy route 收敛 | 保持 OpenSpec required，并把报告第 54-65 行作为证据 |
| P3-C7 健康端点收敛 | 改为 health/status taxonomy proposal 后的 implementation |
| backup 域 | 从普通 backup cleanup 提升为 route/security boundary proposal |
| trading 域 | 从 trading runtime/monitor 技术债提升为 canonical owner proposal |

## 建议的 issue 拆分

### Readiness

```text
P3-0.4: Generate final full route table with prefixes applied
```

Acceptance criteria:

- Expand `VERSION_MAPPING.py` prefixes.
- Expand `router_registry.py include_router()` prefixes.
- Capture `APIRouter(prefix=...)`.
- Produce final `method + full_path + source_module + handler` table.
- Produce duplicate final full path report separately from local decorator duplicate report.

```text
P3-0.5: Normalize route duplicate metrics
```

Acceptance criteria:

- Define `local_decorator_duplicate_group`.
- Define `final_full_path_duplicate_group`.
- Define `domain_alias_or_compat_route`.
- Reconcile report `~200` with JSON `81`.

### Decision

```text
P3-A5: health/status route taxonomy decision
P3-A6: trading canonical route owner decision
P3-A7: backup route owner and security boundary decision
```

Each decision record should contain:

- Current facts from route table baseline.
- Consumers and tests.
- Options considered.
- Canonical owner.
- Compat aliases.
- OpenSpec proposal path.
- Implementation issues unlocked.

### Implementation

Implementation issues should not be created as `ready-for-agent` until their decision record and OpenSpec gate are complete.

## Deepening Opportunities

### 1. API Route Contract Registry

Problem: canonical route ownership currently lives across `VERSION_MAPPING.py`, `router_registry.py`, flat files, package routers, and historical compatibility routes.

Solution: introduce a generated or declarative route contract registry that records canonical owner, prefix, compatibility aliases, and sunset conditions.

Benefit: route changes become reviewable contract changes rather than scattered `include_router` edits.

### 2. Health/Status Contract Layer

Problem: `health` and `status` are shallow labels used for unrelated semantics across modules.

Solution: define three contracts: platform health, dependency health, domain operational status.

Benefit: tests and monitoring can assert the right contract instead of chasing dozens of local `/health` endpoints.

### 3. Domain Route Ownership Map

Problem: announcement / strategy / trading / backup have multiple owners with near-identical handlers.

Solution: create a domain route ownership map tied to OpenSpec decisions.

Benefit: flat/package retirement becomes a sequence of contract-preserving moves, not ad hoc deletion.

## Minimum Changes Before Execution

1. Amend `backend-route-table-openapi-baseline-2026-05-18.md` to distinguish local decorator duplicates from final full path conflicts.
2. Reconcile `~200` duplicate groups with JSON `81` duplicate groups.
3. Move or regenerate `web/backend/--output-dir/backend-audit-baseline.json` to a report artifact path.
4. Update `web/backend/CONTEXT.md`: current health endpoint landscape still says older counts and is now stale.
5. Revise Phase 3 plan: add P3-0.4/P3-0.5 and P3-A5/P3-A6/P3-A7.
6. Mark all route-remediation issues as `needs-triage` or decision-only until OpenSpec approvals exist.

## Verdict

This finding is real and high severity, but the immediate response should be governance and contract clarification, not broad route deletion.

The next safe step is to convert the route table scan into:

- a final full-path route table,
- a route duplicate taxonomy,
- domain-specific decision records,
- OpenSpec proposals for health/status, strategy, trading, backup, and announcement route ownership.

Only after that should implementation issues become `ready-for-agent`.

