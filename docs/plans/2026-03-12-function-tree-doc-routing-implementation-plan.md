# Function Tree Doc Routing Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 `docs/FUNCTION_TREE.md` 升级为业务能力总线，并补齐 AI 快速路由入口、功能管理维护规则和 PR 模板对齐字段。

**Architecture:** 以 `FUNCTION_TREE` 为中心，新增 `docs/guides/AI_QUICK_START.md` 负责按任务类型路由，`docs/INDEX.md` 负责推荐阅读顺序，`docs/guides/FEATURE_MANAGEMENT_WORKFLOW.md` 负责维护和评审闭环，`.github/pull_request_template.md` 负责将功能域映射要求带入交付过程。

**Tech Stack:** Markdown, repository docs, shell verification

---

### Task 1: 落地设计文档与实施计划

**Files:**
- Create: `docs/plans/2026-03-12-function-tree-doc-routing-design.md`
- Create: `docs/plans/2026-03-12-function-tree-doc-routing-implementation-plan.md`

**Step 1: 写入设计文档**

记录目标、信息架构、入口层和维护规则。

**Step 2: 写入实施计划**

将本次修改拆成独立文档任务，列出待修改文件。

**Step 3: 自检**

Run: `sed -n '1,220p' docs/plans/2026-03-12-function-tree-doc-routing-design.md`

Expected: 文档存在且包含目标、决策、验收标准。

### Task 2: 新增 AI 快速路由文档

**Files:**
- Create: `docs/guides/AI_QUICK_START.md`

**Step 1: 写入仓库定位与必读门禁**

说明本仓库是演进中的工程仓库，明确 `STANDARDS`、OpenSpec、多 CLI 治理的优先级。

**Step 2: 写入按任务类型路由**

覆盖方案/规划、新功能、Bug 修复、Code Review、前端、后端/API、运维排障。

**Step 3: 写入最小读取路径和文档优先级**

保证 AI 和开发者能在最少跳转下定位目标功能域。

**Step 4: 自检**

Run: `sed -n '1,260p' docs/guides/AI_QUICK_START.md`

Expected: 存在任务路由、最小读取路径、文档优先级三部分。

### Task 3: 升级 FUNCTION_TREE 为业务能力总线

**Files:**
- Modify: `docs/FUNCTION_TREE.md`

**Step 1: 在文档顶部增加使用说明**

加入对 `AI_QUICK_START.md` 的引用，说明先按任务类型选路，再按功能域下钻。

**Step 2: 为 10 个一级功能域补充统一的 `领域入口` 表**

每个功能域统一写入：

- 规范入口
- API/契约入口
- 前端/交互入口
- 核心代码入口
- 测试与验证入口
- 运行与排障入口

**Step 3: 更新维护规则和关联文档**

加入入口同步维护要求，并修正失效链接。

**Step 4: 自检**

Run: `rg -n "^### 领域入口$" docs/FUNCTION_TREE.md`

Expected: 输出 10 条，分别对应 10 个一级功能域。

### Task 4: 更新 Docs 首页与功能管理工作流

**Files:**
- Modify: `docs/INDEX.md`
- Modify: `docs/guides/FEATURE_MANAGEMENT_WORKFLOW.md`

**Step 1: 更新 Docs 首页**

将 `AI_QUICK_START`、`FUNCTION_TREE`、功能管理工作流标为推荐先读入口。

**Step 2: 更新功能管理工作流**

补充：

- 新文档体系说明
- 功能域入口同步规则
- 跨领域功能引用规则
- PR 描述字段要求
- AI Quick Start 同步要求

**Step 3: 自检**

Run: `sed -n '1,220p' docs/INDEX.md`

Expected: 首页包含“推荐先读”或等价入口。

### Task 5: 更新 PR 模板

**Files:**
- Modify: `.github/pull_request_template.md`

**Step 1: 新增功能域映射字段**

加入：

- 变更类型
- 所属功能域
- `FUNCTION_TREE` 节点
- 受影响入口
- 是否已更新 `FUNCTION_TREE`

**Step 2: 新增验证与回滚字段**

加入：

- 验证证据
- 风险与回滚

**Step 3: 自检**

Run: `sed -n '1,220p' .github/pull_request_template.md`

Expected: 模板包含主线治理字段和功能域映射字段两部分。

### Task 6: 验证改动范围与关键链接

**Files:**
- Modify: `docs/FUNCTION_TREE.md`
- Modify: `docs/INDEX.md`
- Modify: `docs/guides/FEATURE_MANAGEMENT_WORKFLOW.md`
- Create: `docs/guides/AI_QUICK_START.md`
- Create: `docs/plans/2026-03-12-function-tree-doc-routing-design.md`
- Create: `docs/plans/2026-03-12-function-tree-doc-routing-implementation-plan.md`
- Modify: `.github/pull_request_template.md`

**Step 1: 检查 diff**

Run: `git diff -- docs/FUNCTION_TREE.md docs/INDEX.md docs/guides/FEATURE_MANAGEMENT_WORKFLOW.md docs/guides/AI_QUICK_START.md docs/plans/2026-03-12-function-tree-doc-routing-design.md docs/plans/2026-03-12-function-tree-doc-routing-implementation-plan.md .github/pull_request_template.md`

Expected: 只包含本次文档导航和模板相关改动。

**Step 2: 检查主要链接目标是否存在**

Run: `test -e architecture/STANDARDS.md && test -e openspec/AGENTS.md && test -e docs/FUNCTION_TREE.md && test -e docs/guides/AI_QUICK_START.md && test -e docs/testing/E2E_TEST_GUIDE.md && test -e docs/operations/OPS_MANUAL.md && test -e .github/pull_request_template.md`

Expected: 退出码为 `0`。

**Step 3: 检查 markdown 语法风险**

Run: `git diff --check -- docs/FUNCTION_TREE.md docs/INDEX.md docs/guides/FEATURE_MANAGEMENT_WORKFLOW.md docs/guides/AI_QUICK_START.md docs/plans/2026-03-12-function-tree-doc-routing-design.md docs/plans/2026-03-12-function-tree-doc-routing-implementation-plan.md .github/pull_request_template.md`

Expected: 无 trailing whitespace、无冲突标记。
