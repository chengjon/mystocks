# AI Quick Start

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


> **最后更新**: 2026-04-26
> **适用对象**: AI agent、代码评审者、新加入开发者

---

## 这是什么仓库

MyStocks 是持续演进中的工程仓库，不是纯知识库。

- 代码、治理文档、测试入口、运行手册都可能是事实源
- 不要只读 README 或只看代码目录
- 先判断任务类型，再按功能域下钻，效率最高

---

## 必读门禁

开始任何实质工作前，先判断是否命中以下入口：

1. [架构红线与审批门禁](../../../architecture/STANDARDS.md)
   适用：所有写操作、前后端修改、运行与验证
2. [OpenSpec 工作流](../../../openspec/AGENTS.md)
   适用：proposal、plan、spec、能力新增、架构变更、breaking change
3. [Docs 首页](../../INDEX.md)
   适用：需要快速知道从哪份文档开始读
4. [功能树](../../FUNCTION_TREE.md)
   适用：任何落到具体业务能力的任务；也是功能边界与开发方向总览，新增功能或边界变化后必须回写
5. `governance/mainline/task-cards/pr-<PR号>.yaml`
   适用：需要 machine-readable `function_tree` 声明、scope gate 或 reviewer 镜像对齐的任务

---

## 任务类型路由

| 任务类型 | 先读 | 再跳转 | 最后下钻 |
|---------|------|--------|----------|
| 方案 / 规划 / Proposal | [OpenSpec 工作流](../../../openspec/AGENTS.md) | [功能树](../../FUNCTION_TREE.md) 对应功能域 | 该领域的规范、接口和核心代码 |
| 新功能开发 | [架构红线与审批门禁](../../../architecture/STANDARDS.md) | [功能树](../../FUNCTION_TREE.md) 对应功能域 | API/契约、前端、核心代码、测试入口 |
| Bug 修复 | [功能树](../../FUNCTION_TREE.md) 对应功能域 | 该领域“测试与验证入口” | 代码入口和运行与排障入口 |
| Code Review | [功能管理工作流](../governance/FEATURE_MANAGEMENT_WORKFLOW.md) | [功能树](../../FUNCTION_TREE.md) 节点 | 受影响入口、验证证据和风险点 |
| 前端 / 路由 / 布局 | [架构红线与审批门禁](../../../architecture/STANDARDS.md) | [功能树](../../FUNCTION_TREE.md) 对应功能域 | 前端/交互入口和 E2E 入口 |
| 后端 / API / 契约 | [架构红线与审批门禁](../../../architecture/STANDARDS.md) | [功能树](../../FUNCTION_TREE.md) 对应功能域 | API/契约入口和后端测试入口 |
| 运维 / PM2 / 排障 | [运维文档总览](../../operations/README.md) | [功能树](../../FUNCTION_TREE.md) 对应功能域 | 运行与排障入口 |

---

## 最小读取路径

### 新功能开发

1. 读 [架构红线与审批门禁](../../../architecture/STANDARDS.md)
2. 如涉及规划或能力新增，再读 [OpenSpec 工作流](../../../openspec/AGENTS.md)
3. 进入 [功能树](../../FUNCTION_TREE.md) 的目标功能域
4. 只下钻该领域的“领域入口”表
5. 若本次新增了能力、改变了功能入口或调整了职责边界，提交前同步更新 `docs/FUNCTION_TREE.md`
6. 如本次是受治理的 PR / 任务，再检查 task card 中的 `function_tree` 稳定 ID 与 `affected_entrypoints`

### Bug 修复

1. 进入 [功能树](../../FUNCTION_TREE.md) 的目标功能域
2. 先看“测试与验证入口”
3. 再看“运行与排障入口”
4. 最后才扩展到相关核心代码

### Code Review

1. 读 [功能管理工作流](../governance/FEATURE_MANAGEMENT_WORKFLOW.md)
2. 找到 PR 对应的功能域和 `FUNCTION_TREE` 节点
3. 检查领域入口是否覆盖此次改动
4. 用验证证据判断是否存在回归风险

### 运维 / 排障

1. 读 [运维文档总览](../../operations/README.md)
2. 进入 [功能树](../../FUNCTION_TREE.md) 的目标功能域
3. 只看该领域“运行与排障入口”
4. 需要时再回看测试入口或 API 入口

---

## 怎么使用 FUNCTION_TREE

[功能树](../../FUNCTION_TREE.md) 不是只看状态的清单，而是业务能力总线。

每个一级功能域都包含统一的“领域入口”表：

- 规范入口
- API/契约入口
- 前端/交互入口
- 核心代码入口
- 测试与验证入口
- 运行与排障入口

原则：

- 先按功能域定位，不先按目录瞎找
- 先看领域入口，不先展开全仓搜索
- 跨领域任务由主领域维护完整入口，其他领域只看引用
- 新增功能、入口迁移、职责边界变化或状态变化，必须在同一批次回写 `FUNCTION_TREE`
- task card 的 `function_tree` 是机器真相源；`meta-governance` 只在 machine-readable catalog / task card 中声明，不进入业务功能树文档

---

## 文档优先级

### 高优先级

- `architecture/STANDARDS.md`
- `openspec/AGENTS.md`
- `docs/INDEX.md`
- `docs/FUNCTION_TREE.md`
- 活跃 guides
- 测试入口和运行入口

### 低优先级

- 阶段完成报告
- archive
- demo
- 临时分析文档
- 一次性收尾报告

---

## 常见误区

- 不要先做目录式全仓搜索，再反推功能归属
- 不要把历史报告当现行规范
- 不要把单个页面或单个 API 文件当成完整功能边界
- 不要在未确认功能域前就开始改代码
- 不要为 `optimize-data-source-v2` 编造新的 repo-local 编码或补文档任务；该 change 的仓库内研发已闭环，后续只走外部验收、灰度、观测、ROI/SLA、会议与归档
- 不要用 HTML5 / Web Workers / 菜单历史报告恢复移动端范围、6-domain 菜单口径、完整 Worker 编排或 PWA/offline/push/accessibility 已完成结论；当前事实以 active OpenSpec tasks、Desktop-only runtime guides 和代码验证为准

---

## 相关入口

- [Docs 首页](../../INDEX.md)
- [功能树](../../FUNCTION_TREE.md)
- [功能管理工作流](../governance/FEATURE_MANAGEMENT_WORKFLOW.md)
- [架构红线与审批门禁](../../../architecture/STANDARDS.md)
- [OpenSpec 工作流](../../../openspec/AGENTS.md)
