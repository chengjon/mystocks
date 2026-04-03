# MyStocks ArtDeco 工程红线与架构准则 (V3.1)

本文档定义了开发过程中必须严格遵守的架构约束和开发流程。所有代码提交必须符合这些规则。

---

## 零、统一治理与审批门禁 (Single Source of Truth)

### 1. 方案先行准则 (Proposal-First Rule)
*   **严禁自主实施**：任何涉及菜单结构、UI/UX 风格、核心架构的变更，必须先提交《技术方案/设计草案》。
*   **审批后执行**：只有在用户明确回复“批准”、“同意”或“执行”后，方可启动代码修改。
*   **违规回滚**：任何未经审批的自主变更均被视为无效交付，必须按需无条件回滚。

### 2. 共享规则归一化
*   **唯一来源**：以下共享规则以本文件为唯一事实来源：`方案先行准则`、`六步走战略`、`Docker 一等公民原则`。
*   **引用优先**：`CLAUDE.md`、`AGENTS.md`、`.gemini/GEMINI.md` 应以引用本文件为主，避免复制粘贴同一规则正文。
*   **更新顺序**：若规则调整，先更新本文件，再同步各入口文档的引用说明。

---

## 一、 推荐开发流程：六步走战略

### 1. 契约先行 (Contract First) —— 避免“接口分裂”
*   **原则**：严禁在未定义契约前编写业务逻辑。
*   **契约定位**：OpenAPI 是接口契约，不是事后补写的说明文档。前端、后端、测试、第三方集成必须以同一份契约为准。
*   **单源可信**：当前仓库以 `FastAPI 路由 + Pydantic Schema + 导出的 /openapi.json` 为 API 契约唯一事实来源；Markdown 文档、前端手写类型、临时调试脚本均不得充当并行真值。
*   **流程**：先定义 OpenAPI (Swagger) 规范 -> 自动生成/导出契约 -> 运行 `generate_frontend_types.py` 生成 TS 类型。
*   **同步要求**：任何接口字段、参数、认证、错误响应、示例或语义变更，必须与 OpenAPI 契约在同一提交中同步更新；禁止“代码已变，契约未变”。
*   **可追溯性**：契约变更必须与代码一起纳入 Git，确保可比较差异、可回滚、可审计。
*   **收益**：前端永远不会拼错字段名，后端修改字段时前端编译直接报错。

### 2. 单体骨架 (Monolithic Skeleton) —— 避免“循环依赖”
*   **原则**：严禁循环依赖。
*   **分层约束**：
    *   **Core**: 工具类、配置、日志（无依赖）。
    *   **Domain**: 纯 TypeScript/Python 实体定义（无业务逻辑）。
    *   **Infra**: 数据库适配器、API Client、Redis（只依赖 Core 和 Domain）。
    *   **Application**: 业务服务逻辑。
    *   **UI/API**: Vue 组件 / FastAPI 路由（最上层）。
*   **拦截**：禁止底层模块依赖上层模块。

### 3. Mock 驱动开发 (Mock Driven) —— 避免“前端等后端”
*   **原则**：实现前后端开发解耦。
*   **要求**：使用 MSW 或后端 Mock 模式。在后端未就绪前，前端 UI/UX 必须能够通过假数据独立完成视觉验收。

### 4. 垂直切片 (Vertical Slicing) —— 避免“连不上库”
*   **原则**：做一个 Feature，通一个 Feature。
*   **流程**：一次只实现一个完整 Feature 的垂直流（DB -> Service -> API -> UI）。
*   **日志标准化**：严禁使用 `print`，必须统一使用 `from app.core.logger import logger`。

### 5. 集成与可观测性 (Observability) —— 避免“隐形白屏”
*   **原则**：系统运行状态必须对开发者透明。
*   **要求**：
    *   必须实现 RequestId 全链路追踪（注入 Header 与 Logger）。
    *   必须提供 `/health/ready` 探针（校验 DB/Redis 连通性）。
    *   前端 `App.vue` 启动时必须校验后端就绪状态，严禁在故障时显示空内容。

### 6. 自动化防护网 (Safety Net) —— 避免“修好 A 坏了 B”
*   **原则**：拒绝手动回归，依赖代码防护。
*   **要求**：每次涉及路由或 Layout 的修改必须通过 [scripts/run_e2e_pm2.sh](../scripts/run_e2e_pm2.sh) 进行全量冒烟测试。

---

## 二、 技术工程红线 (Technical Red Lines)

### 1. 前端开发红线
*   **路由纯净度**：[App.vue](../web/frontend/src/App.vue) 严禁硬编码业务组件，必须通过 `<router-view />` 渲染。
*   **路径语义化**：当 `MenuConfig` 的路径与路由实现不一致时，必须在 [router/index.ts](../web/frontend/src/router/index.ts) 中使用 `alias`。
*   **禁止硬编码样式**：视觉属性必须引用 [artdeco-tokens.scss](../web/frontend/src/styles/artdeco-tokens.scss) 变量。
*   **TRACE_ID 显化**：所有业务 Tab 必须在 UI 预留 Request ID 展示位。

### 2. 后端开发红线
*   **单例防御**：所有 `global` 变量必须在模块顶层显式初始化为 `None`，杜绝 `NameError`。
*   **导入安全性**：重构后必须全局搜索并清理已废弃模块的引用，防止后端陷入重启死循环。
*   **响应标准化**：所有 API 必须返回 `UnifiedResponse` 包装结构。

### 3. 环境一致性
*   **PM2/Docker 优先**：`ecosystem.config.js` 及其配套环境是“一等公民”。严禁依赖碎片化的命令行启动。

---
**所有 Agent 在执行任何写操作前必须首先通过 `read_file` 加载此准则。**
