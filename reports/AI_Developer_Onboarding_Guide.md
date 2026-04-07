# 🤖 AI 开发者项目启动指南：MyStocks ArtDeco 架构解析

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


本指南专为 AI Agent 或 LLM 开发者设计，用于快速理解、复现并扩展 MyStocks ArtDeco 3.1 架构。

---

## 1. 技术栈选型 (Tech Stack Matrix)
*核心关键字：`Vue3`, `FastAPI`, `PostgreSQL`, `TDengine`, `DesignTokens`*

| 维度 | 选型 | AI 推理逻辑 / 约束 |
| :--- | :--- | :--- |
| **前端框架** | `Vue 3.4+ (SFC)` | 利用 Composition API 实现逻辑高内聚，便于 AI 进行组件原子化拆分。 |
| **类型系统** | `TypeScript 5.x` | 强制类型契约，消除 AI 生成代码时的属性不一致模糊感。 |
| **后端引擎** | `FastAPI` | 基于 Pydantic 的 Schema 验证，便于 AI 理解并生成 API 文档。 |
| **样式系统** | `SCSS + Tokens` | 消除硬编码。AI 必须通过 [artdeco-tokens.scss](../web/frontend/src/styles/artdeco-tokens.scss) 访问设计变量。 |

---

## 2. 核心模块设计 (Core Module Blueprint)
*设计模式：领域驱动设计 (DDD) 与 布局-视图分离*

### A. 前端：布局与视图确权
- **Layout (骨架)**: [ArtDecoLayoutEnhanced.vue](../web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue)。承载侧边栏、Header 和面包屑。
- **View (内容)**: 业务组件存放于 `views/artdeco-pages/` 及其子目录（如 `market-tabs/`）。仅负责业务逻辑，禁止包含全局导航。
- **Entry (关键红线)**: [App.vue](../web/frontend/src/App.vue) 必须保持纯净，仅保留 `<router-view />`。

### B. 后端：单例与工厂模式
- **Factory**: [data_source_factory.py](../web/backend/app/services/data_source_factory/data_source_factory.py)。统一管理 Mock/Real 数据源切换。
- **Service**: 业务逻辑层。API Controller 仅负责参数分发，复杂逻辑必须下沉到 Service 层。

---

## 3. 数据流图 (Data Flow Logic)
*AI 逻辑追踪路径：从 UI 触发到数据回显*

1.  **触发**：UI 组件调用 `useArtDecoApi` 组合函数。
2.  **传输**：Axios 拦截器注入 `Request ID`。
3.  **路由**：FastAPI 路由识别接口，通过依赖注入获取 Service。
4.  **适配**：`DataSourceFactory` 根据 `.env` 配置决定调用真实 DB 或 Mock 数据。
5.  **响应**：通过 `ResponseFormatMiddleware` 包装为 `UnifiedResponse` 返回前端。

---

## 4. API 契约规范 (API Contract Standards)
*关键字：`UnifiedResponse`, `TraceID`, `TypeGeneration`*

- **标准响应格式**: 所有接口必须返回包含 `success`, `data`, `request_id` 的 JSON 体。
- **类型同步流**: 
    1. 修改后端 Pydantic 模型。
    2. 运行 [generate_frontend_types.py](../scripts/generate_frontend_types.py)。
    3. 前端 TS 类型自动更新。**禁止手动修改前端类型。**

---

## 5. 测试策略 (Automated Integrity Strategy)
*AI 闭环验证路径：`Red -> Green -> Refactor`*

- **环境编排**: 使用 [ecosystem.test.config.js](../ecosystem.test.config.js) 通过 PM2 拉起完整环境。
- **自动化断言**: [navigation-consistency.spec.ts](navigation-consistency.spec.ts)。
- **验证维度**: `URL Regex Match` + `Business Title (English/Chinese)` + `Root Element Class`。
- **执行入口**: [run_e2e_pm2.sh](run_e2e_pm2.sh) 一键闭环脚本。

---

## 6. AI 开发者高效上手路径 (Specific Implementation Path)

### 第一步：Context 对齐
- **必读文件**：`CLAUDE.md` (规范), `README.md` (业务), `ArtDeco_E2E_Test_Guide.md` (测试)。
- **样式边界**：扫描 `artdeco-tokens.scss` 建立视觉令牌认知。

### 第二步：架构健康检查
- **路由扫描**：确保 [router/index.ts](../web/frontend/src/router/index.ts) 中定义了 `alias` 以对齐增强版菜单路径。
- **单例初始化**：检查所有 Python 服务的 `get_*_service` 函数，确保全局变量已显式初始化为 `None`。

### 第三步：防御式开发准则
- **Anti-Hardcode**：禁止在 Vue 组件中使用 `color: #...`，必须使用 Token 变量。
- **Import Check**：导入新模块前，先 `grep` 确认其名称和路径，防止 `ImportError`。
- **Observability First**：优先实现 `health` 接口和 `SystemHealthTab`，确保系统“透明”。

---
**交付状态**：文档已就绪 | 适合 Agent 理解 | 路径清晰
