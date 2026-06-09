# Backend OpenSpec Drafts Review

> **Current status (2026-05-18 later pass)**:
> This document reviews an earlier draft snapshot. Do not use its Blockers
> section alone as the current approval status. Use
> `docs/reports/quality/backend-openspec-drafts-mattpocock-review-2026-05-18-addendum.md`
> and
> `docs/reports/quality/backend-openspec-drafts-post-mattpocock-review-2026-05-18.md`
> for the current review stance and resolved/stale blocker disposition.

> 审核对象:
> - `openspec/changes/consolidate-backend-api-domain-routers/`
> - `openspec/changes/migrate-backend-singletons-to-lifecycle-di/`
> - `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/`
> - `openspec/changes/consolidate-backend-health-endpoints/`
>
> 审核日期: 2026-05-18  
> 审核方法: Matt Pocock skills 视角（`to-issues` independently-grabbable / `ready-for-agent` 标准，`improve-codebase-architecture` deepening opportunity 标准，`zoom-out` 上下文校准）  
> 本地 skills 配置来源: `docs/agents/issue-tracker.md`、`docs/agents/triage-labels.md`、`docs/agents/domain.md`  
> 项目约束来源: `architecture/STANDARDS.md`、`openspec/AGENTS.md`、`web/backend/CONTEXT.md`

## 结论

四个 OpenSpec 草案的方向是正确的，且已明显吸收前几轮审查意见：proposal/design/tasks/spec delta 结构完整，包含 OpenAPI diff、consumer matrix、compatibility shim、rollback、teardown、import/runtime smoke 等关键门禁。

`openspec validate --strict` 对四个 change 均返回 valid：

| Change | Strict validation |
|---|---|
| `consolidate-backend-api-domain-routers` | valid |
| `migrate-backend-singletons-to-lifecycle-di` | valid |
| `split-backend-core-modules-with-compatibility-wrappers` | valid |
| `consolidate-backend-health-endpoints` | valid |

CLI 在 validate 后出现 PostHog telemetry flush 网络错误，但 validate 结果已先返回 `Change '<id>' is valid`，该 telemetry 错误不构成 OpenSpec 校验失败。

建议结论：**可进入审批评审，但不建议无条件批准实施**。批准前应补一个跨 proposal 的 orchestration / dependency matrix，并修正 route table 新证据带来的 scope gaps。

## 结构检查

| Change | Files | Spec deltas | Requirements | Scenarios | Tasks |
|---|---:|---:|---:|---:|---:|
| `consolidate-backend-api-domain-routers` | 6 | 3 | 7 | 11 | 25 |
| `migrate-backend-singletons-to-lifecycle-di` | 5 | 2 | 4 | 5 | 21 |
| `split-backend-core-modules-with-compatibility-wrappers` | 5 | 2 | 4 | 6 | 21 |
| `consolidate-backend-health-endpoints` | 6 | 3 | 7 | 7 | 23 |

所有 change 都有 `proposal.md`、`tasks.md`、`design.md` 和 spec deltas。所有 design 都包含 `Non-Goals`、`Rollback`、`Open Questions`。这满足 OpenSpec 草案的基础结构要求。

## Blockers Before Approval

### 1. 缺少四个 proposal 的总编排矩阵

四个草案彼此有真实依赖，但目前依赖分散在各自的 design/tasks 中，没有一个审批层面的 implementation order。

关键交叉依赖：

- API domain router consolidation 和 health endpoint consolidation 都会改变 route exposure、OpenAPI diff、consumer matrix。
- Core split 和 lifecycle DI 都可能触碰 database/cache/security/socketio/logger 等 Core 模块。
- Singleton DI 对 service/provider 路径敏感；Core split 会改变 import shape。
- Health endpoint consolidation 可能依赖 API route table full-path expansion。

风险：

- 两个 change 同时实施时，可能在同一 router、OpenAPI contract 或 Core import surface 上互相覆盖。
- 后续 GitHub issues 无法独立判断 `Blocked by`，不满足 Matt Pocock `ready-for-agent` 标准。

建议新增一个审批前 artifact：

```text
docs/reports/quality/backend-openspec-change-orchestration-2026-05-18.md
```

至少包含：

- change execution order。
- shared files / shared contract surfaces。
- blocking dependencies。
- allowed parallel batches。
- route/OpenAPI diff owner。
- import compatibility owner。
- rollback owner。

### 2. API domain routers 草案未覆盖 route scan 中的 trading / backup 高风险域

`consolidate-backend-api-domain-routers` 覆盖 announcement、strategy、risk，这是合理的。但 2026-05-18 route table scan 已揭示 trading 和 backup 也有严重重复：

- trading: `trading_runtime.py` vs `trading_monitor.py`。
- backup: `backup_recovery.py` vs `backup_recovery_secure/`。

当前 C 草案中 `trading` 和 `backup` 没有进入 scope，也没有被明确列入 Non-Goals / deferred proposals。由于 change 名称是 “backend API domain routers”，这个 omission 会造成审批歧义：评审者可能以为所有高风险 domain router 重复都被纳入了治理。

建议二选一：

- 扩展 C 草案，纳入 trading / backup 的 decision record，但 implementation 可分后续 batch。
- 或在 C design 的 `Non-Goals` 中明确：trading / backup route ownership 将由单独 OpenSpec change 覆盖，并登记 blocked follow-up。

不建议维持当前模糊状态。

### 3. Health endpoint 草案没有真正覆盖 `GET /status`

`consolidate-backend-health-endpoints` 对 health taxonomy、readiness、services probe 做得比较扎实。但 route scan 的严重发现不是只有 health：

- `GET /health`: 22 个模块。
- `GET /status`: 13 个模块。

当前 G 草案里 `status` 只作为 PM2 status 或 response/status code 的语境出现，没有作为 route taxonomy 的一等对象。这会留下一个明显治理洞：health 收敛后，status 重复仍然存在。

建议：

- 将 G 草案范围改为 `health/status endpoint taxonomy`。
- 或新增单独 proposal：`consolidate-backend-status-endpoints`。
- 如果选择后者，G 的 Non-Goals 必须明确 status endpoint 收敛不在本 change 中，并引用 follow-up proposal。

### 4. C/G 草案需要吸收 route scan 的关键限定：local decorator duplicate 不等于 final URL conflict

前一轮 route table review 已确认，当前扫描主要基于 AST decorator 的 local `method + path`，没有完全展开：

- `router_registry.py` include prefix。
- `VERSION_MAPPING.py` prefix。
- router-level `APIRouter(prefix=...)`。
- final FastAPI full path。

C/G 草案都要求 route table 和 OpenAPI diff，这是正确方向。但审批前应把这个限定写进 design：

- local decorator duplicate 是 migration smell / governance risk。
- final full-path duplicate 才是 runtime route conflict。
- implementation gate 必须基于 prefix-expanded final route table 和 OpenAPI diff，而不是只基于 local decorator duplicate。

建议把 `P3-0.4: Generate final full route table with prefixes applied` 作为 C/G 的 shared prerequisite。

### 5. E/F 的实施顺序需要明确

`migrate-backend-singletons-to-lifecycle-di` 和 `split-backend-core-modules-with-compatibility-wrappers` 都会影响 Core 基础设施模块。

如果先做 DI，再移动 database/cache/socketio/security 文件，可能重复修改 provider/import path；如果先拆 Core，但没有 wrapper matrix，DI migration 会在不稳定 import surface 上做生命周期改造。

建议：

- F 先产出 import compatibility matrix。
- 对 database/cache/socketio/security 相关 DI batch，E 必须依赖 F 的 matrix 或等待相关 Core split batch 完成。
- E 的 tasks 中增加 “cross-check against core split wrapper matrix”。
- F 的 tasks 中增加 “identify lifecycle-owned modules that must coordinate with singleton DI migration”。

## Per-Change Review

### C: `consolidate-backend-api-domain-routers`

优点：

- 覆盖 route inventory、OpenAPI baseline、canonical router decision、compatibility shim、consumer matrix、rollback。
- 明确删除 router、prefix change、response model change、shim retirement 都需要审批。
- tasks 中要求 import smoke、OpenAPI diff、targeted backend tests、frontend/API smoke、PM2 backend startup。
- spec deltas 覆盖 api-documentation、api-integration、architecture-governance，方向合理。

需要修订：

- 明确 trading / backup 是否 deferred。
- 将 route table prerequisite 明确为 prefix-expanded final full path table。
- 将 P3 route duplicate scan 的 artifact 路径写入 Source Evidence。
- 在 tasks 中按 domain 拆出 `Blocked by`，不要让 announcement、strategy、risk 共享同一个泛化 verification gate。

建议状态：**conditional approve after scope clarification**。

### E: `migrate-backend-singletons-to-lifecycle-di`

优点：

- 正确避免了“把所有 singleton 机械改成 request-level Depends”的风险。
- 分类覆盖 stateless helper、heavy service、adapter factory、cache-backed service、connection-backed service、compatibility getter。
- 明确 lifespan/app.state、dependency override、teardown evidence。
- code-quality delta 对 dependency override 和 teardown evidence 有具体要求。

需要修订：

- 补和 F core split 的 dependency rule。
- 在 tasks 中明确第一批只允许选择一个低风险 representative candidate；不要让 21 tasks 被解释为可以并行迁移所有 singleton。
- 为 teardown evidence 明确 artifact：例如 log excerpt、test fixture、shutdown hook smoke 或 resource close assertion。

建议状态：**approvable after cross-change dependency note**。

### F: `split-backend-core-modules-with-compatibility-wrappers`

优点：

- 正确把 import compatibility matrix 放在移动前。
- 正确保留 `app.core.logger` canonical entrypoint。
- 区分 same-name package migration 和 old-module wrapper migration。
- wrapper retirement 被延后，符合 `architecture/STANDARDS.md` 的迁移收口规则。

需要修订：

- 与 E 建立共享 owner：哪些 Core modules 是 lifecycle-owned，不能只按目录移动。
- 明确 `app.core.logger` canonical path 的测试命令，例如 import smoke 覆盖 `from app.core.logger import logger`。
- tasks 中的 PM2/backend startup smoke 应给出具体命令或引用现有 smoke script。

建议状态：**approvable with orchestration matrix**。

### G: `consolidate-backend-health-endpoints`

优点：

- 正确强调 health-like endpoints 需要分类，而不是 blanket delete。
- `/health/ready` 与 `/api/health/ready` readiness compatibility 被保留为迁移决策对象。
- `/api/health/services` 作为 current services probe 的方向合理。
- OpenAPI diff、consumer matrix、monitoring compatibility、PM2 smoke 和 rollback 都进入草案。

需要修订：

- 扩展到 status taxonomy，或明确 status 由后续 proposal 处理。
- 引用 2026-05-18 route table scan 的 `GET /health` / `GET /status` 数据。
- 明确 final full route table 是 implementation gate。
- 将 `backup_recovery_secure/cleanup_old_backups.py` 这类 domain health endpoint 是否属于 health consolidation 还是 domain route ownership proposal 说清楚。

建议状态：**conditional approve after status-scope decision**。

## Issue Readiness Review

按 `docs/agents/triage-labels.md`，以下状态应保持：

| Item | Recommended label | Reason |
|---|---|---|
| 四个 OpenSpec proposals 本身 | `needs-triage` / approval review | 需要 human approval |
| C implementation issues | not `ready-for-agent` yet | trading/backup scope and full route table prerequisite unresolved |
| E first inventory issue | can become `ready-for-agent` after orchestration note | inventory/classification is independently actionable |
| E implementation batches | not `ready-for-agent` yet | depends on lifecycle classification and F matrix |
| F import compatibility matrix | can become `ready-for-agent` after approval | bounded evidence task |
| F move batches | not `ready-for-agent` yet | depends on matrix and batch selection |
| G route taxonomy issue | not `ready-for-agent` until status scope decided | health/status boundary unresolved |

## Approval Checklist

Before approving implementation, require:

- [ ] Cross-change orchestration matrix exists.
- [ ] C explicitly includes or defers trading / backup.
- [ ] G explicitly includes or defers `GET /status` taxonomy.
- [ ] C/G require prefix-expanded final route table, not only AST local decorator duplicates.
- [ ] E depends on F import compatibility matrix for shared Core modules.
- [ ] F identifies lifecycle-owned modules that must coordinate with E.
- [ ] Each tasks.md includes concrete verification commands or named scripts, not only generic “run smoke”.
- [ ] Route/OpenAPI artifact paths are named and stable.
- [ ] Follow-up GitHub issues are not marked `ready-for-agent` until their OpenSpec approval and `Blocked by` chain are resolved.

## Final Recommendation

These drafts are structurally valid and directionally sound. They are good enough to start human approval review.

They are not yet sufficient to unlock implementation. The missing piece is not more prose inside each individual proposal; it is a small cross-change orchestration layer plus scope decisions for trading/backup and status endpoints.

Once those items are added, C/E/F/G can serve as the governance backbone for Phase 3 backend route, lifecycle, Core split, and health/status remediation.
