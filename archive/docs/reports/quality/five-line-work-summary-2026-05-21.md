# 项目5条线工作总结（合并版）

日期：2026-05-21

---

## 第一条线：codebase map 有效性判定及治理口径更新

### 一、已完成的工作

已按管家文档完成有效性判定，并落盘新审核报告：docs/reports/quality/codebase-map-task-completion-validity-2026-05-21.md。

核心结论：本条线的 sequence-backend-architecture-unblocks runtime unblock 在当前 clean HEAD f97f2eb57 下有效，复测结果为 app.main routes=548、health collect-only 112 tests collected、OpenAPI paths=500 / operation_ids=536 / duplicate_operation_ids=0。但这只证明 import / collect-only / minimal OpenAPI smoke 层面有效，不等于 PM2/backend runtime gate、Core Batch 2、endpoint retirement 或 OpenSpec archive 已闭环。

同步更新了相关治理口径，避免旧的 asynccontextmanager / dirty-worktree 结论继续误导后续任务：

- docs/reports/quality/backend-openspec-issue83-runtime-triage-2026-05-19.md：标记为历史 triage，当前 runtime 状态由新报告接管。
- docs/reports/quality/backend-core-split-governance-reconciliation-2026-05-19.md：明确 Core Batch 2 仍阻塞，runtime unblock 通过不自动授权 Batch 2。
- docs/reports/quality/backend-sequence-unblocks-preimplementation-evidence-2026-05-20.md：补充 freshness note，作为 Task 1.x 历史证据使用。
- docs/reports/quality/codebase-map-freshness-2026-05-19.md：加入 2026-05-21 当前有效性报告。
- openspec/changes/split-backend-core-modules-with-compatibility-wrappers/tasks.md：更新 Core split runtime evidence 说明，仍不勾选当前 checkout 的 4.3/4.4/4.5。

验证已完成：git diff --check 通过，markdown governance gate 5 files / 0 errors，openspec validate sequence-backend-architecture-unblocks --strict 通过，openspec validate split-backend-core-modules-with-compatibility-wrappers --strict 通过。当前结论也已写入 Graphiti memory。

### 二、提交信息

提交：e74bf92f1 docs(governance): record codebase map validity review

本次提交只包含 6 个已跟踪治理/OpenSpec 文件：

- 新增 docs/reports/quality/codebase-map-task-completion-validity-2026-05-21.md
- 更新 runtime triage、Core split reconciliation、preimplementation evidence、freshness 记录
- 更新 split-backend-core-modules-with-compatibility-wrappers/tasks.md 的 runtime evidence 口径

提交前验证结果：

- GitNexus staged detect：low，affected_count=0
- git diff --cached --check：无输出
- markdown governance gate：5 checked / 0 errors
- openspec validate sequence-backend-architecture-unblocks --strict：通过
- openspec validate split-backend-core-modules-with-compatibility-wrappers --strict：通过

.planning/* 被 .gitignore 忽略，未强制加入提交。当前提交目标路径复查为干净。

### 三、下一步工作计划

按报告里的顺序推进：先做 sequence-backend-architecture-unblocks 完成证据采纳和人工 review，再决定是否 archive；如需要完整运行态闭环，再单独跑 PM2/backend runtime gate；Core Batch 2 继续冻结，必须等 Task 3.2、#83 evidence、issue15、archive readiness 都有明确 accepted disposition 后再开。

### 四、交接文档

生成交接文档：/tmp/handoff-cGDTT5.md

内容覆盖：

- 本条线已完成工作：runtime unblock、schema shim closure、route/OpenAPI/probe refresh、service seam proposal path、有效性复核、提交 e74bf92f1
- 当前有效状态：sequence-backend-architecture-unblocks runtime 证据在 current HEAD 有效，但 archive、PM2/backend runtime gate、Core Batch 2 仍是独立门禁
- 下一步计划：OpenSpec archive 决策、PM2/backend gate 决策、route/OpenAPI governance follow-up、Core split blocked gate、service seam proposal-only 路线
- 接手注意事项：不要 broad-stage、不要强制加入 .planning/*、不要重开已过期 data-lineage import blocker、不要把 runtime smoke 误当成 Core Batch 2 授权
- 建议下一位 agent 使用的 skills 和首批命令

该 handoff 按 skill 要求写入 /tmp 临时 Markdown 文件；本次没有修改仓库文件，也没有新增提交。

---

## 第二条线：codebase map OpenSpec 执行计划推进

### 一、已完成的工作

已继续推进本条线的执行计划，未回填 review 意见，也没有修改 backend 源码、GitHub issue、label 或 OpenSpec proposal。

本轮完成的实际工作：

- 复核 Wave 1 状态：
  - #80 仍为 OPEN / ready-for-human
  - #83 仍为 OPEN / ready-for-agent
  - #83 仍限定为 C/E/F evidence-package work
  - issue15 仍保持 unpublished，并继续受 BLOCKED_BY_TODO: shared evidence package. 阻塞
  - 当前 checkout 6530c88f3 不包含远端 bbb399071
  - 当前 app.main import 仍失败在 web/backend/app/api/data_lineage.py:43 的裸 _data_lineage_responses import，因此继续按 stale checkout / implementation-lane blocker 处理，不在 #83 下修代码

- 刷新 Wave 2 / Wave 3 已落盘报告的 freshness 元数据：
  - docs/reports/quality/backend-schema-dual-directory-closure-2026-05-19.md:7
  - docs/reports/quality/backend-api-flat-package-closure-records-2026-05-19.md:7
  - docs/reports/quality/backend-singleton-lifecycle-routing-matrix-2026-05-19.md:7
  - docs/reports/quality/backend-external-evidence-alignment-2026-05-19.md:11
  - docs/reports/quality/backend-error-contract-completion-verification-2026-05-19.md:7
  - docs/reports/quality/backend-csrf-composition-root-decision-2026-05-19.md:7
  - docs/reports/quality/codebase-map-freshness-2026-05-19.md:7
  - .planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md:744

- 重新生成并写入当前 HEAD 的关键静态计数：
  - schema/: 2 个 Python 文件；from app.schema 为 15 个 tracked Python 文件 / 15 references
  - schemas/: 16 个 Python 文件；from app.schemas 为 76 个 tracked Python 文件 / 101 references
  - web/backend/app/services: 152 个 service .py 文件；116 个 broad singleton/getter/spec-loading candidate files
  - P3-C5 error-contract 当前 HEAD 扫描：web/backend/app/api 下 218 个 Python 文件，五个 fixed-field bucket 全部为 0

验证结果：

- git diff --check：通过，无输出
- scoped markdown governance gate：8 files checked，0 errors
- Wave 1 OpenSpec gate：openspec validate split-backend-core-modules-with-compatibility-wrappers --strict valid；PostHog flush 仍是非阻塞网络 warning

当前边界仍然是：

- Task 6 route/OpenAPI runtime diff 不能继续，因为 app.main 当前还不能 clean import
- Task 9 / Core helper Batch 2 仍不能启动，因为 Task 2 结论是 Batch 2 blocked
- _data_lineage_responses import 修复需要单独 implementation lane 和 GitNexus impact/context，不应混入 #83 evidence-only 工作

本轮实际变更为 8 个文档文件，86 insertions / 20 deletions，没有 backend 代码改动。

### 二、提交信息

已确认本条线已完成的 5 个目标文档变更已经提交在：9dafa16467e34d660bad6d76d29f3997d4e780f1 docs(codebase): refresh openspec execution plan status

当前 HEAD 是 80b8389ed Record miniQMT forward receive result，并且包含上述提交。目标文件现在无未提交 diff，staged 区也是空的，未创建空提交。

本次已提交的文件是：

- docs/reports/quality/backend-csrf-composition-root-decision-2026-05-19.md
- docs/reports/quality/backend-error-contract-completion-verification-2026-05-19.md
- docs/reports/quality/backend-external-evidence-alignment-2026-05-19.md
- docs/reports/quality/backend-schema-dual-directory-closure-2026-05-19.md
- docs/reports/quality/backend-singleton-lifecycle-routing-matrix-2026-05-19.md

提交前已完成的检查：

- git diff --check：通过
- scoped markdown governance gate：5 files checked，0 errors
- GitNexus staged scope：docs-only，无符号变更，risk none

注意：工作区仍有大量其它未提交变更，但不属于本条线这次提交范围，未 stage 或提交它们。

### 三、下一步工作计划

先从 #92 和 task tree 继续，再 reconcile Core split task state，然后处理 route/OpenAPI、schema shim、service seam proposal。

### 四、交接文档

已生成交接文档：docs/reports/quality/backend-codebase-map-openspec-line-handoff-2026-05-21.md

文档内容覆盖了本条线的当前交接重点：

- 当前分支、HEAD、远端状态、dirty worktree 风险
- #80、#83、#92 的最新 GitHub 状态
- 旧 issue15 draft 与 live issue #92 的关系
- 已完成的 publication / evidence / runtime unblock / static decision records
- 关键提交与关键 artifact 路径
- 当前不能做的事项和必须保留的边界
- 下一步建议执行顺序：先从 #92 和 task tree 继续，再 reconcile Core split task state，然后处理 route/OpenAPI、schema shim、service seam proposal
- 推荐给下一条线使用的技能和验证命令

已完成校验：

- git diff --check -- docs/reports/quality/backend-codebase-map-openspec-line-handoff-2026-05-21.md：通过
- markdown governance gate：checked_files=1，errors=0
- 文档中重点引用的 5 个当前后续 artifact 路径均确认存在

该 handoff 文档当前是新建未提交文件，方便审核。

---

## 第三条线：P3-C5 异常整合及大文件拆分

### 一、已完成的工作

- P3-C5 异常迁移：已完成（app/api/ 扫描归零）
- 21 个大文件拆分：已完成（所有文件 ≤700 行）
- 完成报告：docs/reports/P3-C5-exception-consolidation-completion-report.md

工作区剩余的 950+ 未提交文件属于其他工作线，非本条线内容。

### 二、提交信息

已提交 36b1f52da — P3-C5 companion 导入修复 + 完成报告。

本条线提交记录：

| Commit | 内容 |
|--------|------|
| ed723bb22 | 完成 system_health.py 异常迁移 |
| ca4e80e25 | 拆分 8 个大文件（Batch 2） |
| 93baaa775 | 拆分 6 个大文件（Batch 3） |
| 36b1f52da | 修复 companion imports + 提交完成报告 |

P3-C5 工作线已全部提交完毕，无遗漏。

### 三、下一步工作计划

- 266 条历史路由的 UnifiedResponse 契约守卫（独立任务）
- 按需执行计划中的其他任务（如 Task 10 验证）

### 四、交接文档

交接文档已生成：docs/reports/P3-C5-HANDOFF.md

核心内容：

- 已完成：异常迁移 4 项扫描归零 + 21 个大文件拆分（12 次提交）
- 下一步：UnifiedResponse 契约守卫（266 路由）、执行计划 Task 10 验证
- 验证命令：三条可复现的检查命令

---

## 第四条线：data lineage 修复及 route/OpenAPI evidence 收口

### 一、已完成的工作

已继续推进本条线，并完成两个实质性收口点。

**1. 修复 data_lineage runtime import blocker，并提交相关文件：**

修复前，现有回归测试已经红灯：web/backend/tests/test_data_lineage_regressions.py 在 importlib.import_module("app.api.data_lineage") 阶段失败，先是 ModuleNotFoundError: _data_lineage_responses，随后暴露 companion 文件缺失 Optional / BaseModel 等依赖。修复后测试转绿。

- web/backend/app/api/data_lineage.py:41：把裸导入改为包内相对导入，并显式从 companion 文件导入已抽取的模型/adapter。
- web/backend/app/api/_data_lineage_responses.py:3：补齐 companion 文件自身需要的 asynccontextmanager、datetime、List、Optional、BaseModel、Field。
- docs/reports/quality/backend-openspec-issue83-runtime-triage-2026-05-19.md:1：记录这是 #83 evidence scope 之外的独立 implementation-lane fix。

**2. 解除 blocker 后继续完成 Task 6 的 runtime route/OpenAPI evidence，并提交相关文件：**

本地生成了 ignored evidence artifact：.planning/codebase/generated/backend-route-openapi-diff-2026-05-21.json，它按 .gitignore 不提交，但报告里记录了摘要和路径。

- docs/reports/quality/backend-route-openapi-diff-2026-05-19.md:1：新增当前 route/OpenAPI diff 报告。
- docs/reports/quality/backend-api-flat-package-closure-records-2026-05-19.md:1：从 "runtime diff deferred" 更新为 "runtime evidence attached"。

**验证结果**

代码修复验证：

- pytest -o addopts= web/backend/tests/test_data_lineage_regressions.py -q --no-cov：最终结果 1 passed
- env PYTHONPATH=web/backend python -c "from app.main import app; print(len(app.routes))"：最终结果 548
- pytest -o addopts= web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov：最终结果 112 tests collected
- pytest -o addopts= web/backend/tests/test_health_route_conflicts.py -q --no-cov：最终结果 112 passed
- python -m py_compile web/backend/app/api/data_lineage.py web/backend/app/api/_data_lineage_responses.py：exit=0
- ruff check web/backend/app/api/data_lineage.py web/backend/app/api/_data_lineage_responses.py web/backend/tests/test_data_lineage_regressions.py：All checks passed!

文档/evidence 验证：

- git diff --check：通过
- python scripts/compliance/markdown_governance_gate.py ...：通过，errors=0
- openspec validate split-backend-core-modules-with-compatibility-wrappers --strict：通过

GitNexus：

- 修改前 impact：data_lineage.py LOW，_data_lineage_responses.py LOW
- 代码提交前 staged detect：risk medium，唯一受影响流程为 Record_lineage -> Acquire_connection
- 文档提交前 staged detect：risk low
- 两次提交后均已运行 gitnexus analyze，最终索引刷新成功：96,568 nodes | 233,763 edges | 5295 clusters | 300 flows

**Route/OpenAPI 当前结论**

当前 f97f2eb57 runtime evidence summary：

- runtime routes：548
- runtime unique paths：511
- schema-visible routes：536
- hidden runtime routes：12
- endpoint modules：98
- OpenAPI paths：500
- OpenAPI operations：536
- duplicate operationIds：0
- OpenAPI warnings：0
- vs 2026-05-20 route/OpenAPI artifact：runtime route paths：+0 / -0；OpenAPI paths：+0 / -0

仍存在一个已知 runtime duplicate path/method：GET /metrics（hidden：app.main.prometheus_metrics；visible：app.api.prometheus_exporter.metrics），报告里已明确把它归入 control-plane taxonomy，不作为 OpenAPI duplicate operationId，也不授权删除。

**当前注意点**

当前 HEAD 是：86849805e docs(codebase): attach route openapi runtime diff

但工作树仍然是大规模 dirty worktree。本轮提交相关的代码文件和 Task 6 文档文件已经 clean；未把以下后续/并发文档改动纳入提交：

- docs/reports/quality/backend-openspec-issue83-runtime-triage-2026-05-19.md 仍有未提交 diff
- docs/superpowers/plans/2026-05-19-codebase-map-openspec-execution-plan.md 仍有未提交 diff
- docs/reports/quality/codebase-map-task-completion-validity-2026-05-21.md 是 untracked

### 二、提交信息

1. 提交：f97f2eb57 fix(api): repair data lineage companion imports（修复 data_lineage runtime import blocker）
2. 提交：86849805e docs(codebase): attach route openapi runtime diff（完成 Task 6 的 runtime route/OpenAPI evidence）

提交前验证：

- git diff --check：通过
- markdown_governance_gate.py：通过，相关 6 个 Markdown 文件 errors=0
- openspec validate split-backend-core-modules-with-compatibility-wrappers --strict：通过
- GitNexus staged detect：low risk，无 affected processes
- 提交后已运行 gitnexus analyze，索引刷新成功：96,555 nodes | 233,758 edges | 5282 clusters | 300 flows

当前相关路径已 clean，暂存区为空。工作树里仍有大量既有非本条线 dirty/untracked 内容，未把它们带入这次提交。

### 三、下一步工作计划

继续做 "source-state adoption / completion validity" 收口：先审核并决定未提交文档改动是否属于本条线，然后再推进 Core Batch 2、route governance 或 archive gate。

### 四、交接文档

已生成交接文档：/tmp/handoff-8EAtFc.md

文档内容覆盖了：

- 当前分支、HEAD、工作线目的
- 建议下一位 agent 使用的技能和工作方式
- GitHub issue 当前状态：#75/#76/#77/#83 已关闭，#78/#79/#80 仍开
- 本条线已完成的主要工作与对应提交：
  - f97f2eb57 runtime import chain unblock
  - 86849805e route/OpenAPI diff evidence
  - e74bf92f1 validity review
  - 36b1f52da P3-C5 completion reports
  - 9dafa1646 / 93b40f80a execution计划与 evidence record 刷新
  - 80b8389ed miniQMT forward receive result
- 当前 OpenSpec 状态
- dirty worktree / staging 注意事项
- 下一步建议计划：
  - completion evidence adoption
  - #80 / issue15 publication path
  - Core split Batch 2 前置治理
  - API flat-package consumer parity
  - error contract follow-up lane
  - #78/#79 lifecycle DI triage
  - PM2/runtime gate 的边界
- 关键参考文件路径与最后已知验证结果

基本检查：文档 309 行，未命中 governance gate 的禁用歧义短语。

---

## 第五条线：miniQMT 证据对齐及状态同步

### 一、已完成的工作

已继续并完成本条线当前收口，核心更新是把本条线从"validated-forward 本地生成、待 miniQMT validator / preview / apply"推进到当前工作区事实：

- MyStocks raw/candidate mystocks_dry_run 已完成并被 miniQMT 接受。
- MyStocks validated-forward mystocks_dry_run 已生成，并已通过 miniQMT validator / preview / apply。
- miniQMT manual promote to validated 已完成。
- miniQMT manual promote to authoritative-ready 已于 2026-05-20 北京时间完成。
- 最终 authoritative 仍保留为 miniQMT owner/operator 人工审批 gate。
- 仍不授权 source cutover、Quantix ClickHouse writes、backend promotion 或 production application。

更新的主要文件：

- docs/reports/evidence/miniqmt/2026-05-19-mystocks-controlled-evidence-summary-for-review.md:1：新增并入库本条线总结，状态更新为 Updated for review。
- docs/reports/evidence/miniqmt/2026-05-18-external-followups.md:17：同步 completed baseline、follow-up tracks、下一步 gate。
- docs/reports/evidence/miniqmt/README.md:15：更新 artifact index 和 downstream live chain。
- docs/reports/quality/backend-external-evidence-alignment-2026-05-19.md:1：记录 external miniQMT evidence alignment，明确不授权后端执行或切源。
- docs/reports/quality/codebase-map-freshness-2026-05-19.md:1：更新 freshness metadata 和当前 evidence 状态。
- docs/superpowers/plans/2026-05-19-codebase-map-openspec-execution-plan.md:436：Task 8 的 8.1 / 8.2 / 8.3 已标记完成，并同步最新状态。
- .planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md:392：加入 external miniQMT controlled evidence 行，并更新附录证据索引。
- openspec/changes/add-miniqmt-market-data-controlled-evidence-consumer/tasks.md:78：更新 7.13 / 8 的外部 follow-up 状态。

验证已通过：

- git diff --check
- python scripts/compliance/markdown_governance_gate.py ...，8 个文件通过，0 errors
- openspec validate add-miniqmt-market-data-controlled-evidence-consumer --strict
- pre-commit hooks：markdown governance、directory governance、GitNexus workflow gate 均通过
- 本次无 code-like staged files，因此不需要 GitNexus staged code impact evidence

当前这些目标文件提交后是干净的。

此外，已提交本条线已完成工作相关的 2 个文件，没有碰其它工作区脏改：

- docs/reports/evidence/miniqmt/2026-05-18-mystocks-dry-run-closeout.md:75：同步 closeout：validated-forward 已被 miniQMT 接受，authoritative-ready 已完成，剩余为最终 authoritative owner/operator gate。
- docs/reports/evidence/miniqmt/2026-05-19-mystocks-forward-evidence-receive-result.md:1：新增 receive-result 记录：MyStocks validated-forward evidence 在 miniQMT 侧 validator / preview / apply 通过，manual promote to validated 与 authoritative-ready 完成，最终 authoritative 仍需人工审批和 rollback/fallback readiness。

提交前验证已通过：

- git diff --check
- python scripts/compliance/markdown_governance_gate.py ...，2 个文件通过，0 errors
- openspec validate add-miniqmt-market-data-controlled-evidence-consumer --strict
- GitNexus pre-commit gate：无 staged code-like files

这两个目标文件提交后已干净。

### 二、提交信息

1. 提交：7b097fffd Record miniQMT authoritative-ready evidence alignment（文档、证据索引和计划状态同步，无业务逻辑修改）
2. 提交：80b8389ed Record miniQMT forward receive result（提交 2 个和 miniQMT controlled evidence 相关的文件）

### 三、下一步工作计划

等待 miniQMT owner/operator 完成最终 authoritative 人工审批，以及 rollback/fallback readiness 准备；暂不推进 source cutover、Quantix ClickHouse writes、backend promotion 或 production application。

### 四、交接文档

已生成交接文档并完成自检：/tmp/mystocks-miniqmt-handoff-finevm.md

文档内容覆盖了这条线的完成事实、MyStocks / miniQMT 边界、raw/candidate 与 validated-forward 两条 evidence 的状态、当前三条硬规则、后续计划、不要再做的事项、工作区注意事项、建议下一位接手者使用的检查方式，以及核心实现和证据文件索引。

自检结果：227 行，必要章节和关键 identity/hash 均已包含。

这份文件当前保存在 /tmp，没有纳入仓库提交；前面已提交的本条线最新仓库提交仍是 80b8389ed Record miniQMT forward receive result。
