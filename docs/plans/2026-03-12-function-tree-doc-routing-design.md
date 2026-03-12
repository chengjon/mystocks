# Function Tree Doc Routing Design

> **日期**: 2026-03-12
> **状态**: 已批准
> **范围**: `docs/FUNCTION_TREE.md`、`docs/guides/AI_QUICK_START.md`、`docs/INDEX.md`、`docs/guides/FEATURE_MANAGEMENT_WORKFLOW.md`、`.github/pull_request_template.md`

---

## 背景

MyStocks 已经具备较强的治理和交付门禁，但文档入口仍偏目录导向。对于 AI agent、代码评审者和新加入的开发者而言，当前更容易先按路径找文件，而不是先按业务能力和任务类型定位正确入口。

`docs/FUNCTION_TREE.md` 已经承担功能状态总览职责，`docs/INDEX.md` 和 `docs/guides/FEATURE_MANAGEMENT_WORKFLOW.md` 也已将其视为功能管理入口。因此本次设计不再新增一套平行文档体系，而是将 `FUNCTION_TREE` 升级为业务能力总线。

## 目标

- 让 `docs/FUNCTION_TREE.md` 从“功能清单”升级为“按功能域找规范、代码、测试、运行入口”的总线文档
- 新增 `docs/guides/AI_QUICK_START.md`，按任务类型将 AI 和开发者路由到对应功能域
- 让 `docs/INDEX.md` 明确推荐阅读顺序，减少目录式盲找
- 让 `docs/guides/FEATURE_MANAGEMENT_WORKFLOW.md` 明确要求：功能状态变化和入口变化必须同步维护 `FUNCTION_TREE`
- 将 PR 需要补充的功能域映射字段正式落地到 PR 模板

## 非目标

- 不自动生成 `FUNCTION_TREE`
- 不为每个三级功能点维护一套完整链接矩阵
- 不在本次引入新的 CI 文档校验器
- 不新增独立的 `docs/domains/` 平行体系

## 决策

### 1. `FUNCTION_TREE` 作为业务能力总线

每个一级功能域保留当前的：

- 模块路径
- API 前缀
- 完成度

在此基础上，新增统一的 `领域入口` 表，字段固定为：

- 规范入口
- API/契约入口
- 前端/交互入口
- 核心代码入口
- 测试与验证入口
- 运行与排障入口

### 2. `AI_QUICK_START` 只做任务路由，不复制功能树

`docs/guides/AI_QUICK_START.md` 不重复维护功能状态，只负责：

- 说明仓库定位
- 指出必须先读的治理门禁
- 按任务类型给出阅读顺序
- 将读者导向 `FUNCTION_TREE` 对应功能域
- 提示高优先级文档和低优先级文档

### 3. 维护规则合并到功能管理工作流

`docs/guides/FEATURE_MANAGEMENT_WORKFLOW.md` 增补以下规则：

- 新增功能时，除了状态条目，还要补功能域入口
- 功能状态变化或链接入口变化时，同步更新对应功能域入口表
- 跨领域功能由主领域维护完整入口，其他领域仅保留引用
- PR 描述必须标注所属功能域、`FUNCTION_TREE` 节点、受影响入口和验证证据

### 4. PR 模板对齐功能域映射

`.github/pull_request_template.md` 新增功能域映射字段：

- 变更类型
- 所属功能域
- `FUNCTION_TREE` 节点
- 受影响入口
- 是否已更新 `FUNCTION_TREE`
- 验证证据
- 风险与回滚

## 信息架构

### 入口层

- `docs/guides/AI_QUICK_START.md`
- `docs/INDEX.md`

### 总线层

- `docs/FUNCTION_TREE.md`

### 规则层

- `architecture/STANDARDS.md`
- `openspec/AGENTS.md`
- `.multi-cli-tasks/guides/*.md`
- `docs/guides/FEATURE_MANAGEMENT_WORKFLOW.md`

### 执行层

- `web/backend/app/api/**`
- `web/frontend/src/views/**`
- `src/**`
- `tests/**`
- `docs/testing/**`
- `docs/operations/**`
- `docs/deployment/**`

## 风险与折中

### 风险 1: 链接维护成本上升

缓解方式：

- 只在一级功能域维护统一入口表
- 每类入口控制在 2 到 3 个主要链接

### 风险 2: PR 模板与文档规则不一致

缓解方式：

- 在工作流文档和 PR 模板中同时固化字段要求
- 将 `FUNCTION_TREE` 作为评审引用入口，而不是再造第二套功能台账

### 风险 3: 功能树与实际代码脱节

缓解方式：

- 将 `FUNCTION_TREE` 视为功能管理真相源
- 在功能管理工作流中加入“状态变化与入口变化同步维护”的要求

## 验收标准

- 读者能从任务类型在 3 步内定位到目标功能域
- 每个一级功能域都有统一的 `领域入口` 表
- `docs/INDEX.md` 明确推荐先读顺序
- `docs/guides/FEATURE_MANAGEMENT_WORKFLOW.md` 明确同步维护规则和 PR 字段要求
- `.github/pull_request_template.md` 包含功能域映射字段
- 本次改动不引入新的领域平行文档体系
