# MyStocks Backend Audit Phase 2/3 Plan Review

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> 审核对象: `docs/reports/quality/backend-audit-phase2-summary-and-phase3-plan.md`  
> 审核日期: 2026-05-17  
> 审核方法: Matt Pocock skills 视角（`setup-matt-pocock-skills` 前置检查、`to-issues` 的 vertical slice/independently-grabbable 标准、`improve-codebase-architecture` 的 deepening opportunity 标准、`zoom-out` 的上下文校准）  
> 参考上下文: `web/backend/CONTEXT.md`、`architecture/STANDARDS.md`、`openspec/AGENTS.md`、`docs/architecture/0001-core-directory-restructure.md`、`docs/architecture/0002-api-flat-to-package-migration.md`、`docs/architecture/0003-singleton-to-di-migration.md`

## 总体结论

这份文档可以作为 Phase 2 总结和 Phase 3 初稿继续使用，但还不适合作为“直接创建 GitHub Issues 并开工”的输入。

主要原因不是方向错误，而是 Phase 3 的 issue 拆分还没有达到 Matt Pocock `to-issues` 技能要求的 independently-grabbable vertical slice 标准：若干 issue 依赖关系没有显式写出，OpenSpec 审批边界偏窄，验收标准过于通用，且部分事实引用需要用当前代码和可复现扫描重新定基线。

建议先补一个 Phase 2.5“事实基线与 issue readiness”步骤，再批量创建 Phase 3 issues。

## 关键发现

### 1. Blocker: Matt Pocock skills 的本地前置配置缺失

本次检查没有找到以下本地配置文件：

- `docs/agents/issue-tracker.md`
- `docs/agents/triage-labels.md`
- `docs/agents/domain.md`
- 根目录 `CLAUDE.md` 或 `AGENTS.md` 中的 `## Agent skills` block

`setup-matt-pocock-skills` 明确要求在使用 `to-issues`、`triage`、`improve-codebase-architecture`、`zoom-out` 等技能前，先让技能知道 issue tracker、triage label vocabulary 和 domain docs 布局。当前计划第 125-129 行的目标是“转 GitHub Issues”，但第 181-185 行只给了 `tech-debt, audit-finding` 两个标签，没有说明 canonical triage labels（例如 `needs-triage`、`ready-for-agent`）如何映射，也没有说明 issue tracker 事实来源。

影响:

- 创建出的 issues 可能不能被后续 `triage` / AFK agent workflow 正确消费。
- “ready-for-agent” 的状态无法被一致判断。
- 审核计划声称使用 Matt Pocock skills，但技能运行所需的 repo-local contract 不完整。

建议:

- 在 Phase 3 前新增一个阻塞任务：`audit(P3-0): 建立 Matt Pocock skills issue tracker / triage / domain 配置`。
- 如果项目决定使用 GitHub Issues，则落盘 `docs/agents/issue-tracker.md`、`docs/agents/triage-labels.md`、`docs/agents/domain.md`，并在用户确认后选择创建或更新根目录 agent instruction 文件。
- Phase 3 issue template 增加 `Triage label`、`Ready-for-agent criteria`、`Blocked by` 字段。

### 2. Blocker: “第一批可立即执行”包含隐含依赖，不满足 independently-grabbable

第 133-141 行把 5 个 issue 标为“立即可修复（无 OpenSpec 依赖）”，但至少有 3 个并不应立即并行开工：

- Issue 1 `announcement canonical 路径并修复双注册` 先需要 canonical path 决策。目标文件第 100 行也承认 `/api/announcement/*` 与 `/api/v1/announcement/*` 消费关系需要确认。
- Issue 4 `删除已确认的 4 个 _new.py 文件中的冗余副本` 依赖 Issue 3 的“重扫工作树，更新残留文件清册”。
- Issue 5 `monitoring_old 无活跃引用后删除` 同样依赖当前 scan 与双判定。

这与 `to-issues` 的 vertical slice 要求冲突。一个可抓取 issue 应该能让执行者在没有额外口头上下文的情况下知道输入、边界、前置条件、验收命令和阻塞项。

建议改法:

- 把 Issue 1 拆成两个 issue：
  - `audit(D-1a): 产出 announcement canonical route decision record`
  - `audit(D-1b): 按已审批 canonical route 修复双注册`
- Issue 4、Issue 5 明确 `Blocked by: Issue 3`，且只能在残留清册完成双判定后进入 `ready-for-agent`。
- Issue 表格增加 `Blocked by`、`OpenSpec required?`、`GitNexus target`、`Verification command` 四列。

### 3. High: OpenSpec 审批边界偏窄

文档第 158 行只把第三批标为“需 OpenSpec 审批”，但前文第 108-121 行的深化机会里已经写明：

- D-2 `Core exception ×3 → 1 canonical` 的前置条件是 OpenSpec。
- D-4 `Core cache 根级文件移入 cache/ 子目录` 至少需要 GitNexus impact；从 `architecture/STANDARDS.md` 的迁移收口规则看，也属于改变 canonical 归属的结构调整。
- D-5/D-10/D-11 之间有明显架构依赖链。

当前第 155-156 行把 D-4、D-2 放进“第二批低风险改进”，容易绕过 proposal-first gate。虽然第二批不是最高风险，但它们会改变 imports、canonical module ownership、兼容 wrapper 或 re-export 策略，不应只按“低风险 issue”处理。

建议:

- 将 D-2、D-4、D-5、D-8、D-9、D-10、D-11、D-12、schema 双目录合并统一纳入 OpenSpec 分类判断。
- 对每个结构迁移 issue 增加 `Proposal` 字段：
  - `not required`: 明确说明原因，例如纯文档或单点 bugfix。
  - `required`: 指向 `openspec/changes/<change-id>/proposal.md`。
  - `pending decision`: 不能进入 implementation。
- 第 206-211 行的执行约束应改为“OpenSpec proposal 批准前不得进入实现”，而不是只约束第三批。

### 4. High: 事实基线需要可复现扫描，当前数字存在口径漂移风险

目标文档第 60-100 行给出若干核心统计：

- Core: 75 个 Python 文件、26,429 行。
- API: 64 个 flat 文件、20 个 package 目录、10 个重叠域。
- Singleton: 118 处。

本次使用当前工作树做了快速校验，结论是方向基本一致，但口径需要固定：

- `web/backend/app/api` 当前直接文件系统粗扫为 79 个 flat `.py` 文件、18 个带 `__init__.py` 的 package 目录、10 个 overlap 域。
- `web/backend/app/core` 当前粗扫为 77 个 `.py` 文件、约 26,577 行。
- 当前工作树存在 4 个 `*_new.py` 文件：
  - `web/backend/app/api/data/data_api_new.py`
  - `web/backend/app/services/data_adapter_new.py`
  - `web/backend/app/services/data_api_new.py`
  - `web/backend/app/services/risk_management_new.py`
- 当前工作树存在 `web/backend/app/api/monitoring_old/`，非 docs 引用快速扫为 0。

这些差异未必说明目标文档错误，也可能是扫描脚本的包含/排除规则不同，或者工作树在 Phase 2 后继续变化。但 Phase 3 issues 必须绑定可复现事实基线，否则执行者会争论“到底删哪几个、迁哪个路径、验收哪个数”。

建议:

- 在 Phase 3 前新增 `Phase 2.5: fact baseline freeze`。
- 每个统计项必须记录：
  - 扫描日期和 git branch。
  - 扫描脚本或命令。
  - include/exclude 规则，例如是否排除 tests、legacy、worktrees、generated files。
  - 结果文件路径，例如 `docs/reports/quality/backend-audit-phase3-fact-baseline-2026-05-17.md`。
- Issue 的 `当前状态` 字段引用 baseline 文件，不手写孤立数字。

### 5. High: announcement 风险缓解项引用路径与验证策略需要修正

当前代码仍能确认 announcement 双注册风险：

- `web/backend/app/router_registry.py:78` 通过 `VERSION_MAPPING` 注册 `announcement.router`。
- `web/backend/app/router_registry.py:96` 又以 `prefix="/api"` 直接注册 `announcement.router`。
- `web/backend/app/api/VERSION_MAPPING.py:123-126` 将 `announcement` 前缀定义为 `/api/v1/announcement`。

但目标文档第 219 行的缓解措施写的是检查 `versionNegotiationPolicy.ts` 是否将 v1 路径重定向到非 v1 路径。本次校验发现当前文件路径是 `web/frontend/src/services/versionNegotiationPolicy.ts`，不是 `web/frontend/src/utils/versionNegotiationPolicy.ts`；并且该文件没有发现 announcement 专项映射。

建议:

- 风险项改为检查三个事实源：
  - 后端实际 route table：`/api/announcement/*` 与 `/api/v1/announcement/*` 是否同时存在。
  - 前端调用引用：`web/frontend/src/**` 中的 `/announcement`、`/api/announcement`、`/api/v1/announcement`。
  - 契约/测试引用：`web/backend/tests/**`、`tests/**` 中 announcement 路由断言。
- Issue 1 的验收标准增加：
  - OpenAPI route diff 只包含预期变化。
  - 前端 API client 与测试引用同步更新。
  - 兼容路径若保留，必须有明确退役条件和期限。

### 6. High: Singleton “全为 per-app，风险较低”的判断过于粗

第 90 行写“所有 118 个 singleton 均为 per-app 生命周期，迁移到 FastAPI `Depends()` 风险较低”。这个结论需要更谨慎。

问题点:

- `get_xxx()` 命名并不等于 singleton，粗略代码扫描会混入大量 route handler / helper getter。
- `_x = None` 也只是 lazy-init 模式 proxy，不能单独证明生命周期、线程安全、连接池语义或 cleanup 语义。
- ADR-0003 的 Phase 1 示例把 lazy singleton 改成每次 `DatabaseService()`，这可能从“进程级缓存实例”变成“每次依赖解析创建实例”，并不天然等价于 per-app lifecycle。

建议:

- D-10/D-11 前先创建 `audit(E-0): singleton lifecycle inventory`：
  - 按 `business service`、`infrastructure client`、`connection pool`、`cache`、`logger/tracer`、`pure helper` 分类。
  - 明确每类迁移目标：`Depends` factory、`app.state`/lifespan、`lru_cache` provider、保留 module singleton。
  - 为每类列出 teardown/cleanup 要求。
- 在 ADR-0003 或后续 OpenSpec design 中补充“per-app lifecycle 如何保持”的实现决策。
- 不建议把 D-10/D-11 issue 标记为中等风险且只用 8h/16h 估算，除非已经有 lifecycle inventory 和 dependency override 测试样板。

### 7. Medium: Issue 模板过于通用，不能驱动 AFK 执行

第 179-204 行的模板是一个不错的起点，但对真正执行还不够。当前模板没有强制写：

- `Blocked by`
- `Non-goals`
- `Files likely touched`
- `OpenSpec / ADR reference`
- `GitNexus impact target`
- `Route diff / import diff / OpenAPI diff`
- `Rollback plan`
- `Ready-for-agent checklist`

建议模板升级为：

```markdown
## Source
[审计子文档 / D 编号 / baseline 行号]

## Current State
[当前代码事实，引用 baseline 文件和具体路径]

## Target State
[canonical 状态，不含模糊词]

## Scope
- In:
- Out:

## Blocked By
- [issue id / proposal id / none]

## OpenSpec
- required: yes/no
- proposal: [path or pending]

## Implementation Notes
- likely files:
- GitNexus impact target:
- compatibility rule:

## Acceptance Criteria
- [ ] fact baseline updated if counts changed
- [ ] route/import/OpenAPI diff reviewed where relevant
- [ ] relevant tests pass
- [ ] `CONTEXT.md` / `FUNCTION_TREE.md` updated where ownership or canonical path changed
- [ ] `gitnexus_detect_changes(scope: staged)` reviewed before commit
```

### 8. Medium: 批次规划缺少依赖图

目标文件已经隐含了依赖，例如：

- D-10 依赖 D-5。
- D-11 依赖 D-10。
- D-12 依赖健康端点 route table 重测。
- D-8/D-9 依赖 canonical route 决策与 OpenSpec。
- D-2/D-4/D-5 依赖 GitNexus impact 和 import compatibility strategy。

但第 133-177 行的 issue table 只按批次列出，没有把依赖显式编码。这会让多个 worker 并行时踩到同一片架构表面。

建议:

- 在 Phase 3 计划中增加一张 dependency table。
- 将 issues 分为：
  - `P3-0 Readiness`: Matt Pocock setup、fact baseline、route table scan。
  - `P3-1 Decision`: announcement、strategy、risk、schema、singleton lifecycle。
  - `P3-2 Safe closure`: 已有决策且影响面小的 flat/package 收口。
  - `P3-3 Structural migrations`: Core / DI / health consolidation，全部走 OpenSpec 或明确豁免。

### 9. Medium: 估算粒度偏乐观

第 147-156 行把多个 flat→package 收口域估为 3h，把 Core exception 合并估为 4h。对“写代码”可能够，但对当前项目规则要求的完整验收不一定够：

- GitNexus impact。
- route table / OpenAPI diff。
- 测试引用更新。
- `CONTEXT.md` 或治理文档更新。
- staged scope detect changes。

建议:

- 将估算拆成 `analysis`、`implementation`、`verification` 三段。
- 对需要 OpenSpec 的任务使用“审批 lead time”和“实现工时”两个字段。
- 低风险任务也至少预留验证时间，避免 issue 实际关闭时验收不足。

## 建议的 Phase 3 修订骨架

```markdown
## Phase 2.5: Readiness and Fact Baseline

| # | Task | Output | Blocks |
|---|------|--------|--------|
| P3-0.1 | Setup Matt Pocock skills repo contract | docs/agents/*.md + agent skills block decision | all issue publishing |
| P3-0.2 | Freeze backend audit fact baseline | docs/reports/quality/backend-audit-phase3-fact-baseline-YYYY-MM-DD.md | all implementation issues |
| P3-0.3 | Generate route table / OpenAPI diff baseline | route table artifact | D-1, D-6, D-7, D-8, D-9, D-12 |

## Phase 3A: Decision Issues

| # | Issue | OpenSpec | Blocked by |
|---|-------|----------|------------|
| D-1a | announcement canonical route decision | maybe | P3-0.2, P3-0.3 |
| D-8a | strategy canonical route decision | yes | P3-0.3 |
| D-9a | risk canonical route decision | yes | P3-0.3 |
| E-0 | singleton lifecycle inventory | yes/design | P3-0.2 |

## Phase 3B: Implementation Issues

Only issues with resolved decisions and explicit acceptance criteria enter `ready-for-agent`.
```

## 结论

保留当前文档的 Phase 2 总结部分；Phase 3 部分建议先修订后再创建 GitHub Issues。

最小修订要求:

1. 补齐 Matt Pocock skills 的 issue tracker / labels / domain docs 本地配置或明确豁免。
2. 新增 Phase 2.5 当前事实基线，并让所有 issue 引用它。
3. 为每个 issue 补 `Blocked by`、OpenSpec 状态、GitNexus impact target、验证命令。
4. 把 D-2/D-4/D-5/D-8/D-9/D-10/D-11/D-12 从“普通低风险任务”中剥离出来，按 proposal-first gate 处理。
5. 修正 announcement 风险验证路径：使用 `web/backend/app/router_registry.py`、`web/backend/app/api/VERSION_MAPPING.py`、`web/frontend/src/services/versionNegotiationPolicy.ts` 和前后端引用清单作为事实源。

